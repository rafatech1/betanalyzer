from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import get_settings
from app.core.logging import get_logger
from app.services.cache import check_and_increment_monthly_quota, get_or_fetch_json

logger = get_logger(__name__)

QUOTA_KEY = "odds_api"

TTL_ODDS = 30 * 60  # alinhado ao intervalo de atualização de odds da Fase 2

OVER_UNDER_POINT = 2.5

MARKET_LABELS = {
    "h2h": "1x2",
    "totals": "over_under_2.5",
    "btts": "ambas_marcam",
}


@dataclass(frozen=True)
class OddsSelection:
    mercado: str
    selecao: str
    odd: float
    casa_de_aposta: str


def _normalize_selection(market_key: str, outcome_name: str, event: dict[str, Any]) -> str | None:
    if market_key == "h2h":
        if outcome_name == event.get("home_team"):
            return "casa"
        if outcome_name == event.get("away_team"):
            return "fora"
        if outcome_name.lower() == "draw":
            return "empate"
        return None

    if market_key == "totals":
        if outcome_name.lower() == "over":
            return "mais_2.5"
        if outcome_name.lower() == "under":
            return "menos_2.5"
        return None

    if market_key == "btts":
        if outcome_name.lower() == "yes":
            return "sim"
        if outcome_name.lower() == "no":
            return "nao"
        return None

    return None


def extract_best_odds(event: dict[str, Any], preferred_bookmaker: str) -> list[OddsSelection]:
    """Para cada seleção de cada mercado suportado, prioriza a odd da casa
    preferida (ex.: Betano); na ausência dela, usa a melhor odd disponível e
    registra qual casa a ofereceu."""
    # selecao -> {bookmaker_key: (price, bookmaker_title)}
    by_market_selection: dict[str, dict[str, tuple[float, str]]] = {}

    for bookmaker in event.get("bookmakers", []):
        bookmaker_key = bookmaker.get("key", "")
        bookmaker_title = bookmaker.get("title", bookmaker_key)

        for market in bookmaker.get("markets", []):
            market_key = market.get("key")
            if market_key not in MARKET_LABELS:
                continue

            for outcome in market.get("outcomes", []):
                if market_key == "totals" and outcome.get("point") != OVER_UNDER_POINT:
                    continue

                selecao = _normalize_selection(market_key, outcome.get("name", ""), event)
                if selecao is None:
                    continue

                price = outcome.get("price")
                if price is None:
                    continue

                composite_key = f"{market_key}:{selecao}"
                by_market_selection.setdefault(composite_key, {})[bookmaker_key] = (
                    float(price),
                    bookmaker_title,
                )

    results: list[OddsSelection] = []
    for composite_key, offers in by_market_selection.items():
        market_key, selecao = composite_key.split(":", 1)

        if preferred_bookmaker in offers:
            price, title = offers[preferred_bookmaker]
        else:
            price, title = max(offers.values(), key=lambda offer: offer[0])

        results.append(
            OddsSelection(
                mercado=MARKET_LABELS[market_key],
                selecao=selecao,
                odd=price,
                casa_de_aposta=title,
            )
        )

    return results


class OddsAPIClient:
    def __init__(self) -> None:
        settings = get_settings()
        self._base_url = settings.odds_api_base_url
        self._api_key = settings.odds_api_key
        self._monthly_limit = settings.odds_api_monthly_limit
        self._regions = settings.odds_api_regions
        self._preferred_bookmaker = settings.odds_api_preferred_bookmaker

    async def _request_events(
        self, sport_key: str, markets: tuple[str, ...]
    ) -> list[dict[str, Any]]:
        await check_and_increment_monthly_quota(QUOTA_KEY, self._monthly_limit)

        async with httpx.AsyncClient(base_url=self._base_url, timeout=15.0) as client:
            response = await client.get(
                f"/sports/{sport_key}/odds",
                params={
                    "apiKey": self._api_key,
                    "regions": self._regions,
                    "markets": ",".join(markets),
                    "oddsFormat": "decimal",
                },
            )
            response.raise_for_status()
            return response.json()

    async def get_events_odds(
        self, sport_key: str, markets: tuple[str, ...] = ("h2h", "totals", "btts")
    ) -> list[dict[str, Any]]:
        cache_key = f"odds_api:{sport_key}:{','.join(markets)}:{self._regions}"

        async def fetch() -> list[dict[str, Any]]:
            try:
                return await self._request_events(sport_key, markets)
            except httpx.HTTPStatusError as exc:
                # Algumas ligas não suportam o mercado "btts" e respondem 422
                # para a combinação de markets — tenta de novo sem ele antes
                # de desistir, em vez de falhar a coleta inteira da liga.
                if exc.response.status_code == 422 and "btts" in markets:
                    logger.warning(
                        "odds_api_btts_unsupported_retrying_without_btts",
                        sport_key=sport_key,
                    )
                    fallback_markets = tuple(m for m in markets if m != "btts")
                    return await self._request_events(sport_key, fallback_markets)
                raise

        return await get_or_fetch_json(cache_key, TTL_ODDS, fetch)

    async def get_match_odds(self, sport_key: str) -> dict[str, list[OddsSelection]]:
        """Retorna, por evento (chave = id do evento na The Odds API), a lista de
        seleções com a melhor odd (ou a da casa preferida, quando disponível)."""
        events = await self.get_events_odds(sport_key)

        result: dict[str, list[OddsSelection]] = {}
        for event in events:
            result[event["id"]] = extract_best_odds(event, self._preferred_bookmaker)

        return result
