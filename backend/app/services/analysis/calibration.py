def compute_brier_score(predictions: list[tuple[str, float, bool]]) -> float | None:
    """Brier score multi-classe: para cada grupo (ex.: um mercado de um jogo),
    soma o quadrado da diferença entre probabilidade estimada e resultado real
    (1.0/0.0) em cada seleção; o score final é a média dessa soma entre os
    grupos. Quanto menor, melhor calibrado o modelo. `predictions` é uma lista
    de tuplas (chave_do_grupo, prob_estimada, resultado_real)."""
    if not predictions:
        return None

    groups: dict[str, list[tuple[float, bool]]] = {}
    for group_key, prob_estimada, resultado_real in predictions:
        groups.setdefault(group_key, []).append((prob_estimada, resultado_real))

    group_scores = [
        sum((prob - float(actual)) ** 2 for prob, actual in items)
        for items in groups.values()
    ]

    return sum(group_scores) / len(group_scores)
