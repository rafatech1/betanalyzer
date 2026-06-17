from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.bankroll import TipoMovimento


class BankrollCreate(BaseModel):
    tipo: TipoMovimento
    valor: float
    descricao: str | None = None


class BankrollOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: TipoMovimento
    valor: float
    saldo_resultante: float
    descricao: str | None
    created_at: datetime


class BankrollSummaryOut(BaseModel):
    saldo_atual: float
    movimentos: list[BankrollOut]
