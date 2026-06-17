def remove_overround(odds_list: list[float]) -> list[float]:
    """Converte odds decimais em probabilidades implícitas sem a margem da casa.

    Usa normalização proporcional: cada probabilidade implícita bruta (1/odd) é
    dividida pela soma de todas as probabilidades brutas do mercado, de forma
    que o resultado some exatamente 1.0.
    """
    if not odds_list:
        raise ValueError("odds_list não pode ser vazia")

    for odd in odds_list:
        if odd <= 1.0:
            raise ValueError(f"odd inválida: {odd} (deve ser > 1.0)")

    raw_probabilities = [1.0 / odd for odd in odds_list]
    overround = sum(raw_probabilities)

    return [p / overround for p in raw_probabilities]
