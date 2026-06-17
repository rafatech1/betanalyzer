import uuid
from contextlib import asynccontextmanager
from typing import AsyncIterator

from app.db.redis import redis_client

LOCK_TTL_SECONDS = 60


class AnalysisInProgressError(Exception):
    """Já existe uma análise em andamento para este fixture."""


@asynccontextmanager
async def analysis_lock(fixture_id: int) -> AsyncIterator[None]:
    """Lock distribuído no Redis para impedir que duas requisições simultâneas
    disparem o pipeline (camada estatística + chamada ao Claude) duplicado
    para o mesmo jogo — essencial na arquitetura de análise compartilhada."""
    key = f"analysis:lock:{fixture_id}"
    token = uuid.uuid4().hex

    acquired = await redis_client.set(key, token, nx=True, ex=LOCK_TTL_SECONDS)
    if not acquired:
        raise AnalysisInProgressError(f"Análise já em andamento para o fixture {fixture_id}")

    try:
        yield
    finally:
        current = await redis_client.get(key)
        if current == token:
            await redis_client.delete(key)
