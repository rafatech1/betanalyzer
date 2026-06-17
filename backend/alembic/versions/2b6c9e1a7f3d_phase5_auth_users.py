"""phase5: users table + user_id scoping on bets/bankroll/app_settings

Revision ID: 2b6c9e1a7f3d
Revises: 8f3a1c2d4e6b
Create Date: 2026-06-16

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "2b6c9e1a7f3d"
down_revision: Union[str, None] = "8f3a1c2d4e6b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("senha_hash", sa.String(255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("admin", "user", name="user_role"),
            nullable=False,
            server_default="user",
        ),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.add_column(
        "bets", sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True)
    )
    op.add_column(
        "bankroll", sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True)
    )

    # app_settings era uma tabela singleton (id=1); a partir daqui passa a ser
    # uma linha por usuário, então a linha antiga (sem dono) é descartada.
    op.execute("DELETE FROM app_settings")
    op.add_column(
        "app_settings",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
    )
    op.create_unique_constraint("uq_app_settings_user_id", "app_settings", ["user_id"])


def downgrade() -> None:
    op.drop_constraint("uq_app_settings_user_id", "app_settings", type_="unique")
    op.drop_column("app_settings", "user_id")
    op.drop_column("bankroll", "user_id")
    op.drop_column("bets", "user_id")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS user_role")
