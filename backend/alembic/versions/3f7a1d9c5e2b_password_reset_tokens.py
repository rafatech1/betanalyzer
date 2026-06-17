"""password reset tokens: tabela para tokens de redefinição de senha

Revision ID: 3f7a1d9c5e2b
Revises: 9d4f2a8c1b6e
Create Date: 2026-06-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "3f7a1d9c5e2b"
down_revision: Union[str, None] = "9d4f2a8c1b6e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        # UUID gerado pelo backend (não o tipo nativo Postgres) para manter
        # o link de reset simples de montar/validar como string crua.
        sa.Column("token", sa.String(36), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_unique_constraint(
        "uq_password_reset_tokens_token", "password_reset_tokens", ["token"]
    )
    op.create_index(
        "ix_password_reset_tokens_token", "password_reset_tokens", ["token"]
    )


def downgrade() -> None:
    op.drop_index("ix_password_reset_tokens_token", table_name="password_reset_tokens")
    op.drop_constraint(
        "uq_password_reset_tokens_token", "password_reset_tokens", type_="unique"
    )
    op.drop_table("password_reset_tokens")
