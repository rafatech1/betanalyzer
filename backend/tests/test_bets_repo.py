from app.models.bet import ResultadoAposta
from app.services.bets_repo import _auto_lucro


def test_auto_lucro_ganha_returns_profit_from_odd() -> None:
    assert _auto_lucro(ResultadoAposta.GANHA, odd=2.5, stake=10.0) == 15.0


def test_auto_lucro_perdida_returns_negative_stake() -> None:
    assert _auto_lucro(ResultadoAposta.PERDIDA, odd=2.5, stake=10.0) == -10.0


def test_auto_lucro_anulada_returns_zero() -> None:
    assert _auto_lucro(ResultadoAposta.ANULADA, odd=2.5, stake=10.0) == 0.0
