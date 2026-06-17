"""initial schema

Revision ID: c3f1fd8c421a
Revises:
Create Date: 2026-06-16

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "c3f1fd8c421a"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    fixture_status = sa.Enum(
        "agendada",
        "em_andamento",
        "finalizada",
        "cancelada",
        "postergada",
        name="fixture_status",
    )
    nivel_confianca = sa.Enum("baixa", "media", "alta", name="nivel_confianca")
    recomendacao_enum = sa.Enum("apostar", "evitar", "observar", name="recomendacao")
    resultado_aposta = sa.Enum(
        "pendente", "ganha", "perdida", "anulada", "cashout", name="resultado_aposta"
    )
    tipo_movimento = sa.Enum(
        "deposito", "retirada", "aposta", "ganho", "ajuste", name="tipo_movimento"
    )

    op.create_table(
        "leagues",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("pais", sa.String(length=100), nullable=False),
        sa.Column("temporada", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )

    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column(
            "liga_id", sa.Integer(), sa.ForeignKey("leagues.id"), nullable=False
        ),
    )

    op.create_table(
        "fixtures",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "liga_id", sa.Integer(), sa.ForeignKey("leagues.id"), nullable=False
        ),
        sa.Column(
            "time_casa_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False
        ),
        sa.Column(
            "time_fora_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False
        ),
        sa.Column("data_hora", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "status",
            fixture_status,
            nullable=False,
            server_default="agendada",
        ),
        sa.Column("placar_casa", sa.Integer(), nullable=True),
        sa.Column("placar_fora", sa.Integer(), nullable=True),
    )

    op.create_table(
        "odds",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "fixture_id", sa.Integer(), sa.ForeignKey("fixtures.id"), nullable=False
        ),
        sa.Column("casa_de_aposta", sa.String(length=100), nullable=False),
        sa.Column("mercado", sa.String(length=100), nullable=False),
        sa.Column("selecao", sa.String(length=100), nullable=False),
        sa.Column("odd", sa.Float(), nullable=False),
        sa.Column(
            "prob_implicita",
            sa.Float(),
            nullable=False,
            comment="Probabilidade implícita já sem o overround",
        ),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_odds_fixture_mercado_timestamp",
        "odds",
        ["fixture_id", "mercado", "timestamp"],
    )

    op.create_table(
        "analyses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "fixture_id", sa.Integer(), sa.ForeignKey("fixtures.id"), nullable=False
        ),
        sa.Column("prob_estimada", sa.Float(), nullable=False),
        sa.Column("prob_implicita", sa.Float(), nullable=False),
        sa.Column(
            "ev", sa.Float(), nullable=False, comment="Valor esperado (EV)"
        ),
        sa.Column("confianca", nivel_confianca, nullable=False),
        sa.Column("recomendacao", recomendacao_enum, nullable=False),
        sa.Column(
            "stake_sugerido",
            sa.Float(),
            nullable=False,
            comment="Fração da banca, Kelly fracionado máx. 25% do Kelly",
        ),
        sa.Column("resumo_ia", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )

    op.create_table(
        "bets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "fixture_id", sa.Integer(), sa.ForeignKey("fixtures.id"), nullable=False
        ),
        sa.Column(
            "analysis_id", sa.Integer(), sa.ForeignKey("analyses.id"), nullable=True
        ),
        sa.Column("mercado", sa.String(length=100), nullable=False),
        sa.Column("selecao", sa.String(length=100), nullable=False),
        sa.Column("odd", sa.Float(), nullable=False),
        sa.Column("stake", sa.Float(), nullable=False),
        sa.Column(
            "resultado",
            resultado_aposta,
            nullable=False,
            server_default="pendente",
        ),
        sa.Column("lucro", sa.Float(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )

    op.create_table(
        "bankroll",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tipo", tipo_movimento, nullable=False),
        sa.Column("valor", sa.Float(), nullable=False),
        sa.Column("saldo_resultante", sa.Float(), nullable=False),
        sa.Column("descricao", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )


def downgrade() -> None:
    op.drop_table("bankroll")
    op.drop_table("bets")
    op.drop_table("analyses")
    op.drop_index("ix_odds_fixture_mercado_timestamp", table_name="odds")
    op.drop_table("odds")
    op.drop_table("fixtures")
    op.drop_table("teams")
    op.drop_table("leagues")

    sa.Enum(name="tipo_movimento").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="resultado_aposta").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="recomendacao").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="nivel_confianca").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="fixture_status").drop(op.get_bind(), checkfirst=True)
