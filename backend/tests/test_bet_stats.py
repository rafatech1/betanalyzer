from datetime import datetime, timezone

from app.services.bet_stats import ResolvedBet, compute_bet_stats


def _dt(day: int) -> datetime:
    return datetime(2026, 1, day, tzinfo=timezone.utc)


def test_compute_bet_stats_no_bets_returns_neutral_values() -> None:
    result = compute_bet_stats(1000.0, [], [], total_apostas=0)

    assert result.total_apostas == 0
    assert result.apostas_resolvidas == 0
    assert result.taxa_acerto is None
    assert result.roi == 0.0
    assert result.yield_ is None
    assert result.evolucao == []


def test_compute_bet_stats_win_and_loss_compute_roi_and_yield() -> None:
    resolved = [
        ResolvedBet(created_at=_dt(1), stake=100.0, lucro=50.0, resultado="ganha"),
        ResolvedBet(created_at=_dt(2), stake=100.0, lucro=-100.0, resultado="perdida"),
    ]

    result = compute_bet_stats(1000.0, resolved, [], total_apostas=2)

    assert result.apostas_resolvidas == 2
    assert result.lucro_acumulado == -50.0
    assert result.total_investido == 200.0
    assert result.taxa_acerto == 0.5
    assert result.roi == -50.0 / 1000.0
    assert result.yield_ == -50.0 / 200.0


def test_compute_bet_stats_evolucao_is_chronological_running_balance() -> None:
    resolved = [
        ResolvedBet(created_at=_dt(2), stake=10.0, lucro=10.0, resultado="ganha"),
        ResolvedBet(created_at=_dt(1), stake=10.0, lucro=-10.0, resultado="perdida"),
    ]

    result = compute_bet_stats(100.0, resolved, [], total_apostas=2)

    saldos = [p.saldo_acumulado for p in result.evolucao]
    assert saldos == [100.0, 90.0, 100.0]


def test_compute_bet_stats_ignores_cashout_and_anulada_in_hit_rate() -> None:
    resolved = [
        ResolvedBet(created_at=_dt(1), stake=10.0, lucro=0.0, resultado="anulada"),
        ResolvedBet(created_at=_dt(2), stake=10.0, lucro=5.0, resultado="cashout"),
        ResolvedBet(created_at=_dt(3), stake=10.0, lucro=10.0, resultado="ganha"),
    ]

    result = compute_bet_stats(100.0, resolved, [], total_apostas=3)

    assert result.taxa_acerto == 1.0


def test_compute_bet_stats_includes_manual_bankroll_movements() -> None:
    manual_movements = [(_dt(1), 200.0)]
    resolved = [ResolvedBet(created_at=_dt(2), stake=10.0, lucro=10.0, resultado="ganha")]

    result = compute_bet_stats(100.0, resolved, manual_movements, total_apostas=1)

    saldos = [p.saldo_acumulado for p in result.evolucao]
    assert saldos == [100.0, 300.0, 310.0]
