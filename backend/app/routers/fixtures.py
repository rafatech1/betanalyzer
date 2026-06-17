from datetime import datetime, time, timedelta, timezone
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.fixture import Fixture
from app.models.odds import Odds
from app.models.team import Team
from app.schemas.analysis import AnalyzeRequest, AnalyzeResponse
from app.schemas.fixture import FixtureOut, LeagueSummary, TeamOut
from app.schemas.fixture_details import FixtureDetailsOut
from app.schemas.odds import OddsOut
from app.services.analysis.exceptions import FixtureNotFoundError, InsufficientModelDataError
from app.services.analysis.lock import AnalysisInProgressError
from app.services.analysis.pipeline import run_analysis_pipeline
from app.services.external.api_football import APIFootballClient
from app.services.fixture_details import build_fixture_details
from app.services.fixtures_repo import get_fixture_with_relations

router = APIRouter(
    prefix="/fixtures", tags=["fixtures"], dependencies=[Depends(get_current_user)]
)


class Period(str, Enum):
    today = "today"
    week = "week"
    month = "month"


_PERIOD_DAYS_AHEAD = {Period.today: 0, Period.week: 6, Period.month: 29}


def _resolve_date_range(period: Period, now: datetime) -> tuple[datetime, datetime]:
    """Calcula o range [início, fim] usado para filtrar fixtures por período.

    Para "hoje", o início do range é o instante atual (não a meia-noite) —
    jogos que já começaram ou terminaram não devem aparecer na listagem do
    dia. Para semana/mês, o início continua sendo a meia-noite de hoje, já
    que esses períodos mais amplos ainda devem incluir jogos em
    andamento/finalizados de hoje (o frontend decide como exibi-los)."""
    today = now.date()
    end_date = today + timedelta(days=_PERIOD_DAYS_AHEAD[period])

    range_start = now if period == Period.today else datetime.combine(today, time.min, tzinfo=timezone.utc)
    range_end = datetime.combine(end_date, time.max, tzinfo=timezone.utc)
    return range_start, range_end


async def _attach_odds_preview(
    db: AsyncSession, fixtures: list[Fixture]
) -> dict[int, dict[str, float]]:
    fixture_ids = [f.id for f in fixtures]
    if not fixture_ids:
        return {}

    stmt = (
        select(Odds)
        .where(Odds.fixture_id.in_(fixture_ids), Odds.mercado == "1x2")
        .order_by(Odds.timestamp.desc())
    )
    result = await db.execute(stmt)

    preview: dict[int, dict[str, float]] = {}
    for row in result.scalars().all():
        fixture_odds = preview.setdefault(row.fixture_id, {})
        fixture_odds.setdefault(row.selecao, row.odd)

    return preview


def _to_fixture_out(fixture: Fixture, odds_preview: dict[str, float] | None) -> FixtureOut:
    return FixtureOut(
        id=fixture.id,
        liga_id=fixture.liga_id,
        liga=LeagueSummary(id=fixture.league.id, nome=fixture.league.nome, pais=fixture.league.pais),
        time_casa=TeamOut(id=fixture.time_casa.id, nome=fixture.time_casa.nome),
        time_fora=TeamOut(id=fixture.time_fora.id, nome=fixture.time_fora.nome),
        data_hora=fixture.data_hora,
        status=fixture.status,
        placar_casa=fixture.placar_casa,
        placar_fora=fixture.placar_fora,
        odds_1x2=odds_preview,
    )


@router.get("", response_model=list[FixtureOut])
async def list_fixtures(
    period: Period = Period.today,
    league: int | None = None,
    pais: str | None = None,
    hora_inicio: str | None = None,
    hora_fim: str | None = None,
    busca: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[FixtureOut]:
    range_start, range_end = _resolve_date_range(period, datetime.now(timezone.utc))

    stmt = (
        select(Fixture)
        .join(Fixture.league)
        .options(
            selectinload(Fixture.time_casa),
            selectinload(Fixture.time_fora),
            selectinload(Fixture.league),
        )
        .where(Fixture.data_hora >= range_start, Fixture.data_hora <= range_end)
        .order_by(Fixture.data_hora)
    )
    if league is not None:
        stmt = stmt.where(Fixture.liga_id == league)
    if pais is not None:
        stmt = stmt.where(Fixture.league.has(pais=pais))
    if busca:
        stmt = stmt.join(Team, or_(Fixture.time_casa_id == Team.id, Fixture.time_fora_id == Team.id)).where(
            Team.nome.ilike(f"%{busca}%")
        )

    result = await db.execute(stmt)
    fixtures = list(result.scalars().unique().all())

    if hora_inicio or hora_fim:
        start_t = time.fromisoformat(hora_inicio) if hora_inicio else time.min
        end_t = time.fromisoformat(hora_fim) if hora_fim else time.max
        fixtures = [f for f in fixtures if start_t <= f.data_hora.time() <= end_t]

    odds_preview = await _attach_odds_preview(db, fixtures)
    return [_to_fixture_out(f, odds_preview.get(f.id)) for f in fixtures]


@router.get("/{fixture_id}", response_model=FixtureOut)
async def get_fixture(fixture_id: int, db: AsyncSession = Depends(get_db)) -> FixtureOut:
    fixture = await get_fixture_with_relations(db, fixture_id)
    if fixture is None:
        raise HTTPException(status_code=404, detail="Fixture não encontrado")

    odds_preview = await _attach_odds_preview(db, [fixture])
    return _to_fixture_out(fixture, odds_preview.get(fixture.id))


@router.get("/{fixture_id}/details", response_model=FixtureDetailsOut)
async def get_fixture_details(
    fixture_id: int, db: AsyncSession = Depends(get_db)
) -> FixtureDetailsOut:
    fixture = await get_fixture_with_relations(db, fixture_id)
    if fixture is None:
        raise HTTPException(status_code=404, detail="Fixture não encontrado")

    api_client = APIFootballClient()
    return await build_fixture_details(db, fixture, api_client)


@router.post("/{fixture_id}/analyze", response_model=AnalyzeResponse)
async def analyze_fixture(
    fixture_id: int,
    payload: AnalyzeRequest | None = None,
    db: AsyncSession = Depends(get_db),
) -> AnalyzeResponse:
    contexto_adicional = payload.contexto_adicional if payload else None

    try:
        analyses = await run_analysis_pipeline(db, fixture_id, contexto_adicional)
    except FixtureNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InsufficientModelDataError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except AnalysisInProgressError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return AnalyzeResponse(analises=analyses)


@router.get("/{fixture_id}/odds", response_model=list[OddsOut])
async def get_fixture_odds(
    fixture_id: int,
    mercado: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[Odds]:
    fixture = await db.get(Fixture, fixture_id)
    if fixture is None:
        raise HTTPException(status_code=404, detail="Fixture não encontrado")

    stmt = (
        select(Odds)
        .where(Odds.fixture_id == fixture_id)
        .order_by(Odds.timestamp.desc())
    )
    if mercado is not None:
        stmt = stmt.where(Odds.mercado == mercado)

    result = await db.execute(stmt)
    return list(result.scalars().all())
