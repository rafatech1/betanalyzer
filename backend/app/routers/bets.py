from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.bet import Bet
from app.models.user import User
from app.schemas.bet import BetCreate, BetFixtureSummary, BetOut, BetStatsOut, BetUpdate
from app.services.bets_repo import compute_stats, create_bet, list_bets, update_bet_result

router = APIRouter(prefix="/bets", tags=["bets"])


def _to_bet_out(bet: Bet) -> BetOut:
    fixture_summary = None
    if bet.fixture is not None:
        fixture_summary = BetFixtureSummary(
            id=bet.fixture.id,
            time_casa=bet.fixture.time_casa.nome,
            time_fora=bet.fixture.time_fora.nome,
            data_hora=bet.fixture.data_hora,
        )

    return BetOut(
        id=bet.id,
        fixture_id=bet.fixture_id,
        analysis_id=bet.analysis_id,
        mercado=bet.mercado,
        selecao=bet.selecao,
        odd=bet.odd,
        stake=bet.stake,
        resultado=bet.resultado,
        lucro=bet.lucro,
        created_at=bet.created_at,
        fixture=fixture_summary,
    )


@router.get("", response_model=list[BetOut])
async def get_bets(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[BetOut]:
    bets = await list_bets(db, current_user.id)
    return [_to_bet_out(bet) for bet in bets]


@router.get("/stats", response_model=BetStatsOut)
async def get_bet_stats(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
) -> BetStatsOut:
    return await compute_stats(db, current_user.id)


@router.post("", response_model=BetOut, status_code=201)
async def post_bet(
    payload: BetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BetOut:
    bet = await create_bet(db, current_user.id, payload)
    bets = await list_bets(db, current_user.id)
    refreshed = next((b for b in bets if b.id == bet.id), bet)
    return _to_bet_out(refreshed)


@router.patch("/{bet_id}", response_model=BetOut)
async def patch_bet(
    bet_id: int,
    payload: BetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BetOut:
    bet = await update_bet_result(db, current_user.id, bet_id, payload.resultado, payload.lucro)
    if bet is None:
        raise HTTPException(status_code=404, detail="Aposta não encontrada")

    bets = await list_bets(db, current_user.id)
    refreshed = next((b for b in bets if b.id == bet.id), bet)
    return _to_bet_out(refreshed)
