import json
from datetime import datetime, timedelta, timezone
from typing import Any

from app.core.logging import get_logger
from app.db.redis import redis_client

logger = get_logger(__name__)

SECONDS_PER_DAY = 86_400


class QuotaExceededError(Exception):
    """Limite de requisições do plano gratuito da API foi atingido."""


async def cache_get_json(key: str) -> Any | None:
    raw = await redis_client.get(key)
    return json.loads(raw) if raw is not None else None


async def cache_set_json(key: str, value: Any, ttl_seconds: int) -> None:
    await redis_client.set(key, json.dumps(value), ex=ttl_seconds)


async def get_or_fetch_json(
    key: str, ttl_seconds: int, fetcher: Any
) -> Any:
    """Retorna o valor em cache se existir; caso contrário, chama `fetcher` (coroutine
    sem argumentos) e armazena o resultado em cache antes de retorná-lo."""
    cached = await cache_get_json(key)
    if cached is not None:
        logger.debug("cache_hit", key=key)
        return cached

    logger.debug("cache_miss", key=key)
    value = await fetcher()
    await cache_set_json(key, value, ttl_seconds)
    return value


def _seconds_until_next_day(now: datetime) -> int:
    tomorrow = (now + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return max(int((tomorrow - now).total_seconds()), 1)


def _seconds_until_next_month(now: datetime) -> int:
    if now.month == 12:
        next_month = now.replace(
            year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0
        )
    else:
        next_month = now.replace(
            month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0
        )
    return max(int((next_month - now).total_seconds()), 1)


async def check_and_increment_daily_quota(quota_key: str, limit: int) -> int:
    """Incrementa o contador diário de requisições e levanta QuotaExceededError
    se o limite do plano gratuito for excedido. Retorna a contagem atual."""
    now = datetime.now(timezone.utc)
    key = f"quota:daily:{quota_key}:{now.date().isoformat()}"

    current = await redis_client.incr(key)
    if current == 1:
        await redis_client.expire(key, _seconds_until_next_day(now))

    if current > limit:
        logger.warning("quota_exceeded", quota_key=quota_key, current=current, limit=limit)
        raise QuotaExceededError(
            f"Limite diário de requisições excedido para {quota_key}: {current}/{limit}"
        )

    return current


async def check_and_increment_monthly_quota(quota_key: str, limit: int) -> int:
    """Incrementa o contador mensal de requisições e levanta QuotaExceededError
    se o limite do plano gratuito for excedido. Retorna a contagem atual."""
    now = datetime.now(timezone.utc)
    key = f"quota:monthly:{quota_key}:{now.year}-{now.month:02d}"

    current = await redis_client.incr(key)
    if current == 1:
        await redis_client.expire(key, _seconds_until_next_month(now))

    if current > limit:
        logger.warning("quota_exceeded", quota_key=quota_key, current=current, limit=limit)
        raise QuotaExceededError(
            f"Limite mensal de requisições excedido para {quota_key}: {current}/{limit}"
        )

    return current
