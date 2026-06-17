from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bankroll import Bankroll, TipoMovimento
from app.services.settings_repo import get_settings_row

_SIGN: dict[TipoMovimento, int] = {
    TipoMovimento.DEPOSITO: 1,
    TipoMovimento.RETIRADA: -1,
    TipoMovimento.APOSTA: -1,
    TipoMovimento.GANHO: 1,
    TipoMovimento.AJUSTE: 1,
}


async def get_current_balance(db: AsyncSession, user_id: int) -> float:
    stmt = (
        select(Bankroll.saldo_resultante)
        .where(Bankroll.user_id == user_id)
        .order_by(Bankroll.created_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    saldo = result.scalar_one_or_none()
    if saldo is not None:
        return saldo

    settings = await get_settings_row(db, user_id)
    return settings.banca_inicial


async def list_movements(db: AsyncSession, user_id: int) -> list[Bankroll]:
    stmt = (
        select(Bankroll).where(Bankroll.user_id == user_id).order_by(Bankroll.created_at)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_movement(
    db: AsyncSession, user_id: int, tipo: TipoMovimento, valor: float, descricao: str | None
) -> Bankroll:
    saldo_anterior = await get_current_balance(db, user_id)
    saldo_resultante = saldo_anterior + _SIGN[tipo] * abs(valor)

    movimento = Bankroll(
        user_id=user_id,
        tipo=tipo,
        valor=valor,
        saldo_resultante=saldo_resultante,
        descricao=descricao,
    )
    db.add(movimento)
    await db.commit()
    await db.refresh(movimento)
    return movimento
