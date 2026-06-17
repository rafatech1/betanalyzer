from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.app_settings import AppSettings
from app.models.user import User
from app.schemas.app_settings import AppSettingsOut, AppSettingsUpdate
from app.services.settings_repo import get_settings_row, update_settings_row

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=AppSettingsOut)
async def get_app_settings(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
) -> AppSettings:
    return await get_settings_row(db, current_user.id)


@router.put("", response_model=AppSettingsOut)
async def put_app_settings(
    payload: AppSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AppSettings:
    return await update_settings_row(
        db,
        current_user.id,
        banca_inicial=payload.banca_inicial,
        kelly_fraction=payload.kelly_fraction,
        ev_threshold=payload.ev_threshold,
        favorite_league_ids=payload.favorite_league_ids,
    )
