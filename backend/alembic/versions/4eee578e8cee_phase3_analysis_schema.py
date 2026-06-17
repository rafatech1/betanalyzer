"""phase3 analysis schema: mercado/selecao/odd_referencia em analyses + model_predictions

Revision ID: 4eee578e8cee
Revises: c3f1fd8c421a
Create Date: 2026-06-16

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "4eee578e8cee"
down_revision: Union[str, None] = "c3f1fd8c421a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "analyses", sa.Column("mercado", sa.String(length=100), nullable=False, server_default="1x2")
    )
    op.add_column(
        "analyses", sa.Column("selecao", sa.String(length=100), nullable=False, server_default="casa")
    )
    op.add_column(
        "analyses",
        sa.Column(
            "odd_referencia",
            sa.Float(),
            nullable=False,
            server_default="1",
            comment="Odd usada no cálculo do EV no momento da análise",
        ),
    )
    op.alter_column("analyses", "mercado", server_default=None)
    op.alter_column("analyses", "selecao", server_default=None)
    op.alter_column("analyses", "odd_referencia", server_default=None)

    op.create_table(
        "model_predictions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "fixture_id", sa.Integer(), sa.ForeignKey("fixtures.id"), nullable=False
        ),
        sa.Column("mercado", sa.String(length=100), nullable=False),
        sa.Column("selecao", sa.String(length=100), nullable=False),
        sa.Column("prob_estimada", sa.Float(), nullable=False),
        sa.Column(
            "resultado_real",
            sa.Boolean(),
            nullable=True,
            comment="Preenchido quando o fixture é finalizado",
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )
    op.create_index(
        "ix_model_predictions_fixture_resultado",
        "model_predictions",
        ["fixture_id", "resultado_real"],
    )


def downgrade() -> None:
    op.drop_index("ix_model_predictions_fixture_resultado", table_name="model_predictions")
    op.drop_table("model_predictions")
    op.drop_column("analyses", "odd_referencia")
    op.drop_column("analyses", "selecao")
    op.drop_column("analyses", "mercado")
