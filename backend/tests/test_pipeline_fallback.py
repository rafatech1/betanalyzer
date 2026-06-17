import pytest

from app.services.analysis.pipeline import _build_prob_modelo_from_odds


class _FakeOddsRow:
    def __init__(self, mercado: str, selecao: str, odd: float) -> None:
        self.mercado = mercado
        self.selecao = selecao
        self.odd = odd


def test_build_prob_modelo_from_odds_groups_by_market() -> None:
    rows = [
        _FakeOddsRow("1x2", "casa", 2.00),
        _FakeOddsRow("1x2", "empate", 3.40),
        _FakeOddsRow("1x2", "fora", 4.00),
        _FakeOddsRow("over_under_2.5", "mais_2.5", 1.90),
        _FakeOddsRow("over_under_2.5", "menos_2.5", 1.95),
    ]

    prob_modelo = _build_prob_modelo_from_odds(rows)

    assert prob_modelo.keys() == {"casa", "empate", "fora", "mais_2.5", "menos_2.5"}
    assert prob_modelo["casa"] + prob_modelo["empate"] + prob_modelo["fora"] == pytest.approx(1.0)
    assert prob_modelo["mais_2.5"] + prob_modelo["menos_2.5"] == pytest.approx(1.0)
    assert prob_modelo["casa"] > prob_modelo["empate"] > prob_modelo["fora"]


def test_build_prob_modelo_from_odds_empty_returns_empty_dict() -> None:
    assert _build_prob_modelo_from_odds([]) == {}
