from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.analysis import NivelConfianca, Recomendacao
from app.models.fixture import FixtureStatus
from app.schemas.fixture import LeagueSummary, TeamOut

RISK_WARNING = (
    "Esta análise não garante resultados. Toda aposta envolve risco de perda de capital. "
    "Use sempre as ferramentas de controle de banca e nunca aposte mais do que pode perder."
)


class AnalyzeRequest(BaseModel):
    contexto_adicional: str | None = None


class AnalysisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fixture_id: int
    mercado: str
    selecao: str
    odd_referencia: float
    prob_estimada: float
    prob_implicita: float
    ev: float
    confianca: NivelConfianca
    recomendacao: Recomendacao
    stake_sugerido: float
    resumo_ia: str | None
    created_at: datetime


class AnalyzeResponse(BaseModel):
    aviso_risco: str = RISK_WARNING
    analises: list[AnalysisOut]


class AnalysisFixtureSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    liga: LeagueSummary
    time_casa: TeamOut
    time_fora: TeamOut
    data_hora: datetime
    status: FixtureStatus
    placar_casa: int | None
    placar_fora: int | None


class AnalysisHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fixture: AnalysisFixtureSummary
    mercado: str
    selecao: str
    odd_referencia: float
    ev: float
    confianca: NivelConfianca
    recomendacao: Recomendacao
    created_at: datetime


class AnalysisHistoryResponse(BaseModel):
    items: list[AnalysisHistoryItem]
    total: int
