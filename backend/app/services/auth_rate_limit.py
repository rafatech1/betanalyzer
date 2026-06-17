from fastapi import HTTPException
from redis.asyncio import Redis

from app.core.config import get_settings

settings = get_settings()


def _attempts_key(ip: str) -> str:
    return f"login_attempts:{ip}"


def _lockout_key(ip: str) -> str:
    return f"login_lockout:{ip}"


async def ensure_not_rate_limited(redis: Redis, ip: str) -> None:
    if await redis.exists(_lockout_key(ip)):
        raise HTTPException(
            status_code=429, detail="Muitas tentativas de login. Tente novamente em breve."
        )


async def register_failed_attempt(redis: Redis, ip: str) -> None:
    key = _attempts_key(ip)
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, settings.login_rate_limit_window_seconds)
    if count >= settings.login_rate_limit_attempts:
        await redis.set(_lockout_key(ip), "1", ex=settings.login_lockout_seconds)
        await redis.delete(key)


async def clear_attempts(redis: Redis, ip: str) -> None:
    await redis.delete(_attempts_key(ip))
