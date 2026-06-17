import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ResultadoAposta(str, enum.Enum):
    PENDENTE = "pendente"
    GANHA = "ganha"
    PERDIDA = "perdida"
    ANULADA = "anulada"
    CASHOUT = "cashout"


class Bet(Base):
    __tablename__ = "bets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    fixture_id: Mapped[int] = mapped_column(ForeignKey("fixtures.id"), nullable=False)
    analysis_id: Mapped[int | None] = mapped_column(
        ForeignKey("analyses.id"), nullable=True
    )
    mercado: Mapped[str] = mapped_column(String(100), nullable=False)
    selecao: Mapped[str] = mapped_column(String(100), nullable=False)
    odd: Mapped[float] = mapped_column(Float, nullable=False)
    stake: Mapped[float] = mapped_column(Float, nullable=False)
    resultado: Mapped[ResultadoAposta] = mapped_column(
        # values_callable é necessário porque o SQLAlchemy, por padrão, usa o
        # NOME do membro do enum para o valor no banco, não o .value — mesmo
        # bug corrigido em UserRole (ver app/models/user.py).
        Enum(
            ResultadoAposta,
            name="resultado_aposta",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        nullable=False,
        default=ResultadoAposta.PENDENTE,
    )
    lucro: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    fixture: Mapped["Fixture"] = relationship(back_populates="bets")
