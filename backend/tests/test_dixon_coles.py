from datetime import date, timedelta

import pytest

from app.services.analysis.dixon_coles import MatchResult, fit_dixon_coles, predict_match

# Time 1 = forte, Time 2 = médio, Time 3 = fraco — repetido em 3 rodadas para
# dar sinal suficiente ao ajuste por máxima verossimilhança.
BASE_ROUND = [
    (1, 2, 3, 1),
    (2, 1, 0, 2),
    (1, 3, 4, 0),
    (3, 1, 0, 3),
    (2, 3, 2, 1),
    (3, 2, 1, 2),
]


def _synthetic_matches(rounds: int = 3) -> list[MatchResult]:
    start = date(2026, 1, 1)
    matches = []
    for round_index in range(rounds):
        round_date = start + timedelta(days=round_index * 7)
        for home_id, away_id, goals_home, goals_away in BASE_ROUND:
            matches.append(
                MatchResult(
                    home_id=home_id,
                    away_id=away_id,
                    goals_home=goals_home,
                    goals_away=goals_away,
                    match_date=round_date,
                )
            )
    return matches


def test_fit_recovers_relative_team_strength_ordering() -> None:
    ratings = fit_dixon_coles(_synthetic_matches())

    assert ratings.attack[1] > ratings.attack[2] > ratings.attack[3]
    # defesa: valor MAIOR significa defesa mais fraca (sofre mais gols)
    assert ratings.defense[1] < ratings.defense[2] < ratings.defense[3]


def test_predict_match_probabilities_sum_to_one() -> None:
    ratings = fit_dixon_coles(_synthetic_matches())
    probs = predict_match(ratings, home_id=1, away_id=3)

    assert probs.prob_casa + probs.prob_empate + probs.prob_fora == pytest.approx(1.0, abs=1e-6)
    assert probs.prob_over_2_5 + probs.prob_under_2_5 == pytest.approx(1.0, abs=1e-6)


def test_strong_team_favored_at_home_against_weak_team() -> None:
    ratings = fit_dixon_coles(_synthetic_matches())

    strong_at_home = predict_match(ratings, home_id=1, away_id=3)
    weak_at_home = predict_match(ratings, home_id=3, away_id=1)

    assert strong_at_home.prob_casa > strong_at_home.prob_fora
    assert weak_at_home.prob_fora > weak_at_home.prob_casa
    assert strong_at_home.prob_casa > weak_at_home.prob_fora  # casa + força combinadas


def test_raises_on_empty_matches() -> None:
    with pytest.raises(ValueError):
        fit_dixon_coles([])


def test_raises_on_single_team() -> None:
    matches = [
        MatchResult(home_id=1, away_id=1, goals_home=1, goals_away=1, match_date=date(2026, 1, 1))
    ]
    with pytest.raises(ValueError):
        fit_dixon_coles(matches)
