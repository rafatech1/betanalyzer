from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, selectinload

from app.models.fixture import Fixture, FixtureStatus
from app.models.league import League
from app.models.team import Team
from app.services.external.api_football import current_season

_STATUS_MAP: dict[str, FixtureStatus] = {
    "NS": FixtureStatus.AGENDADA,
    "TBD": FixtureStatus.AGENDADA,
    "1H": FixtureStatus.EM_ANDAMENTO,
    "HT": FixtureStatus.EM_ANDAMENTO,
    "2H": FixtureStatus.EM_ANDAMENTO,
    "ET": FixtureStatus.EM_ANDAMENTO,
    "BT": FixtureStatus.EM_ANDAMENTO,
    "P": FixtureStatus.EM_ANDAMENTO,
    "LIVE": FixtureStatus.EM_ANDAMENTO,
    "FT": FixtureStatus.FINALIZADA,
    "AET": FixtureStatus.FINALIZADA,
    "PEN": FixtureStatus.FINALIZADA,
    "PST": FixtureStatus.POSTERGADA,
    "SUSP": FixtureStatus.POSTERGADA,
    "INT": FixtureStatus.POSTERGADA,
    "CANC": FixtureStatus.CANCELADA,
    "ABD": FixtureStatus.CANCELADA,
    "AWD": FixtureStatus.CANCELADA,
    "WO": FixtureStatus.CANCELADA,
}


def map_fixture_status(short_status: str) -> FixtureStatus:
    return _STATUS_MAP.get(short_status, FixtureStatus.AGENDADA)


async def _upsert_league(db: AsyncSession, league_payload: dict[str, Any]) -> None:
    stmt = pg_insert(League).values(
        id=league_payload["id"],
        nome=league_payload["name"],
        pais=league_payload.get("country", ""),
        temporada=league_payload.get("season"),
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=[League.id],
        set_={
            "nome": stmt.excluded.nome,
            "pais": stmt.excluded.pais,
            "temporada": stmt.excluded.temporada,
        },
    )
    await db.execute(stmt)


async def _upsert_team(db: AsyncSession, team_payload: dict[str, Any], liga_id: int) -> None:
    stmt = pg_insert(Team).values(
        id=team_payload["id"],
        nome=team_payload["name"],
        liga_id=liga_id,
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=[Team.id],
        set_={"nome": stmt.excluded.nome, "liga_id": stmt.excluded.liga_id},
    )
    await db.execute(stmt)


async def _upsert_fixture(
    db: AsyncSession,
    fixture_payload: dict[str, Any],
    league_id: int,
    teams_payload: dict[str, Any],
    goals_payload: dict[str, Any],
) -> int:
    fixture_id = fixture_payload["id"]
    status = map_fixture_status(fixture_payload["status"]["short"])

    stmt = pg_insert(Fixture).values(
        id=fixture_id,
        liga_id=league_id,
        time_casa_id=teams_payload["home"]["id"],
        time_fora_id=teams_payload["away"]["id"],
        data_hora=datetime.fromisoformat(fixture_payload["date"]),
        status=status,
        placar_casa=goals_payload.get("home"),
        placar_fora=goals_payload.get("away"),
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=[Fixture.id],
        set_={
            "status": stmt.excluded.status,
            "placar_casa": stmt.excluded.placar_casa,
            "placar_fora": stmt.excluded.placar_fora,
            "data_hora": stmt.excluded.data_hora,
        },
    )
    await db.execute(stmt)
    return fixture_id


async def upsert_fixtures_batch(db: AsyncSession, fixtures_payload: list[dict[str, Any]]) -> list[int]:
    """Persiste leagues, teams e fixtures a partir do payload bruto da API-Football.
    Idempotente: cada fixture é identificado pelo próprio id da API-Football."""
    fixture_ids: list[int] = []

    for item in fixtures_payload:
        league_payload = item["league"]
        teams_payload = item["teams"]
        fixture_payload = item["fixture"]
        goals_payload = item.get("goals", {}) or {}

        await _upsert_league(db, league_payload)
        await _upsert_team(db, teams_payload["home"], league_payload["id"])
        await _upsert_team(db, teams_payload["away"], league_payload["id"])
        fixture_id = await _upsert_fixture(
            db, fixture_payload, league_payload["id"], teams_payload, goals_payload
        )
        fixture_ids.append(fixture_id)

    await db.commit()
    return fixture_ids


# Rótulo (nome, país) para sport_keys conhecidos da The Odds API — usados
# como fonte principal de fixtures desde que o plano gratuito da API-Football
# deixou de cobrir a temporada atual. Chaves fora deste mapa recebem um rótulo
# derivado automaticamente (ver `_league_info_from_sport_key`).
SPORT_KEY_LEAGUE_INFO: dict[str, tuple[str, str]] = {
    "soccer_brazil_campeonato": ("Brasileirão Série A", "Brasil"),
    "soccer_brazil_serie_b": ("Brasileirão Série B", "Brasil"),
    "soccer_epl": ("Premier League", "Inglaterra"),
    "soccer_spain_la_liga": ("La Liga", "Espanha"),
    "soccer_italy_serie_a": ("Serie A", "Itália"),
    "soccer_germany_bundesliga": ("Bundesliga", "Alemanha"),
    "soccer_france_ligue_one": ("Ligue 1", "França"),
    "soccer_portugal_primeira_liga": ("Primeira Liga", "Portugal"),
    "soccer_netherlands_eredivisie": ("Eredivisie", "Holanda"),
    "soccer_uefa_champs_league": ("UEFA Champions League", "Europa"),
    "soccer_uefa_europa_league": ("UEFA Europa League", "Europa"),
    "soccer_conmebol_copa_libertadores": ("Copa Libertadores", "América do Sul"),
}


def _league_info_from_sport_key(sport_key: str) -> tuple[str, str]:
    if sport_key in SPORT_KEY_LEAGUE_INFO:
        return SPORT_KEY_LEAGUE_INFO[sport_key]
    label = sport_key.removeprefix("soccer_").replace("_", " ").title()
    return label, "Desconhecido"


def _parse_commence_time(raw: str) -> datetime:
    return datetime.fromisoformat(raw.replace("Z", "+00:00"))


async def upsert_league_from_sport_key(db: AsyncSession, sport_key: str) -> int:
    """Upsert idempotente de uma liga sourced da The Odds API, identificada
    pelo sport_key (sem ID numérico equivalente ao da API-Football)."""
    nome, pais = _league_info_from_sport_key(sport_key)
    stmt = pg_insert(League).values(
        external_key=sport_key,
        nome=nome,
        pais=pais,
        temporada=current_season(),
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=[League.external_key],
        set_={"nome": stmt.excluded.nome, "pais": stmt.excluded.pais},
    ).returning(League.id)
    result = await db.execute(stmt)
    return result.scalar_one()


async def upsert_team_by_name(db: AsyncSession, nome: str, liga_id: int) -> int:
    """Upsert idempotente de um time sourced da The Odds API, identificado
    por (nome, liga_id) — a API só fornece o nome, sem ID estável."""
    stmt = pg_insert(Team).values(nome=nome, liga_id=liga_id)
    stmt = stmt.on_conflict_do_update(
        index_elements=[Team.nome, Team.liga_id],
        set_={"nome": stmt.excluded.nome},
    ).returning(Team.id)
    result = await db.execute(stmt)
    return result.scalar_one()


async def upsert_fixtures_from_odds_events(
    db: AsyncSession, sport_key: str, events: list[dict[str, Any]]
) -> list[int]:
    """Persiste leagues, teams e fixtures a partir de eventos da The Odds API.

    Diferente de `upsert_fixtures_batch` (API-Football), a The Odds API não
    informa placar nem status ao vivo/finalizado — fixtures novos entram
    sempre como AGENDADA, e o status não é atualizado por aqui depois disso.
    """
    if not events:
        return []

    league_id = await upsert_league_from_sport_key(db, sport_key)

    fixture_ids: list[int] = []
    for event in events:
        home_id = await upsert_team_by_name(db, event["home_team"], league_id)
        away_id = await upsert_team_by_name(db, event["away_team"], league_id)

        stmt = pg_insert(Fixture).values(
            external_id=event["id"],
            liga_id=league_id,
            time_casa_id=home_id,
            time_fora_id=away_id,
            data_hora=_parse_commence_time(event["commence_time"]),
            status=FixtureStatus.AGENDADA,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=[Fixture.external_id],
            set_={
                "data_hora": stmt.excluded.data_hora,
                "time_casa_id": stmt.excluded.time_casa_id,
                "time_fora_id": stmt.excluded.time_fora_id,
            },
        ).returning(Fixture.id)
        result = await db.execute(stmt)
        fixture_ids.append(result.scalar_one())

    await db.commit()
    return fixture_ids


async def get_upcoming_fixtures_with_teams(
    db: AsyncSession, window_hours: int
) -> list[dict[str, Any]]:
    """Fixtures agendados nas próximas `window_hours` horas, com nomes dos times,
    usados para casar eventos da The Odds API (que não compartilha IDs com a
    API-Football) por nome de time + horário de início."""
    home_team = aliased(Team)
    away_team = aliased(Team)

    now = datetime.now(timezone.utc)
    window_end = now + timedelta(hours=window_hours)

    stmt = (
        select(
            Fixture.id,
            Fixture.data_hora,
            home_team.nome.label("home_name"),
            away_team.nome.label("away_name"),
        )
        .join(home_team, Fixture.time_casa_id == home_team.id)
        .join(away_team, Fixture.time_fora_id == away_team.id)
        .where(
            Fixture.status == FixtureStatus.AGENDADA,
            Fixture.data_hora >= now,
            Fixture.data_hora <= window_end,
        )
    )

    result = await db.execute(stmt)
    return [
        {
            "fixture_id": row.id,
            "data_hora": row.data_hora,
            "home_name": row.home_name,
            "away_name": row.away_name,
        }
        for row in result
    ]


async def get_fixture_with_relations(db: AsyncSession, fixture_id: int) -> Fixture | None:
    stmt = (
        select(Fixture)
        .options(
            selectinload(Fixture.time_casa),
            selectinload(Fixture.time_fora),
            selectinload(Fixture.league),
        )
        .where(Fixture.id == fixture_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_finished_fixtures_for_league(
    db: AsyncSession, league_id: int, lookback_days: int = 730
) -> list[dict[str, Any]]:
    """Histórico de jogos finalizados de uma liga, usado para ajustar o modelo
    Dixon-Coles (força de ataque/defesa ponderada por recência)."""
    since = datetime.now(timezone.utc) - timedelta(days=lookback_days)

    stmt = (
        select(Fixture)
        .where(
            Fixture.liga_id == league_id,
            Fixture.status == FixtureStatus.FINALIZADA,
            Fixture.data_hora >= since,
            Fixture.placar_casa.is_not(None),
            Fixture.placar_fora.is_not(None),
        )
        .order_by(Fixture.data_hora)
    )

    result = await db.execute(stmt)
    return [
        {
            "home_id": fixture.time_casa_id,
            "away_id": fixture.time_fora_id,
            "goals_home": fixture.placar_casa,
            "goals_away": fixture.placar_fora,
            "match_date": fixture.data_hora.date(),
        }
        for fixture in result.scalars().all()
    ]


async def get_recent_finished_fixtures_for_team(
    db: AsyncSession, team_id: int, limit: int = 5
) -> list[dict[str, Any]]:
    """Últimos jogos finalizados de um time (casa ou fora), usados para resumir
    a forma recente na análise qualitativa."""
    stmt = (
        select(Fixture)
        .where(
            (Fixture.time_casa_id == team_id) | (Fixture.time_fora_id == team_id),
            Fixture.status == FixtureStatus.FINALIZADA,
            Fixture.placar_casa.is_not(None),
            Fixture.placar_fora.is_not(None),
        )
        .order_by(Fixture.data_hora.desc())
        .limit(limit)
    )

    result = await db.execute(stmt)
    fixtures = result.scalars().all()

    summaries = []
    for fixture in fixtures:
        is_home = fixture.time_casa_id == team_id
        gols_marcados = fixture.placar_casa if is_home else fixture.placar_fora
        gols_sofridos = fixture.placar_fora if is_home else fixture.placar_casa

        if gols_marcados > gols_sofridos:
            resultado = "V"
        elif gols_marcados < gols_sofridos:
            resultado = "D"
        else:
            resultado = "E"

        summaries.append(
            {
                "resultado": resultado,
                "gols_marcados": gols_marcados,
                "gols_sofridos": gols_sofridos,
                "data_hora": fixture.data_hora,
            }
        )

    return summaries
