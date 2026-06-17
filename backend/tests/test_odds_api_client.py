from typing import Any

import httpx
import pytest

from app.services.external import odds_api as odds_api_module
from app.services.external.odds_api import OddsAPIClient


class _FakeResponse:
    def __init__(self, status_code: int, payload: Any = None) -> None:
        self.status_code = status_code
        self._payload = payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                f"status {self.status_code}",
                request=httpx.Request("GET", "http://test"),
                response=httpx.Response(self.status_code, request=httpx.Request("GET", "http://test")),
            )

    def json(self) -> Any:
        return self._payload


def _make_fake_client(calls: list[dict[str, Any]]):
    class _FakeAsyncClient:
        def __init__(self, *args, **kwargs) -> None:
            pass

        async def __aenter__(self) -> "_FakeAsyncClient":
            return self

        async def __aexit__(self, *exc_info) -> None:
            return None

        async def get(self, path: str, params: dict[str, Any]) -> _FakeResponse:
            calls.append(params)
            if "btts" in params["markets"].split(","):
                return _FakeResponse(422)
            return _FakeResponse(200, [{"id": "evt1"}])

    return _FakeAsyncClient


@pytest.fixture(autouse=True)
def _bypass_cache_and_quota(monkeypatch):
    async def fake_quota(*args, **kwargs) -> int:
        return 1

    async def fake_get_or_fetch_json(key: str, ttl: int, fetcher):
        return await fetcher()

    monkeypatch.setattr(odds_api_module, "check_and_increment_monthly_quota", fake_quota)
    monkeypatch.setattr(odds_api_module, "get_or_fetch_json", fake_get_or_fetch_json)


@pytest.mark.asyncio
async def test_retries_without_btts_on_422(monkeypatch) -> None:
    calls: list[dict[str, Any]] = []
    monkeypatch.setattr(httpx, "AsyncClient", _make_fake_client(calls))

    client = OddsAPIClient()
    events = await client.get_events_odds("soccer_some_league")

    assert events == [{"id": "evt1"}]
    assert len(calls) == 2
    assert calls[0]["markets"] == "h2h,totals,btts"
    assert calls[1]["markets"] == "h2h,totals"


@pytest.mark.asyncio
async def test_does_not_retry_when_btts_not_requested(monkeypatch) -> None:
    calls: list[dict[str, Any]] = []
    monkeypatch.setattr(httpx, "AsyncClient", _make_fake_client(calls))

    client = OddsAPIClient()
    events = await client.get_events_odds("soccer_some_league", markets=("h2h", "totals"))

    assert events == [{"id": "evt1"}]
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_propagates_non_422_errors(monkeypatch) -> None:
    class _FakeAsyncClient500:
        def __init__(self, *args, **kwargs) -> None:
            pass

        async def __aenter__(self) -> "_FakeAsyncClient500":
            return self

        async def __aexit__(self, *exc_info) -> None:
            return None

        async def get(self, path: str, params: dict[str, Any]) -> _FakeResponse:
            return _FakeResponse(500)

    monkeypatch.setattr(httpx, "AsyncClient", _FakeAsyncClient500)

    client = OddsAPIClient()
    with pytest.raises(httpx.HTTPStatusError):
        await client.get_events_odds("soccer_some_league")
