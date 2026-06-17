from datetime import date, datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.session import AsyncSessionLocal
from app.models.fixture import Fixture, FixtureStatus
from app.services.analysis.exceptions import FixtureNotFoundError, InsufficientModelDataError
from app.services.analysis.lock import AnalysisInProgressError
from app.services.analysis.pipeline import run_analysis_pipeline
from app.services.cache import QuotaExceededError
from app.services.external.api_football import APIFootballClient
from app.services.external.odds_api import OddsAPIClient, extract_best_odds
from app.services.fixtures_repo import get_upcoming_fixtures_with_teams, upsert_fixtures_batch
from app.services.model_prediction_repo import backfill_model_prediction_results
from app.services.odds_matching import find_matching_fixture
from app.services.odds_repo import save_odds_selections

logger = get_logger(__name__)

# Sem ligas monitoradas configuradas, busca globalmente apenas os próximos dias
# (1 requisição por dia consultado) para não comprometer a cota diária.
GLOBAL_FETCH_DAYS_AHEAD = 2

scheduler = AsyncIOScheduler()


async def update_fixtures_job() -> None:
    settings = get_settings()
    client = APIFootballClient()
    today = date.today()

    async with AsyncSessionLocal() as db:
        try:
            if settings.monitored_league_ids:
                for league_id in settings.monitored_league_ids:
                    fixtures = await client.get_fixtures(
                        today, today + timedelta(days=7), league_id=league_id
                    )
                    fixture_ids = await upsert_fixtures_batch(db, fixtures)
                    logger.info(
                        "fixtures_updated", league_id=league_id, count=len(fixture_ids)
                    )
            else:
                fixtures = await client.get_fixtures(
                    today, today + timedelta(days=GLOBAL_FETCH_DAYS_AHEAD)
                )
                fixture_ids = await upsert_fixtures_batch(db, fixtures)
                logger.info("fixtures_updated", league_id=None, count=len(fixture_ids))
        except QuotaExceededError as exc:
            logger.warning("fixtures_job_skipped_quota", error=str(exc))

        updated = await backfill_model_prediction_results(db)
        if updated:
            logger.info("model_predictions_backfilled", count=updated)


async def update_odds_job() -> None:
    settings = get_settings()

    if not settings.odds_api_sport_keys:
        logger.debug("odds_job_skipped_no_sport_keys")
        return

    odds_client = OddsAPIClient()

    async with AsyncSessionLocal() as db:
        upcoming_fixtures = await get_upcoming_fixtures_with_teams(
            db, settings.odds_update_window_hours
        )
        if not upcoming_fixtures:
            logger.debug("odds_job_no_upcoming_fixtures")
            return

        saved_count = 0
        try:
            for sport_key in settings.odds_api_sport_keys:
                events = await odds_client.get_events_odds(sport_key)
                for event in events:
                    fixture_id = find_matching_fixture(event, upcoming_fixtures)
                    if fixture_id is None:
                        continue

                    selections = extract_best_odds(
                        event, settings.odds_api_preferred_bookmaker
                    )
                    if not selections:
                        continue

                    await save_odds_selections(db, fixture_id, selections)
                    saved_count += len(selections)
        except QuotaExceededError as exc:
            logger.warning("odds_job_skipped_quota", error=str(exc))
            return

        logger.info("odds_updated", selections_saved=saved_count)


async def pre_analysis_job() -> None:
    """Pré-analisa os jogos das principais ligas que começam nas próximas
    `pre_analysis_window_hours` horas, para que a análise já esteja em cache
    quando o usuário acessar o jogo (arquitetura de análise compartilhada)."""
    settings = get_settings()
    if not settings.pre_analysis_league_ids:
        logger.debug("pre_analysis_job_skipped_no_leagues")
        return

    now = datetime.now(timezone.utc)
    window_end = now + timedelta(hours=settings.pre_analysis_window_hours)

    async with AsyncSessionLocal() as db:
        stmt = select(Fixture.id).where(
            Fixture.liga_id.in_(settings.pre_analysis_league_ids),
            Fixture.status == FixtureStatus.AGENDADA,
            Fixture.data_hora >= now,
            Fixture.data_hora <= window_end,
        )
        result = await db.execute(stmt)
        fixture_ids = [row[0] for row in result.all()]

    analyzed = 0
    for fixture_id in fixture_ids:
        async with AsyncSessionLocal() as db:
            try:
                await run_analysis_pipeline(db, fixture_id)
                analyzed += 1
            except (FixtureNotFoundError, InsufficientModelDataError, AnalysisInProgressError) as exc:
                logger.info("pre_analysis_skipped", fixture_id=fixture_id, reason=str(exc))
            except Exception as exc:  # noqa: BLE001
                logger.error("pre_analysis_failed", fixture_id=fixture_id, error=str(exc))

    logger.info("pre_analysis_completed", analyzed=analyzed, total=len(fixture_ids))


def start_scheduler() -> None:
    scheduler.add_job(
        update_fixtures_job,
        "interval",
        hours=6,
        id="update_fixtures",
        replace_existing=True,
    )
    scheduler.add_job(
        update_odds_job,
        "interval",
        minutes=30,
        id="update_odds",
        replace_existing=True,
    )
    scheduler.add_job(
        pre_analysis_job,
        "interval",
        hours=6,
        id="pre_analysis",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("scheduler_started")


def shutdown_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("scheduler_stopped")
