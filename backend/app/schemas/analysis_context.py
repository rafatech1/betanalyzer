from datetime import datetime

from pydantic import BaseModel


class OddsContext(BaseModel):
    mercado: str
    selecao: str
    odd: float
    prob_implicita: float
    casa_de_aposta: str


class AnalysisContext(BaseModel):
    fixture_id: int
    time_casa: str
    time_fora: str
    data_hora: datetime
    liga: str
    prob_modelo: dict[str, float]
    odds: list[OddsContext]
    forma_casa: str | None = None
    forma_fora: str | None = None
    h2h_resumo: str | None = None
    lesoes_casa: list[str] = []
    lesoes_fora: list[str] = []
    contexto_adicional: str | None = None
