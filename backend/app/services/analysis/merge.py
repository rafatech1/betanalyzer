from app.services.analysis.dixon_coles import MatchProbabilities

MARKET_GROUPS: dict[str, list[str]] = {
    "1x2": ["casa", "empate", "fora"],
    "over_under_2.5": ["mais_2.5", "menos_2.5"],
}


def match_probabilities_to_dict(probabilities: MatchProbabilities) -> dict[str, float]:
    return {
        "casa": probabilities.prob_casa,
        "empate": probabilities.prob_empate,
        "fora": probabilities.prob_fora,
        "mais_2.5": probabilities.prob_over_2_5,
        "menos_2.5": probabilities.prob_under_2_5,
    }


def merge_probabilities(
    model_probs: dict[str, float], adjustments: dict[str, float]
) -> dict[str, float]:
    """Aplica os ajustes sugeridos pela camada qualitativa por cima das
    probabilidades do modelo estatístico e renormaliza cada grupo de mercado
    (1X2, over/under) para que volte a somar 1."""
    merged = dict(model_probs)
    for selecao, value in adjustments.items():
        if selecao in merged:
            merged[selecao] = value

    for selections in MARKET_GROUPS.values():
        relevant = [s for s in selections if s in merged]
        total = sum(merged[s] for s in relevant)
        if total > 0:
            for s in relevant:
                merged[s] = merged[s] / total

    return merged
