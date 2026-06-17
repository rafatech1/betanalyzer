from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.fixture import FixtureStatus


class TeamOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str


class LeagueSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    pais: str


class FixtureOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    liga_id: int
    liga: LeagueSummary
    time_casa: TeamOut
    time_fora: TeamOut
    data_hora: datetime
    status: FixtureStatus
    placar_casa: int | None
    placar_fora: int | None
    odds_1x2: dict[str, float] | None = None
