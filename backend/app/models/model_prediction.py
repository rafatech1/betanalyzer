from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ModelPrediction(Base):
    """Previsão bruta da Camada 1 (Dixon-Coles), antes do ajuste qualitativo do
    Claude. Usada para monitorar a calibração do modelo via Brier score —
    independe de uma análise ter sido recomendada ou não."""

    __tablename__ = "model_predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fixture_id: Mapped[int] = mapped_column(ForeignKey("fixtures.id"), nullable=False)
    mercado: Mapped[str] = mapped_column(String(100), nullable=False)
    selecao: Mapped[str] = mapped_column(String(100), nullable=False)
    prob_estimada: Mapped[float] = mapped_column(Float, nullable=False)
    resultado_real: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, comment="Preenchido quando o fixture é finalizado"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    fixture: Mapped["Fixture"] = relationship()
