from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Team(Base):
    __tablename__ = "teams"
    __table_args__ = (
        # Times sourced da The Odds API não têm um ID numérico equivalente ao
        # da API-Football — upsert idempotente passa a ser por (nome, liga_id).
        UniqueConstraint("nome", "liga_id", name="uq_teams_nome_liga_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    liga_id: Mapped[int] = mapped_column(ForeignKey("leagues.id"), nullable=False)

    league: Mapped["League"] = relationship(back_populates="teams")
