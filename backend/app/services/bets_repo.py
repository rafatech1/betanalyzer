from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.bankroll import TipoMovimento
from app.models.bet import Bet, ResultadoAposta
from app.models.fixture import Fixture
from app.schemas.bet import BetCreate, BetStatsOut
from app.services.bankroll_repo import list_movements
from app.services.bet_stats import ResolvedBet, compute_bet_stats
from app.services.settings_repo import get_settings_row

_MANUAL_MOVEMENT_TYPES = {TipoMovimento.DEPOSITO, TipoMovimento.RETIRADA, TipoMovimento.AJUSTE}
_MOVEMENT_SIGN = {TipoMovimento.DEPOSITO: 1, TipoMovimento.RETIRADA: -1, TipoMovimento.AJUSTE: 1}


def _auto_lucro(resultado: ResultadoAposta, odd: float, stake: float) -> float:
    if resultado == ResultadoAposta.GANHA:
        return stake * (odd - 1)
    if resultado == ResultadoAposta.PERDIDA:
        return -stake
    if resultado == ResultadoAposta.ANULADA:
        return 0.0
    return 0.0


async def create_bet(db: AsyncSession, user_id: int, payload: BetCreate) -> Bet:
    bet = Bet(
        user_id=user_id,
        fixture_id=payload.fixture_id,
        analysis_id=payload.analysis_id,
        mercado=payload.mercado,
        selecao=payload.selecao,
        odd=payload.odd,
        stake=payload.stake,
    )
    db.add(bet)
    await db.commit()
    await db.refresh(bet)
    return bet


async def list_bets(db: AsyncSession, user_id: int) -> list[Bet]:
    stmt = (
        select(Bet)
        .where(Bet.user_id == user_id)
        .options(
            selectinload(Bet.fixture).selectinload(Fixture.time_casa),
            selectinload(Bet.fixture).selectinload(Fixture.time_fora),
        )
        .order_by(Bet.created_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_bet_result(
    db: AsyncSession, user_id: int, bet_id: int, resultado: ResultadoAposta, lucro: float | None
) -> Bet | None:
    bet = await db.get(Bet, bet_id)
    if bet is None or bet.user_id != user_id:
        return None

    bet.resultado = resultado
    if lucro is not None:
        bet.lucro = lucro
    elif resultado == ResultadoAposta.CASHOUT:
        bet.lucro = bet.lucro or 0.0
    else:
        bet.lucro = _auto_lucro(resultado, bet.odd, bet.stake)

    await db.commit()
    await db.refresh(bet)
    return bet


async def compute_stats(db: AsyncSession, user_id: int) -> BetStatsOut:
    settings = await get_settings_row(db, user_id)
    movements = await list_movements(db, user_id)
    bets = await list_bets(db, user_id)

    manual_movements = [
        (m.created_at, _MOVEMENT_SIGN[m.tipo] * abs(m.valor))
        for m in movements
        if m.tipo in _MANUAL_MOVEMENT_TYPES
    ]
    resolved = [
        ResolvedBet(
            created_at=b.created_at,
            stake=b.stake,
            lucro=b.lucro or 0.0,
            resultado=b.resultado.value,
        )
        for b in bets
        if b.resultado != ResultadoAposta.PENDENTE
    ]

    return compute_bet_stats(settings.banca_inicial, resolved, manual_movements, len(bets))
