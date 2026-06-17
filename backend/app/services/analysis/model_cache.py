from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.analysis.dixon_coles import MatchResult, TeamRatings, fit_dixon_coles
from app.services.cache import cache_get_json, cache_set_json
from app.services.fixtures_repo import get_finished_fixtures_for_league

TTL_RATINGS = 12 * 3600
MIN_MATCHES_TO_FIT = 20


def _ratings_to_json(ratings: TeamRatings) -> dict:
    return {
        "attack": {str(k): v for k, v in ratings.attack.items()},
        "defense": {str(k): v for k, v in ratings.defense.items()},
        "home_advantage": ratings.home_advantage,
        "rho": ratings.rho,
    }


def _ratings_from_json(data: dict) -> TeamRatings:
    return TeamRatings(
        attack={int(k): v for k, v in data["attack"].items()},
        defense={int(k): v for k, v in data["defense"].items()},
        home_advantage=data["home_advantage"],
        rho=data["rho"],
    )


async def get_team_ratings(db: AsyncSession, league_id: int) -> TeamRatings | None:
    """Retorna as ratings de ataque/defesa ajustadas para a liga, usando cache
    de 12h. Retorna None se não houver histórico suficiente para um ajuste
    confiável."""
    cache_key = f"dixon_coles:ratings:{league_id}"
    cached = await cache_get_json(cache_key)
    if cached is not None:
        return _ratings_from_json(cached)

    rows = await get_finished_fixtures_for_league(db, league_id)
    if len(rows) < MIN_MATCHES_TO_FIT:
        return None

    matches = [
        MatchResult(
            home_id=row["home_id"],
            away_id=row["away_id"],
            goals_home=row["goals_home"],
            goals_away=row["goals_away"],
            match_date=row["match_date"],
        )
        for row in rows
    ]

    ratings = fit_dixon_coles(matches, as_of=date.today())
    await cache_set_json(cache_key, _ratings_to_json(ratings), TTL_RATINGS)
    return ratings
