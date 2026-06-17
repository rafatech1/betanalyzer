from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.bankroll import BankrollCreate, BankrollSummaryOut
from app.services.bankroll_repo import create_movement, get_current_balance, list_movements

router = APIRouter(prefix="/bankroll", tags=["bankroll"])


@router.get("", response_model=BankrollSummaryOut)
async def get_bankroll(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
) -> BankrollSummaryOut:
    saldo = await get_current_balance(db, current_user.id)
    movimentos = await list_movements(db, current_user.id)
    return BankrollSummaryOut(saldo_atual=saldo, movimentos=list(reversed(movimentos)))


@router.post("", response_model=BankrollSummaryOut, status_code=201)
async def post_bankroll_movement(
    payload: BankrollCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BankrollSummaryOut:
    await create_movement(db, current_user.id, payload.tipo, payload.valor, payload.descricao)
    saldo = await get_current_balance(db, current_user.id)
    movimentos = await list_movements(db, current_user.id)
    return BankrollSummaryOut(saldo_atual=saldo, movimentos=list(reversed(movimentos)))
