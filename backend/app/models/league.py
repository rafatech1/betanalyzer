from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class League(Base):
    __tablename__ = "leagues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    pais: Mapped[str] = mapped_column(String(100), nullable=False)
    temporada: Mapped[int] = mapped_column(Integer, nullable=False)
    # sport_key da The Odds API (ex.: "soccer_brazil_campeonato"), usado para
    # upsert idempotente de ligas sourced de lá — que não têm um ID numérico
    # equivalente ao da API-Football. Nulo para ligas legadas da API-Football.
    external_key: Mapped[str | None] = mapped_column(String(100), nullable=True, unique=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    teams: Mapped[list["Team"]] = relationship(back_populates="league")
    fixtures: Mapped[list["Fixture"]] = relationship(back_populates="league")
