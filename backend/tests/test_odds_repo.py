import pytest

from app.services.external.odds_api import OddsSelection
from app.services.odds_repo import _attach_implied_probabilities


def test_implied_probabilities_grouped_per_market_sum_to_one() -> None:
    selections = [
        OddsSelection(mercado="1x2", selecao="casa", odd=2.00, casa_de_aposta="Betano"),
        OddsSelection(mercado="1x2", selecao="empate", odd=3.40, casa_de_aposta="Betano"),
        OddsSelection(mercado="1x2", selecao="fora", odd=4.00, casa_de_aposta="Betano"),
        OddsSelection(mercado="ambas_marcam", selecao="sim", odd=1.80, casa_de_aposta="Betano"),
        OddsSelection(mercado="ambas_marcam", selecao="nao", odd=2.10, casa_de_aposta="Betano"),
    ]

    paired = _attach_implied_probabilities(selections)

    by_market: dict[str, float] = {}
    for selection, prob in paired:
        by_market[selection.mercado] = by_market.get(selection.mercado, 0.0) + prob

    assert by_market["1x2"] == pytest.approx(1.0, abs=1e-9)
    assert by_market["ambas_marcam"] == pytest.approx(1.0, abs=1e-9)


def test_each_selection_keeps_its_own_odd_paired_with_probability() -> None:
    selections = [
        OddsSelection(mercado="1x2", selecao="casa", odd=2.00, casa_de_aposta="Betano"),
        OddsSelection(mercado="1x2", selecao="fora", odd=2.00, casa_de_aposta="Betano"),
    ]

    paired = _attach_implied_probabilities(selections)
    result = {selection.selecao: prob for selection, prob in paired}

    assert result == pytest.approx({"casa": 0.5, "fora": 0.5})
