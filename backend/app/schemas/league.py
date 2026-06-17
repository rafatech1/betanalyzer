from pydantic import BaseModel, ConfigDict


class LeagueOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    pais: str
    temporada: int
