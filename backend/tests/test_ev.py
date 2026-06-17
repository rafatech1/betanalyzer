import pytest

from app.models.analysis import NivelConfianca
from app.services.analysis.ev import (
    calculate_ev,
    kelly_fraction,
    should_recommend,
    suggested_stake,
)


def test_calculate_ev_positive() -> None:
    # prob 55%, odd 2.20 -> EV = 0.55*2.20 - 1 = 0.21
    assert calculate_ev(0.55, 2.20) == pytest.approx(0.21)


def test_calculate_ev_negative() -> None:
    assert calculate_ev(0.40, 2.00) == pytest.approx(-0.20)


def test_kelly_fraction_zero_when_no_edge() -> None:
    # odds justas (sem margem): prob == prob implícita -> Kelly = 0
    assert kelly_fraction(0.5, 2.0) == pytest.approx(0.0)


def test_kelly_fraction_positive_with_edge() -> None:
    # prob 55%, odd 2.20: b=1.2, q=0.45 -> f = (1.2*0.55 - 0.45)/1.2 = 0.175
    assert kelly_fraction(0.55, 2.20) == pytest.approx(0.175, abs=1e-9)


def test_kelly_fraction_never_negative() -> None:
    assert kelly_fraction(0.30, 2.00) == 0.0


def test_suggested_stake_caps_at_25_percent_of_kelly() -> None:
    # full kelly = 0.175 -> 25% = 0.04375, abaixo do teto de banca (0.03)? não, 0.04375 > 0.03
    stake = suggested_stake(0.55, 2.20, max_kelly_fraction=0.25, max_stake_fraction_of_bankroll=0.03)
    assert stake == pytest.approx(0.03)


def test_suggested_stake_uses_fractional_kelly_when_below_cap() -> None:
    stake = suggested_stake(0.55, 2.20, max_kelly_fraction=0.1, max_stake_fraction_of_bankroll=0.03)
    assert stake == pytest.approx(0.0175, abs=1e-9)


def test_suggested_stake_zero_when_no_edge() -> None:
    assert suggested_stake(0.5, 2.0) == pytest.approx(0.0)


def test_should_recommend_true_above_threshold_with_high_confidence() -> None:
    assert should_recommend(ev=0.05, confianca=NivelConfianca.ALTA, ev_threshold=0.03) is True


def test_should_recommend_false_below_threshold() -> None:
    assert should_recommend(ev=0.02, confianca=NivelConfianca.ALTA, ev_threshold=0.03) is False


def test_should_recommend_false_with_low_confidence_even_with_high_ev() -> None:
    assert should_recommend(ev=0.20, confianca=NivelConfianca.BAIXA, ev_threshold=0.03) is False


def test_should_recommend_true_with_medium_confidence() -> None:
    assert should_recommend(ev=0.05, confianca=NivelConfianca.MEDIA, ev_threshold=0.03) is True
