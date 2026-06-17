import pytest

from app.services.auth_rate_limit import (
    clear_attempts,
    ensure_not_rate_limited,
    register_failed_attempt,
)


class FakeRedis:
    """Minimal in-memory stand-in for redis.asyncio.Redis, async-compatible."""

    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    async def exists(self, key: str) -> int:
        return 1 if key in self._store else 0

    async def get(self, key: str) -> str | None:
        return self._store.get(key)

    async def incr(self, key: str) -> int:
        value = int(self._store.get(key, "0")) + 1
        self._store[key] = str(value)
        return value

    async def expire(self, key: str, ttl: int) -> None:
        pass

    async def set(self, key: str, value: str, ex: int | None = None) -> None:
        self._store[key] = value

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)


@pytest.mark.asyncio
async def test_ensure_not_rate_limited_passes_when_no_lockout() -> None:
    redis = FakeRedis()
    await ensure_not_rate_limited(redis, "1.2.3.4")


@pytest.mark.asyncio
async def test_repeated_failures_trigger_lockout() -> None:
    redis = FakeRedis()
    ip = "1.2.3.4"

    for _ in range(5):
        await register_failed_attempt(redis, ip)

    with pytest.raises(Exception) as exc_info:
        await ensure_not_rate_limited(redis, ip)
    assert exc_info.value.status_code == 429


@pytest.mark.asyncio
async def test_clear_attempts_removes_counter() -> None:
    redis = FakeRedis()
    ip = "1.2.3.4"

    await register_failed_attempt(redis, ip)
    await clear_attempts(redis, ip)

    assert await redis.get("login_attempts:1.2.3.4") is None
