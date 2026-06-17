from app.models.analysis import NivelConfianca

_CONFIDENCE_ORDER = {
    NivelConfianca.BAIXA: 0,
    NivelConfianca.MEDIA: 1,
    NivelConfianca.ALTA: 2,
}


def calculate_ev(prob: float, odd: float) -> float:
    """EV = (prob_final × odd) − 1."""
    return prob * odd - 1


def kelly_fraction(prob: float, odd: float) -> float:
    """Fração de Kelly completa. b = odd líquida (odd-1), q = 1-prob."""
    b = odd - 1
    if b <= 0:
        return 0.0

    q = 1 - prob
    f = (b * prob - q) / b
    return max(f, 0.0)


def suggested_stake(
    prob: float,
    odd: float,
    max_kelly_fraction: float = 0.25,
    max_stake_fraction_of_bankroll: float = 0.03,
) -> float:
    """Stake sugerido como fração da banca: Kelly fracionado (máx. 25% do Kelly
    completo por padrão), com teto absoluto sobre a fração da banca."""
    full_kelly = kelly_fraction(prob, odd)
    fractional_kelly = full_kelly * max_kelly_fraction
    return min(fractional_kelly, max_stake_fraction_of_bankroll)


def meets_confidence_threshold(
    confianca: NivelConfianca, minimum: NivelConfianca = NivelConfianca.MEDIA
) -> bool:
    return _CONFIDENCE_ORDER[confianca] >= _CONFIDENCE_ORDER[minimum]


def should_recommend(
    ev: float, confianca: NivelConfianca, ev_threshold: float = 0.03
) -> bool:
    """Recomendação só é emitida se EV > limiar E confiança >= média."""
    return ev > ev_threshold and meets_confidence_threshold(confianca)
