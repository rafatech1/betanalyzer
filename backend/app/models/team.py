from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    liga_id: Mapped[int] = mapped_column(ForeignKey("leagues.id"), nullable=False)

    league: Mapped["League"] = relationship(back_populates="teams")
