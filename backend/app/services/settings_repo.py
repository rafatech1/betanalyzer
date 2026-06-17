from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_settings import AppSettings


async def get_settings_row(db: AsyncSession, user_id: int) -> AppSettings:
    stmt = select(AppSettings).where(AppSettings.user_id == user_id)
    result = await db.execute(stmt)
    settings = result.scalar_one_or_none()

    if settings is None:
        settings = AppSettings(
            user_id=user_id,
            banca_inicial=1000.0,
            kelly_fraction=0.25,
            ev_threshold=0.03,
            favorite_league_ids=[],
        )
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    return settings


async def update_settings_row(
    db: AsyncSession,
    user_id: int,
    banca_inicial: float | None,
    kelly_fraction: float | None,
    ev_threshold: float | None,
    favorite_league_ids: list[int] | None,
) -> AppSettings:
    settings = await get_settings_row(db, user_id)

    if banca_inicial is not None:
        settings.banca_inicial = banca_inicial
    if kelly_fraction is not None:
        settings.kelly_fraction = kelly_fraction
    if ev_threshold is not None:
        settings.ev_threshold = ev_threshold
    if favorite_league_ids is not None:
        settings.favorite_league_ids = favorite_league_ids

    await db.commit()
    await db.refresh(settings)
    return settings
