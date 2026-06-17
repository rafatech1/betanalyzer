from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import Analysis
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
