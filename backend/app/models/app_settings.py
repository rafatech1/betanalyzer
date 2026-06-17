from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AppSettings(Base):
    """Configuração editável por usuário. Uma linha por user_id."""

    __tablename__ = "app_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True)
    banca_inicial: Mapped[float] = mapped_column(Float, nullable=False, default=1000.0)
    kelly_fraction: Mapped[float] = mapped_column(Float, nullable=False, default=0.25)
    ev_threshold: Mapped[float] = mapped_column(Float, nullable=False, default=0.03)
    favorite_league_ids: Mapped[list[int]] = mapped_column(JSON, nullable=False, default=list)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
