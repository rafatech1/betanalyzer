import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        # values_callable é necessário porque o SQLAlchemy, por padrão, usa o
        # NOME do membro do enum (ADMIN/USER) para o valor no banco, não o
        # .value ("admin"/"user") — e o tipo nativo `user_role` no Postgres
        # foi criado pela migração só com os labels minúsculos.
        Enum(UserRole, name="user_role", values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        nullable=False,
        default=UserRole.USER,
    )
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
