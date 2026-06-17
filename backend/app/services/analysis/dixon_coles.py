import math
from dataclasses import dataclass
from datetime import date

import numpy as np
from scipy.optimize import minimize
from scipy.stats import poisson

DEFAULT_DECAY_RATE = 0.0018  # por dia — meia-vida de ~385 dias para o peso de recência
MAX_GOALS = 9


@dataclass(frozen=True)
class MatchResult:
    home_id: int
    away_id: int
    goals_home: int
    goals_away: int
    match_date: date


@dataclass(frozen=True)
class TeamRatings:
    attack: dict[int, float]
    defense: dict[int, float]
    home_advantage: float
    rho: float


@dataclass(frozen=True)
class MatchProbabilities:
    prob_casa: float
    prob_empate: float
    prob_fora: float
    prob_over_2_5: float
    prob_under_2_5: float


def _dixon_coles_tau(x: int, y: int, lam: float, mu: float, rho: float) -> float:
    """Correção de Dixon-Coles para a subestimação de empates/baixo placar pelo
    Poisson bivariado independente."""
    if x == 0 and y == 0:
        return 1 - lam * mu * rho
    if x == 0 and y == 1:
        return 1 + lam * rho
    if x == 1 and y == 0:
        return 1 + mu * rho
    if x == 1 and y == 1:
        return 1 - rho
    return 1.0


def fit_dixon_coles(
    matches: list[MatchResult],
    as_of: date | None = None,
    decay_rate: float = DEFAULT_DECAY_RATE,
) -> TeamRatings:
    """Ajusta força de ataque/defesa por time, vantagem de casa e o parâmetro de
    correção rho via máxima verossimilhança ponderada por recência (jogos mais
    antigos pesam exponencialmente menos)."""
    if not matches:
        raise ValueError("matches não pode ser vazio")

    as_of = as_of or max(match.match_date for match in matches)
    team_ids = sorted({m.home_id for m in matches} | {m.away_id for m in matches})
    if len(team_ids) < 2:
        raise ValueError("são necessários ao menos 2 times distintos")

    index = {team_id: i for i, team_id in enumerate(team_ids)}
    n = len(team_ids)
    n_attack_params = n - 1  # ataque do time 0 é fixado como referência (log=0)

    weights = [
        math.exp(-decay_rate * max((as_of - m.match_date).days, 0)) for m in matches
    ]

    def unpack(params: np.ndarray) -> tuple[np.ndarray, np.ndarray, float, float]:
        log_attack = np.concatenate(([0.0], params[:n_attack_params]))
        log_defense = params[n_attack_params : n_attack_params + n]
        log_home_advantage = params[-2]
        rho = params[-1]
        return np.exp(log_attack), np.exp(log_defense), math.exp(log_home_advantage), rho

    def negative_log_likelihood(params: np.ndarray) -> float:
        attack, defense, home_advantage, rho = unpack(params)
        total = 0.0
        for match, weight in zip(matches, weights):
            i, j = index[match.home_id], index[match.away_id]
            lam = attack[i] * defense[j] * home_advantage
            mu = attack[j] * defense[i]

            tau = max(_dixon_coles_tau(match.goals_home, match.goals_away, lam, mu, rho), 1e-10)

            log_pmf_home = (
                match.goals_home * math.log(lam) - lam - math.lgamma(match.goals_home + 1)
            )
            log_pmf_away = (
                match.goals_away * math.log(mu) - mu - math.lgamma(match.goals_away + 1)
            )

            total -= weight * (log_pmf_home + log_pmf_away + math.log(tau))

        return total

    initial_params = np.zeros(n_attack_params + n + 2)
    bounds = (
        [(-3.0, 3.0)] * n_attack_params
        + [(-3.0, 3.0)] * n
        + [(-1.0, 1.0)]  # vantagem de casa em log-escala (~0.37x a ~2.7x)
        + [(-0.3, 0.3)]  # rho
    )

    result = minimize(
        negative_log_likelihood,
        initial_params,
        method="L-BFGS-B",
        bounds=bounds,
    )

    attack, defense, home_advantage, rho = unpack(result.x)

    return TeamRatings(
        attack={team_id: float(attack[index[team_id]]) for team_id in team_ids},
        defense={team_id: float(defense[index[team_id]]) for team_id in team_ids},
        home_advantage=home_advantage,
        rho=rho,
    )


def predict_match(
    ratings: TeamRatings, home_id: int, away_id: int, max_goals: int = MAX_GOALS
) -> MatchProbabilities:
    if home_id not in ratings.attack or away_id not in ratings.attack:
        raise ValueError("time não encontrado nas ratings ajustadas")

    lam = ratings.attack[home_id] * ratings.defense[away_id] * ratings.home_advantage
    mu = ratings.attack[away_id] * ratings.defense[home_id]

    goals_range = np.arange(max_goals + 1)
    home_pmf = poisson.pmf(goals_range, lam)
    away_pmf = poisson.pmf(goals_range, mu)
    matrix = np.outer(home_pmf, away_pmf)

    for x in range(max_goals + 1):
        for y in range(max_goals + 1):
            tau = max(_dixon_coles_tau(x, y, lam, mu, ratings.rho), 0.0)
            matrix[x, y] *= tau

    matrix /= matrix.sum()

    prob_casa = float(np.tril(matrix, -1).sum())
    prob_empate = float(np.trace(matrix))
    prob_fora = float(np.triu(matrix, 1).sum())

    totals = np.add.outer(goals_range, goals_range)
    prob_over = float(matrix[totals >= 3].sum())
    prob_under = float(matrix[totals <= 2].sum())

    return MatchProbabilities(
        prob_casa=prob_casa,
        prob_empate=prob_empate,
        prob_fora=prob_fora,
        prob_over_2_5=prob_over,
        prob_under_2_5=prob_under,
    )
