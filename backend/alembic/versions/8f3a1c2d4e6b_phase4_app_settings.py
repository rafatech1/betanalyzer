"""phase4: app_settings singleton table

Revision ID: 8f3a1c2d4e6b
Revises: 4eee578e8cee
Create Date: 2026-06-16

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "8f3a1c2d4e6b"
down_revision: Union[str, None] = "4eee578e8cee"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "app_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("banca_inicial", sa.Float(), nullable=False, server_default="1000"),
        sa.Column("kelly_fraction", sa.Float(), nullable=False, server_default="0.25"),
        sa.Column("ev_threshold", sa.Float(), nullable=False, server_default="0.03"),
        sa.Column("favorite_league_ids", sa.JSON(), nullable=False),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )
    op.execute(
        "INSERT INTO app_settings (id, banca_inicial, kelly_fraction, ev_threshold, favorite_league_ids) "
        "VALUES (1, 1000, 0.25, 0.03, '[]')"
    )


def downgrade() -> None:
    op.drop_table("app_settings")
