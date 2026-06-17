import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class FixtureStatus(str, enum.Enum):
    AGENDADA = "agendada"
    EM_ANDAMENTO = "em_andamento"
    FINALIZADA = "finalizada"
    CANCELADA = "cancelada"
    POSTERGADA = "postergada"


class Fixture(Base):
    __tablename__ = "fixtures"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    liga_id: Mapped[int] = mapped_column(ForeignKey("leagues.id"), nullable=False)
    time_casa_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    time_fora_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    data_hora: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[FixtureStatus] = mapped_column(
        # values_callable é necessário porque o SQLAlchemy, por padrão, usa o
        # NOME do membro do enum (AGENDADA/EM_ANDAMENTO/...) para o valor no
        # banco, não o .value — mesmo bug corrigido em UserRole (ver
        # app/models/user.py).
        Enum(
            FixtureStatus,
            name="fixture_status",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        nullable=False,
        default=FixtureStatus.AGENDADA,
    )
    placar_casa: Mapped[int | None] = mapped_column(Integer, nullable=True)
    placar_fora: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # ID do evento na The Odds API (fonte principal de fixtures desde que o
    # plano gratuito da API-Football deixou de cobrir a temporada atual).
    # Nulo para fixtures legados sourced da API-Football.
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)

    league: Mapped["League"] = relationship(back_populates="fixtures")
    time_casa: Mapped["Team"] = relationship(foreign_keys=[time_casa_id])
    time_fora: Mapped["Team"] = relationship(foreign_keys=[time_fora_id])
    odds: Mapped[list["Odds"]] = relationship(back_populates="fixture")
    analyses: Mapped[list["Analysis"]] = relationship(back_populates="fixture")
    bets: Mapped[list["Bet"]] = relationship(back_populates="fixture")
