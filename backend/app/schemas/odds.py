from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OddsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fixture_id: int
    casa_de_aposta: str
    mercado: str
    selecao: str
    odd: float
    prob_implicita: float
    timestamp: datetime
