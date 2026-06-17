from dataclasses import dataclass
from datetime import datetime

from app.schemas.bet import BankrollPoint, BetStatsOut


@dataclass(frozen=True)
class ResolvedBet:
    created_at: datetime
    stake: float
    lucro: float
    resultado: str


def compute_bet_stats(
    banca_inicial: float,
    resolved_bets: list[ResolvedBet],
    manual_movements: list[tuple[datetime, float]],
    total_apostas: int,
) -> BetStatsOut:
    """Lógica pura de cálculo de ROI/yield/taxa de acerto/evolução de banca,
    separada do acesso a dados para permitir testes sem banco."""
    events: list[tuple[datetime, float]] = list(manual_movements)
    events.extend((bet.created_at, bet.lucro) for bet in resolved_bets)
    events.sort(key=lambda item: item[0])

    evolucao: list[BankrollPoint] = []
    saldo = banca_inicial
    if events:
        evolucao.append(BankrollPoint(data=events[0][0], saldo_acumulado=saldo))
    for data, delta in events:
        saldo += delta
        evolucao.append(BankrollPoint(data=data, saldo_acumulado=saldo))

    lucro_acumulado = sum(bet.lucro for bet in resolved_bets)
    total_investido = sum(bet.stake for bet in resolved_bets)

    ganhas = sum(1 for bet in resolved_bets if bet.resultado == "ganha")
    perdidas = sum(1 for bet in resolved_bets if bet.resultado == "perdida")
    decididas = ganhas + perdidas

    return BetStatsOut(
        total_apostas=total_apostas,
        apostas_resolvidas=len(resolved_bets),
        taxa_acerto=(ganhas / decididas) if decididas > 0 else None,
        total_investido=total_investido,
        lucro_acumulado=lucro_acumulado,
        roi=(lucro_acumulado / banca_inicial) if banca_inicial > 0 else None,
        yield_=(lucro_acumulado / total_investido) if total_investido > 0 else None,
        evolucao=evolucao,
    )
