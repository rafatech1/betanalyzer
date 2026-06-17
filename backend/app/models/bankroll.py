import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TipoMovimento(str, enum.Enum):
    DEPOSITO = "deposito"
    RETIRADA = "retirada"
    APOSTA = "aposta"
    GANHO = "ganho"
    AJUSTE = "ajuste"


class Bankroll(Base):
    __tablename__ = "bankroll"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    tipo: Mapped[TipoMovimento] = mapped_column(
        Enum(TipoMovimento, name="tipo_movimento"), nullable=False
    )
    valor: Mapped[float] = mapped_column(Float, nullable=False)
    saldo_resultante: Mapped[float] = mapped_column(Float, nullable=False)
    descricao: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
