from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.league import League
from app.schemas.league import LeagueOut

router = APIRouter(
    prefix="/leagues", tags=["leagues"], dependencies=[Depends(get_current_user)]
)


@router.get("", response_model=list[LeagueOut])
async def list_leagues(db: AsyncSession = Depends(get_db)) -> list[League]:
    stmt = select(League).order_by(League.pais, League.nome)
    result = await db.execute(stmt)
    return list(result.scalars().all())
