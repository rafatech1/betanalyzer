from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AppSettingsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    banca_inicial: float
    kelly_fraction: float
    ev_threshold: float
    favorite_league_ids: list[int]
    updated_at: datetime


class AppSettingsUpdate(BaseModel):
    banca_inicial: float | None = None
    kelly_fraction: float | None = None
    ev_threshold: float | None = None
    favorite_league_ids: list[int] | None = None
