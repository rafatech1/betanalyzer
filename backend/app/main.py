from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.db.redis import redis_client
from app.db.session import AsyncSessionLocal, engine
from app.routers import admin, analyses, auth, bankroll, bets, fixtures, leagues
from app.routers import settings as settings_router
from app.services.auth_repo import seed_admin_user
from app.services.scheduler import shutdown_scheduler, start_scheduler

settings = get_settings()
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup", environment=settings.environment, cors_origins=settings.cors_origins)
    async with AsyncSessionLocal() as session:
        await seed_admin_user(session)
    start_scheduler()
    yield
    shutdown_scheduler()
    await engine.dispose()
    await redis_client.aclose()
    logger.info("shutdown")


app = FastAPI(title=settings.app_name, lifespan=lifespan)

# allow_credentials=True exige origens explícitas em allow_origins — nunca
# "*" — senão o browser rejeita a resposta. allow_methods/allow_headers="*"
# cobre o preflight OPTIONS (inclusive o método OPTIONS em si e os headers
# Content-Type/Authorization usados pelo frontend).
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(analyses.router)
app.include_router(fixtures.router)
app.include_router(leagues.router)
app.include_router(bets.router)
app.include_router(bankroll.router)
app.include_router(settings_router.router)
app.include_router(admin.router)


@app.get("/health")
async def health() -> dict[str, str]:
    db_status = "ok"
    redis_status = "ok"

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001
        logger.error("health_db_failed", error=str(exc))
        db_status = "error"

    try:
        await redis_client.ping()
    except Exception as exc:  # noqa: BLE001
        logger.error("health_redis_failed", error=str(exc))
        redis_status = "error"

    overall = "ok" if db_status == "ok" and redis_status == "ok" else "degraded"

    return {"status": overall, "database": db_status, "redis": redis_status}
