from typing import Any


def summarize_recent_form(games: list[dict[str, Any]]) -> str | None:
    if not games:
        return None

    sequence = "-".join(game["resultado"] for game in games)
    total_marcados = sum(game["gols_marcados"] for game in games)
    total_sofridos = sum(game["gols_sofridos"] for game in games)

    return (
        f"{sequence} (últimos {len(games)} jogos: {total_marcados} gols marcados, "
        f"{total_sofridos} sofridos)"
    )


def summarize_h2h(
    matches: list[dict[str, Any]], home_team_id: int, home_name: str, away_name: str
) -> str | None:
    valid_matches = [
        m
        for m in matches
        if m.get("goals", {}).get("home") is not None and m.get("goals", {}).get("away") is not None
    ]
    if not valid_matches:
        return None

    home_wins = away_wins = draws = 0
    for match in valid_matches:
        goals_home = match["goals"]["home"]
        goals_away = match["goals"]["away"]
        match_home_id = match["teams"]["home"]["id"]
        match_away_id = match["teams"]["away"]["id"]

        if goals_home > goals_away:
            winner_id = match_home_id
        elif goals_away > goals_home:
            winner_id = match_away_id
        else:
            winner_id = None

        if winner_id is None:
            draws += 1
        elif winner_id == home_team_id:
            home_wins += 1
        else:
            away_wins += 1

    return (
        f"Últimos {len(valid_matches)} confrontos diretos: {home_wins} vitórias de "
        f"{home_name}, {draws} empates, {away_wins} vitórias de {away_name}"
    )


def summarize_injuries(injuries: list[dict[str, Any]]) -> list[str]:
    summaries = []
    for injury in injuries:
        player = injury.get("player", {})
        name = player.get("name", "Jogador não identificado")
        reason = player.get("reason") or player.get("type") or "motivo não informado"
        summaries.append(f"{name} ({reason})")
    return summaries
