import pytest

from app.services.model_prediction_repo import _actual_outcome


def test_1x2_home_win() -> None:
    assert _actual_outcome("1x2", "casa", 2, 0) is True
    assert _actual_outcome("1x2", "empate", 2, 0) is False
    assert _actual_outcome("1x2", "fora", 2, 0) is False


def test_1x2_draw() -> None:
    assert _actual_outcome("1x2", "empate", 1, 1) is True
    assert _actual_outcome("1x2", "casa", 1, 1) is False


def test_1x2_away_win() -> None:
    assert _actual_outcome("1x2", "fora", 0, 3) is True
    assert _actual_outcome("1x2", "casa", 0, 3) is False


def test_over_under_threshold() -> None:
    assert _actual_outcome("over_under_2.5", "mais_2.5", 2, 1) is True
    assert _actual_outcome("over_under_2.5", "menos_2.5", 2, 1) is False
    assert _actual_outcome("over_under_2.5", "menos_2.5", 1, 1) is True
    assert _actual_outcome("over_under_2.5", "mais_2.5", 1, 1) is False


def test_raises_on_unknown_market() -> None:
    with pytest.raises(ValueError):
        _actual_outcome("ambas_marcam", "sim", 1, 1)
