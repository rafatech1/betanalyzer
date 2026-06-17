import pytest

from app.services.probability import remove_overround


def test_three_way_market_sums_to_one() -> None:
    # 1X2 com overround típico (~5-6%)
    probs = remove_overround([2.00, 3.40, 4.00])

    assert sum(probs) == pytest.approx(1.0, abs=1e-9)


def test_two_way_market_sums_to_one() -> None:
    # Over/Under 2.5
    probs = remove_overround([1.90, 1.95])

    assert sum(probs) == pytest.approx(1.0, abs=1e-9)


def test_proportional_normalization_preserves_relative_order() -> None:
    probs = remove_overround([2.00, 3.40, 4.00])

    # Odd menor (favorito) deve resultar em probabilidade maior
    assert probs[0] > probs[1] > probs[2]


def test_fair_odds_without_margin_are_unchanged_proportionally() -> None:
    # Odds "justas" (sem margem): 1/2 + 1/2 = 1, overround = 1, sem ajuste
    probs = remove_overround([2.00, 2.00])

    assert probs == pytest.approx([0.5, 0.5])


def test_known_overround_value_is_removed_correctly() -> None:
    # Odds implícitas brutas: 1/1.90 + 1/1.90 ≈ 1.0526 (overround de ~5.26%)
    probs = remove_overround([1.90, 1.90])

    assert probs == pytest.approx([0.5, 0.5])


def test_raises_on_empty_list() -> None:
    with pytest.raises(ValueError):
        remove_overround([])


def test_raises_on_odd_equal_to_one() -> None:
    with pytest.raises(ValueError):
        remove_overround([1.0, 2.0])


def test_raises_on_negative_odd() -> None:
    with pytest.raises(ValueError):
        remove_overround([-1.5, 2.0])


def test_raises_on_zero_odd() -> None:
    with pytest.raises(ValueError):
        remove_overround([0.0, 2.0])
