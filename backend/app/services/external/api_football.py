from datetime import date, timedelta
from typing import Any

import httpx

from app.core.config import get_settings
from app.core.logging import get_logger
from app.services.cache import check_and_increment_daily_quota, get_or_fetch_json

logger = get_logger(__name__)

QUOTA_KEY = "api_football"

# TTLs em segundos — calibrados para a janela de atualização da Fase 2
# (fixtures a cada 6h, odds/lesões mudam com mais frequência perto do jogo).
TTL_FIXTURES = 6 * 3600
TTL_TEAM_STATISTICS = 12 * 3600
TTL_H2H = 24 * 3600
TTL_INJURIES = 6 * 3600

MAX_DATE_RANGE_DAYS = 7


def current_season(today: date | None = None) -> int:
    """Temporada europeia: jogos de jan-jun pertencem à temporada iniciada no ano anterior."""
    today = today or date.today()
    return today.year - 1 if today.month < 7 else today.year


def _date_chunks(date_from: date, date_to: date, max_days: int = MAX_DATE_RANGE_DAYS) -> list[tuple[date, date]]:
    chunks: list[tuple[date, date]] = []
    cursor = date_from
    while cursor <= date_to:
        chunk_end = min(cursor + timedelta(days=max_days - 1), date_to)
        chunks.append((cursor, chunk_end))
        cursor = chunk_end + timedelta(days=1)
    return chunks


class APIFootballClient:
    def __init__(self) -> None:
        settings = get_settings()
        self._base_url = settings.api_football_base_url
        self._api_key = settings.api_football_key
        self._daily_limit = settings.api_football_daily_limit
        self._season_override = settings.football_season

    async def _get(self, endpoint: str, params: dict[str, Any], ttl: int) -> list[dict[str, Any]]:
        cache_key = "api_football:" + endpoint + ":" + ":".join(
            f"{k}={v}" for k, v in sorted(params.items())
        )

        async def fetch() -> list[dict[str, Any]]:
            await check_and_increment_daily_quota(QUOTA_KEY, self._daily_limit)

            async with httpx.AsyncClient(base_url=self._base_url, timeout=15.0) as client:
                response = await client.get(
                    endpoint,
                    params=params,
                    headers={"x-apisports-key": self._api_key},
                )
                response.raise_for_status()
                payload = response.json()

            errors = payload.get("errors")
            if errors:
                logger.warning("api_football_response_errors", endpoint=endpoint, errors=errors)

            return payload.get("response", [])

        return await get_or_fetch_json(cache_key, ttl, fetch)

    async def get_fixtures(
        self,
        date_from: date,
        date_to: date,
        league_id: int | None = None,
        season: int | None = None,
    ) -> list[dict[str, Any]]:
        """Busca fixtures no intervalo [date_from, date_to].

        Se `league_id` for informado, usa o endpoint com from/to/league/season
        (dividido em blocos de até 7 dias, como exige a API). Caso contrário,
        busca globalmente dia a dia via parâmetro `date` — mais caro em termos
        de cota, mitigado pelo cache de 6h.
        """
        season = season or self._season_override or current_season(date_from)
        results: list[dict[str, Any]] = []

        if league_id is not None:
            for chunk_from, chunk_to in _date_chunks(date_from, date_to):
                params = {
                    "league": league_id,
                    "season": season,
                    "from": chunk_from.isoformat(),
                    "to": chunk_to.isoformat(),
                }
                results.extend(await self._get("/fixtures", params, TTL_FIXTURES))
        else:
            cursor = date_from
            while cursor <= date_to:
                params = {"date": cursor.isoformat()}
                results.extend(await self._get("/fixtures", params, TTL_FIXTURES))
                cursor += timedelta(days=1)

        return results

    async def get_team_statistics(
        self, team_id: int, league_id: int, season: int | None = None
    ) -> dict[str, Any]:
        season = season or self._season_override or current_season()
        params = {"team": team_id, "league": league_id, "season": season}
        response = await self._get("/teams/statistics", params, TTL_TEAM_STATISTICS)
        return response[0] if isinstance(response, list) and response else (response or {})

    async def get_h2h(
        self, team1_id: int, team2_id: int, last: int = 10
    ) -> list[dict[str, Any]]:
        params = {"h2h": f"{team1_id}-{team2_id}", "last": last}
        return await self._get("/fixtures/headtohead", params, TTL_H2H)

    async def get_injuries(
        self, team_id: int | None = None, fixture_id: int | None = None
    ) -> list[dict[str, Any]]:
        if not team_id and not fixture_id:
            raise ValueError("informe team_id ou fixture_id")

        params: dict[str, Any] = {}
        if fixture_id is not None:
            params["fixture"] = fixture_id
        else:
            params["team"] = team_id
            params["season"] = self._season_override or current_season()

        return await self._get("/injuries", params, TTL_INJURIES)
