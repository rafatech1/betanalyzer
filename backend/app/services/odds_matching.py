import unicodedata
from datetime import datetime, timezone
from typing import Any

DEFAULT_MAX_KICKOFF_DIFF_HOURS = 3


def normalize_team_name(name: str) -> str:
    decomposed = unicodedata.normalize("NFKD", name)
    ascii_only = "".join(char for char in decomposed if not unicodedata.combining(char))
    return "".join(char for char in ascii_only.lower() if char.isalnum())


def _parse_commence_time(raw: str) -> datetime:
    return datetime.fromisoformat(raw.replace("Z", "+00:00"))


def find_matching_fixture(
    event: dict[str, Any],
    fixtures: list[dict[str, Any]],
    max_kickoff_diff_hours: int = DEFAULT_MAX_KICKOFF_DIFF_HOURS,
) -> int | None:
    """Casa um evento da The Odds API a um fixture já persistido, comparando
    nomes de times normalizados e tolerância de horário — as duas APIs não
    compartilham um identificador comum."""
    home = normalize_team_name(event.get("home_team", ""))
    away = normalize_team_name(event.get("away_team", ""))
    commence_time = _parse_commence_time(event["commence_time"])

    for fixture in fixtures:
        data_hora = fixture["data_hora"]
        if data_hora.tzinfo is None:
            data_hora = data_hora.replace(tzinfo=timezone.utc)

        if (
            normalize_team_name(fixture["home_name"]) == home
            and normalize_team_name(fixture["away_name"]) == away
            and abs((data_hora - commence_time).total_seconds())
            <= max_kickoff_diff_hours * 3600
        ):
            return fixture["fixture_id"]

    return None
