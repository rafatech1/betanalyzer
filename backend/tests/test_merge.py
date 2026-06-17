import pytest

from app.services.analysis.dixon_coles import MatchProbabilities
from app.services.analysis.merge import match_probabilities_to_dict, merge_probabilities


def test_match_probabilities_to_dict_maps_all_fields() -> None:
    probs = MatchProbabilities(
        prob_casa=0.45, prob_empate=0.27, prob_fora=0.28, prob_over_2_5=0.55, prob_under_2_5=0.45
    )

    result = match_probabilities_to_dict(probs)

    assert result == {
        "casa": 0.45,
        "empate": 0.27,
        "fora": 0.28,
        "mais_2.5": 0.55,
        "menos_2.5": 0.45,
    }


def test_no_adjustments_returns_model_probabilities_unchanged() -> None:
    model_probs = {"casa": 0.45, "empate": 0.27, "fora": 0.28, "mais_2.5": 0.55, "menos_2.5": 0.45}

    result = merge_probabilities(model_probs, {})

    assert result == pytest.approx(model_probs)


def test_adjustment_to_one_selection_renormalizes_its_market_group() -> None:
    model_probs = {"casa": 0.45, "empate": 0.27, "fora": 0.28, "mais_2.5": 0.55, "menos_2.5": 0.45}

    result = merge_probabilities(model_probs, {"casa": 0.60})

    assert result["casa"] + result["empate"] + result["fora"] == pytest.approx(1.0)
    assert result["casa"] > 0.45  # ajuste para cima foi respeitado proporcionalmente
    # mercado over/under não foi tocado
    assert result["mais_2.5"] == pytest.approx(0.55)
    assert result["menos_2.5"] == pytest.approx(0.45)


def test_unknown_selection_in_adjustments_is_ignored() -> None:
    model_probs = {"casa": 0.5, "empate": 0.3, "fora": 0.2}

    result = merge_probabilities(model_probs, {"selecao_inexistente": 0.9})

    assert result == pytest.approx(model_probs)
