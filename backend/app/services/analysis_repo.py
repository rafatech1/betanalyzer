from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.analysis import Analysis, Recomendacao
from app.models.fixture import Fixture
from app.models.odds import Odds


async def get_latest_odds_by_selection(db: AsyncSession, fixture_id: int) -> list[Odds]:
    """Última odd registrada para cada combinação (mercado, seleção) do fixture."""
    stmt = (
        select(Odds)
        .where(Odds.fixture_id == fixture_id)
        .order_by(Odds.timestamp.desc())
    )
    result = await db.execute(stmt)

    latest: dict[tuple[str, str], Odds] = {}
    for row in result.scalars().all():
        key = (row.mercado, row.selecao)
        if key not in latest:
            latest[key] = row

    return list(latest.values())


async def get_latest_analysis_batch(db: AsyncSession, fixture_id: int) -> list[Analysis]:
    """Linhas da análise mais recente (mesmo `created_at`) para o fixture —
    representa a última vez que o pipeline completo (camada 1 + 2) rodou."""
    max_created_at = (
        select(func.max(Analysis.created_at))
        .where(Analysis.fixture_id == fixture_id)
        .scalar_subquery()
    )
    stmt = select(Analysis).where(
        Analysis.fixture_id == fixture_id, Analysis.created_at == max_created_at
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def save_analyses(db: AsyncSession, rows: list[Analysis]) -> list[Analysis]:
    db.add_all(rows)
    await db.commit()
    return rows


async def list_analyses_paginated(
    db: AsyncSession,
    limit: int,
    offset: int,
    liga_id: int | None = None,
    recomendacao: Recomendacao | None = None,
    since: datetime | None = None,
) -> tuple[list[Analysis], int]:
    """Histórico de análises (todas as execuções, mais recente primeiro)."""
    base_stmt = select(Analysis).join(Analysis.fixture)
    if liga_id is not None:
        base_stmt = base_stmt.where(Fixture.liga_id == liga_id)
    if recomendacao is not None:
        base_stmt = base_stmt.where(Analysis.recomendacao == recomendacao)
    if since is not None:
        base_stmt = base_stmt.where(Analysis.created_at >= since)

    total = (
        await db.execute(select(func.count()).select_from(base_stmt.subquery()))
    ).scalar_one()

    stmt = (
        base_stmt.options(
            selectinload(Analysis.fixture).selectinload(Fixture.league),
            selectinload(Analysis.fixture).selectinload(Fixture.time_casa),
            selectinload(Analysis.fixture).selectinload(Fixture.time_fora),
        )
        .order_by(Analysis.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all()), total
