from redis.asyncio import Redis

_PREFIX = "refresh_token:"


def _key(jti: str) -> str:
    return f"{_PREFIX}{jti}"


async def store_refresh_token(redis: Redis, jti: str, user_id: int, ttl_seconds: int) -> None:
    await redis.set(_key(jti), str(user_id), ex=ttl_seconds)


async def get_refresh_token_user_id(redis: Redis, jti: str) -> int | None:
    value = await redis.get(_key(jti))
    return int(value) if value is not None else None


async def revoke_refresh_token(redis: Redis, jti: str) -> None:
    await redis.delete(_key(jti))
