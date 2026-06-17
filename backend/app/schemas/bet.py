from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.bet import ResultadoAposta


class BetFixtureSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    time_casa: str
    time_fora: str
    data_hora: datetime


class BetCreate(BaseModel):
    fixture_id: int
    mercado: str
    selecao: str
    odd: float
    stake: float
    analysis_id: int | None = None


class BetUpdate(BaseModel):
    resultado: ResultadoAposta
    lucro: float | None = None


class BetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fixture_id: int
    analysis_id: int | None
    mercado: str
    selecao: str
    odd: float
    stake: float
    resultado: ResultadoAposta
    lucro: float | None
    created_at: datetime
    fixture: BetFixtureSummary | None = None


class BetStatsOut(BaseModel):
    total_apostas: int
    apostas_resolvidas: int
    taxa_acerto: float | None
    total_investido: float
    lucro_acumulado: float
    roi: float | None
    yield_: float | None
    evolucao: list["BankrollPoint"]


class BankrollPoint(BaseModel):
    data: datetime
    saldo_acumulado: float


BetStatsOut.model_rebuild()
