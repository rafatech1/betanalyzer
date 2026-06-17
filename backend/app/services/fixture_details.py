from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.fixture import Fixture
from app.schemas.fixture_details import FixtureDetailsOut
from app.services.analysis.qualitative_data import (
    summarize_h2h,
    summarize_injuries,
    summarize_recent_form,
)
from app.services.external.api_football import APIFootballClient
from app.services.fixtures_repo import get_recent_finished_fixtures_for_team

logger = get_logger(__name__)


async def build_fixture_details(
    db: AsyncSession, fixture: Fixture, api_client: APIFootballClient
) -> FixtureDetailsOut:
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

    return FixtureDetailsOut(
        forma_casa=summarize_recent_form(home_recent),
        forma_fora=summarize_recent_form(away_recent),
        h2h_resumo=h2h_resumo,
        lesoes_casa=lesoes_casa,
        lesoes_fora=lesoes_fora,
    )
