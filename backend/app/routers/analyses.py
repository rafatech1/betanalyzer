from datetime import datetime, timedelta, timezone
from enum import Enum

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.analysis import Analysis, Recomendacao
from app.schemas.analysis import (
    AnalysisFixtureSummary,
    AnalysisHistoryItem,
    AnalysisHistoryResponse,
)
from app.schemas.fixture import LeagueSummary, TeamOut
from app.services.analysis_repo import list_analyses_paginated

router = APIRouter(prefix="/analyses", tags=["analyses"], dependencies=[Depends(get_current_user)])


class AnalysisPeriod(str, Enum):
    week = "7d"
    month = "30d"
    all = "all"


_PERIOD_DAYS = {AnalysisPeriod.week: 7, AnalysisPeriod.month: 30}


def _to_history_item(analysis: Analysis) -> AnalysisHistoryItem:
    fixture = analysis.fixture
    return AnalysisHistoryItem(
        id=analysis.id,
        fixture=AnalysisFixtureSummary(
            id=fixture.id,
            liga=LeagueSummary(
                id=fixture.league.id, nome=fixture.league.nome, pais=fixture.league.pais
            ),
            time_casa=TeamOut(id=fixture.time_casa.id, nome=fixture.time_casa.nome),
            time_fora=TeamOut(id=fixture.time_fora.id, nome=fixture.time_fora.nome),
            data_hora=fixture.data_hora,
            status=fixture.status,
            placar_casa=fixture.placar_casa,
            placar_fora=fixture.placar_fora,
        ),
        mercado=analysis.mercado,
        selecao=analysis.selecao,
        odd_referencia=analysis.odd_referencia,
        ev=analysis.ev,
        confianca=analysis.confianca,
        recomendacao=analysis.recomendacao,
        created_at=analysis.created_at,
    )


@router.get("", response_model=AnalysisHistoryResponse)
async def list_analyses(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    liga: int | None = None,
    recomendacao: Recomendacao | None = None,
    period: AnalysisPeriod = AnalysisPeriod.all,
    db: AsyncSession = Depends(get_db),
) -> AnalysisHistoryResponse:
    since = None
    if period != AnalysisPeriod.all:
        since = datetime.now(timezone.utc) - timedelta(days=_PERIOD_DAYS[period])

    analyses, total = await list_analyses_paginated(
        db,
        limit=limit,
        offset=offset,
        liga_id=liga,
        recomendacao=recomendacao,
        since=since,
    )
    return AnalysisHistoryResponse(items=[_to_history_item(a) for a in analyses], total=total)
