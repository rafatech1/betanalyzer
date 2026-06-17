from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.fixture import Fixture
from app.models.odds import Odds
from app.schemas.analysis_context import AnalysisContext, OddsContext
from app.services.analysis.qualitative_data import (
    summarize_h2h,
    summarize_injuries,
    summarize_recent_form,
)
from app.services.external.api_football import APIFootballClient
from app.services.fixtures_repo import get_recent_finished_fixtures_for_team

logger = get_logger(__name__)


async def build_analysis_context(
    db: AsyncSession,
    fixture: Fixture,
    prob_modelo: dict[str, float],
    odds_rows: list[Odds],
    api_client: APIFootballClient,
    modelo_estatistico_disponivel: bool = True,
    contexto_adicional: str | None = None,
) -> AnalysisContext:
    home_recent = await get_recent_finished_fixtures_for_team(db, fixture.time_casa_id)
    away_recent = await get_recent_finished_fixtures_for_team(db, fixture.time_fora_id)

    h2h_resumo: str | None = None
    try:
        h2h_matches = await api_client.get_h2h(fixture.time_casa_id, fixture.time_fora_id)
        h2h_resumo = summarize_h2h(
            h2h_matches, fixture.time_casa_id, fixture.time_casa.nome, fixture.time_fora.nome
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("h2h_fetch_failed", fixture_id=fixture.id, error=str(exc))

    lesoes_casa: list[str] = []
    lesoes_fora: list[str] = []
    try:
        injuries = await api_client.get_injuries(fixture_id=fixture.id)
        lesoes_casa = summarize_injuries(
            [i for i in injuries if i.get("team", {}).get("id") == fixture.time_casa_id]
        )
        lesoes_fora = summarize_injuries(
            [i for i in injuries if i.get("team", {}).get("id") == fixture.time_fora_id]
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("injuries_fetch_failed", fixture_id=fixture.id, error=str(exc))

    odds_context = [
        OddsContext(
            mercado=row.mercado,
            selecao=row.selecao,
            odd=row.odd,
            prob_implicita=row.prob_implicita,
            casa_de_aposta=row.casa_de_aposta,
        )
        for row in odds_rows
    ]

    return AnalysisContext(
        fixture_id=fixture.id,
        time_casa=fixture.time_casa.nome,
        time_fora=fixture.time_fora.nome,
        data_hora=fixture.data_hora,
        liga=fixture.league.nome,
        prob_modelo=prob_modelo,
        odds=odds_context,
        forma_casa=summarize_recent_form(home_recent),
        forma_fora=summarize_recent_form(away_recent),
        h2h_resumo=h2h_resumo,
        lesoes_casa=lesoes_casa,
        lesoes_fora=lesoes_fora,
        contexto_adicional=contexto_adicional,
        modelo_estatistico_disponivel=modelo_estatistico_disponivel,
    )
