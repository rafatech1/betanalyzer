from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Odds(Base):
    """Histórico de odds. Cada coleta gera uma nova linha — nunca sobrescrever."""

    __tablename__ = "odds"
    __table_args__ = (
        Index("ix_odds_fixture_mercado_timestamp", "fixture_id", "mercado", "timestamp"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fixture_id: Mapped[int] = mapped_column(ForeignKey("fixtures.id"), nullable=False)
    casa_de_aposta: Mapped[str] = mapped_column(String(100), nullable=False)
    mercado: Mapped[str] = mapped_column(String(100), nullable=False)
    selecao: Mapped[str] = mapped_column(String(100), nullable=False)
    odd: Mapped[float] = mapped_column(Float, nullable=False)
    prob_implicita: Mapped[float] = mapped_column(
        Float, nullable=False, comment="Probabilidade implícita já sem o overround"
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    fixture: Mapped["Fixture"] = relationship(back_populates="odds")
