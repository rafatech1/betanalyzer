from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, selectinload

from app.models.fixture import Fixture, FixtureStatus
from app.models.league import League
from app.models.team import Team

_STATUS_MAP: dict[str, FixtureStatus] = {
    "NS": FixtureStatus.AGENDADA,
    "TBD": FixtureStatus.AGENDADA,
    "1H": FixtureStatus.EM_ANDAMENTO,
    "HT": FixtureStatus.EM_ANDAMENTO,
    "2H": FixtureStatus.EM_ANDAMENTO,
    "ET": FixtureStatus.EM_ANDAMENTO,
    "BT": FixtureStatus.EM_ANDAMENTO,
    "P": FixtureStatus.EM_ANDAMENTO,
    "LIVE": FixtureStatus.EM_ANDAMENTO,
    "FT": FixtureStatus.FINALIZADA,
    "AET": FixtureStatus.FINALIZADA,
    "PEN": FixtureStatus.FINALIZADA,
    "PST": FixtureStatus.POSTERGADA,
    "SUSP": FixtureStatus.POSTERGADA,
    "INT": FixtureStatus.POSTERGADA,
    "CANC": FixtureStatus.CANCELADA,
    "ABD": FixtureStatus.CANCELADA,
    "AWD": FixtureStatus.CANCELADA,
    "WO": FixtureStatus.CANCELADA,
}


def map_fixture_status(short_status: str) -> FixtureStatus:
    return _STATUS_MAP.get(short_status, FixtureStatus.AGENDADA)


async def _upsert_league(db: AsyncSession, league_payload: dict[str, Any]) -> None:
    stmt = pg_insert(League).values(
        id=league_payload["id"],
        nome=league_payload["name"],
        pais=league_payload.get("country", ""),
        temporada=league_payload.get("season"),
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=[League.id],
        set_={
            "nome": stmt.excluded.nome,
            "pais": stmt.excluded.pais,
            "temporada": stmt.excluded.temporada,
        },
    )
    await db.execute(stmt)


async def _upsert_team(db: AsyncSession, team_payload: dict[str, Any], liga_id: int) -> None:
    stmt = pg_insert(Team).values(
        id=team_payload["id"],
        nome=team_payload["name"],
        liga_id=liga_id,
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=[Team.id],
        set_={"nome": stmt.excluded.nome, "liga_id": stmt.excluded.liga_id},
    )
    await db.execute(stmt)


async def _upsert_fixture(
    db: AsyncSession,
    fixture_payload: dict[str, Any],
    league_id: int,
    teams_payload: dict[str, Any],
    goals_payload: dict[str, Any],
) -> int:
    fixture_id = fixture_payload["id"]
    status = map_fixture_status(fixture_payload["status"]["short"])

    stmt = pg_insert(Fixture).values(
        id=fixture_id,
        liga_id=league_id,
        time_casa_id=teams_payload["home"]["id"],
        time_fora_id=teams_payload["away"]["id"],
        data_hora=datetime.fromisoformat(fixture_payload["date"]),
        status=status,
        placar_casa=goals_payload.get("home"),
        placar_fora=goals_payload.get("away"),
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=[Fixture.id],
        set_={
            "status": stmt.excluded.status,
            "placar_casa": stmt.excluded.placar_casa,
            "placar_fora": stmt.excluded.placar_fora,
            "data_hora": stmt.excluded.data_hora,
        },
    )
    await db.execute(stmt)
    return fixture_id


async def upsert_fixtures_batch(db: AsyncSession, fixtures_payload: list[dict[str, Any]]) -> list[int]:
    """Persiste leagues, teams e fixtures a partir do payload bruto da API-Football.
    Idempotente: cada fixture é identificado pelo próprio id da API-Football."""
    fixture_ids: list[int] = []

    for item in fixtures_payload:
        league_payload = item["league"]
        teams_payload = item["teams"]
        fixture_payload = item["fixture"]
        goals_payload = item.get("goals", {}) or {}

        await _upsert_league(db, league_payload)
        await _upsert_team(db, teams_payload["home"], league_payload["id"])
        await _upsert_team(db, teams_payload["away"], league_payload["id"])
        fixture_id = await _upsert_fixture(
            db, fixture_payload, league_payload["id"], teams_payload, goals_payload
        )
        fixture_ids.append(fixture_id)

    await db.commit()
    return fixture_ids


async def get_upcoming_fixtures_with_teams(
    db: AsyncSession, window_hours: int
) -> list[dict[str, Any]]:
    """Fixtures agendados nas próximas `window_hours` horas, com nomes dos times,
    usados para casar eventos da The Odds API (que não compartilha IDs com a
    API-Football) por nome de time + horário de início."""
    home_team = aliased(Team)
    away_team = aliased(Team)

    now = datetime.now(timezone.utc)
    window_end = now + timedelta(hours=window_hours)

    stmt = (
        select(
            Fixture.id,
            Fixture.data_hora,
            home_team.nome.label("home_name"),
            away_team.nome.label("away_name"),
        )
        .join(home_team, Fixture.time_casa_id == home_team.id)
        .join(away_team, Fixture.time_fora_id == away_team.id)
        .where(
            Fixture.status == FixtureStatus.AGENDADA,
            Fixture.data_hora >= now,
            Fixture.data_hora <= window_end,
        )
    )

    result = await db.execute(stmt)
    return [
        {
            "fixture_id": row.id,
            "data_hora": row.data_hora,
            "home_name": row.home_name,
            "away_name": row.away_name,
        }
        for row in result
    ]


async def get_fixture_with_relations(db: AsyncSession, fixture_id: int) -> Fixture | None:
    stmt = (
        select(Fixture)
        .options(
            selectinload(Fixture.time_casa),
            selectinload(Fixture.time_fora),
            selectinload(Fixture.league),
        )
        .where(Fixture.id == fixture_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_finished_fixtures_for_league(
    db: AsyncSession, league_id: int, lookback_days: int = 730
) -> list[dict[str, Any]]:
    """Histórico de jogos finalizados de uma liga, usado para ajustar o modelo
    Dixon-Coles (força de ataque/defesa ponderada por recência)."""
    since = datetime.now(timezone.utc) - timedelta(days=lookback_days)

    stmt = (
        select(Fixture)
        .where(
            Fixture.liga_id == league_id,
            Fixture.status == FixtureStatus.FINALIZADA,
            Fixture.data_hora >= since,
            Fixture.placar_casa.is_not(None),
            Fixture.placar_fora.is_not(None),
        )
        .order_by(Fixture.data_hora)
    )

    result = await db.execute(stmt)
    return [
        {
            "home_id": fixture.time_casa_id,
            "away_id": fixture.time_fora_id,
            "goals_home": fixture.placar_casa,
            "goals_away": fixture.placar_fora,
            "match_date": fixture.data_hora.date(),
        }
        for fixture in result.scalars().all()
    ]


async def get_recent_finished_fixtures_for_team(
    db: AsyncSession, team_id: int, limit: int = 5
) -> list[dict[str, Any]]:
    """Últimos jogos finalizados de um time (casa ou fora), usados para resumir
    a forma recente na análise qualitativa."""
    stmt = (
        select(Fixture)
        .where(
            (Fixture.time_casa_id == team_id) | (Fixture.time_fora_id == team_id),
            Fixture.status == FixtureStatus.FINALIZADA,
            Fixture.placar_casa.is_not(None),
            Fixture.placar_fora.is_not(None),
        )
        .order_by(Fixture.data_hora.desc())
        .limit(limit)
    )

    result = await db.execute(stmt)
    fixtures = result.scalars().all()

    summaries = []
    for fixture in fixtures:
        is_home = fixture.time_casa_id == team_id
        gols_marcados = fixture.placar_casa if is_home else fixture.placar_fora
        gols_sofridos = fixture.placar_fora if is_home else fixture.placar_casa

        if gols_marcados > gols_sofridos:
            resultado = "V"
        elif gols_marcados < gols_sofridos:
            resultado = "D"
        else:
            resultado = "E"

        summaries.append(
            {
                "resultado": resultado,
                "gols_marcados": gols_marcados,
                "gols_sofridos": gols_sofridos,
                "data_hora": fixture.data_hora,
            }
        )

    return summaries
