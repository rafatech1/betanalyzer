"""odds-api fixture sourcing: external keys for league-upsert-without-api-football-id

Revision ID: 9d4f2a8c1b6e
Revises: 2b6c9e1a7f3d
Create Date: 2026-06-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "9d4f2a8c1b6e"
down_revision: Union[str, None] = "2b6c9e1a7f3d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # sport_key da The Odds API (ex.: "soccer_brazil_campeonato") — permite
    # upsert idempotente de ligas sourced de lá, que não têm um ID numérico
    # equivalente ao da API-Football.
    op.add_column("leagues", sa.Column("external_key", sa.String(100), nullable=True))
    op.create_unique_constraint("uq_leagues_external_key", "leagues", ["external_key"])

    # Times sourced da The Odds API só têm nome (sem ID estável) — upsert
    # idempotente passa a ser por (nome, liga_id).
    op.create_unique_constraint("uq_teams_nome_liga_id", "teams", ["nome", "liga_id"])

    # ID do evento na The Odds API — permite upsert idempotente de fixtures
    # sourced de lá (a API não compartilha IDs com a API-Football).
    op.add_column("fixtures", sa.Column("external_id", sa.String(255), nullable=True))
    op.create_unique_constraint("uq_fixtures_external_id", "fixtures", ["external_id"])


def downgrade() -> None:
    op.drop_constraint("uq_fixtures_external_id", "fixtures", type_="unique")
    op.drop_column("fixtures", "external_id")
    op.drop_constraint("uq_teams_nome_liga_id", "teams", type_="unique")
    op.drop_constraint("uq_leagues_external_key", "leagues", type_="unique")
    op.drop_column("leagues", "external_key")
