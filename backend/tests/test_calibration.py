import pytest

from app.services.analysis.calibration import compute_brier_score


def test_perfect_predictions_score_zero() -> None:
    predictions = [
        ("jogo1:1x2", 1.0, True),
        ("jogo1:1x2", 0.0, False),
        ("jogo1:1x2", 0.0, False),
    ]

    assert compute_brier_score(predictions) == pytest.approx(0.0)


def test_worst_possible_predictions_score_two_per_group() -> None:
    predictions = [
        ("jogo1:1x2", 0.0, True),
        ("jogo1:1x2", 1.0, False),
    ]

    assert compute_brier_score(predictions) == pytest.approx(2.0)


def test_uniform_uncertainty_for_three_way_market() -> None:
    predictions = [
        ("jogo1:1x2", 1 / 3, True),
        ("jogo1:1x2", 1 / 3, False),
        ("jogo1:1x2", 1 / 3, False),
    ]

    # (2/3)^2 + (1/3)^2 + (1/3)^2 = 4/9 + 1/9 + 1/9 = 6/9
    assert compute_brier_score(predictions) == pytest.approx(6 / 9)


def test_averages_across_multiple_groups() -> None:
    predictions = [
        ("jogo1:1x2", 1.0, True),
        ("jogo1:1x2", 0.0, False),
        ("jogo2:1x2", 0.0, True),
        ("jogo2:1x2", 1.0, False),
    ]

    assert compute_brier_score(predictions) == pytest.approx(1.0)


def test_returns_none_for_empty_predictions() -> None:
    assert compute_brier_score([]) is None
