import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Recomendacao(str, enum.Enum):
    APOSTAR = "apostar"
    EVITAR = "evitar"
    OBSERVAR = "observar"


class NivelConfianca(str, enum.Enum):
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fixture_id: Mapped[int] = mapped_column(ForeignKey("fixtures.id"), nullable=False)
    mercado: Mapped[str] = mapped_column(String(100), nullable=False)
    selecao: Mapped[str] = mapped_column(String(100), nullable=False)
    odd_referencia: Mapped[float] = mapped_column(
        Float, nullable=False, comment="Odd usada no cálculo do EV no momento da análise"
    )
    prob_estimada: Mapped[float] = mapped_column(Float, nullable=False)
    prob_implicita: Mapped[float] = mapped_column(Float, nullable=False)
    ev: Mapped[float] = mapped_column(Float, nullable=False, comment="Valor esperado (EV)")
    confianca: Mapped[NivelConfianca] = mapped_column(
        # values_callable é necessário porque o SQLAlchemy, por padrão, usa o
        # NOME do membro do enum (BAIXA/MEDIA/ALTA) para o valor no banco, não
        # o .value — mesmo bug corrigido em UserRole (ver app/models/user.py).
        Enum(
            NivelConfianca,
            name="nivel_confianca",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        nullable=False,
    )
    recomendacao: Mapped[Recomendacao] = mapped_column(
        Enum(
            Recomendacao,
            name="recomendacao",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        nullable=False,
    )
    stake_sugerido: Mapped[float] = mapped_column(
        Float, nullable=False, comment="Fração da banca, Kelly fracionado máx. 25% do Kelly"
    )
    resumo_ia: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    fixture: Mapped["Fixture"] = relationship(back_populates="analyses")
