from app.services.analysis.qualitative_data import (
    summarize_h2h,
    summarize_injuries,
    summarize_recent_form,
)


def test_summarize_recent_form_returns_none_when_empty() -> None:
    assert summarize_recent_form([]) is None


def test_summarize_recent_form_builds_sequence_and_goal_totals() -> None:
    games = [
        {"resultado": "V", "gols_marcados": 2, "gols_sofridos": 0},
        {"resultado": "E", "gols_marcados": 1, "gols_sofridos": 1},
        {"resultado": "D", "gols_marcados": 0, "gols_sofridos": 2},
    ]

    summary = summarize_recent_form(games)

    assert summary is not None
    assert "V-E-D" in summary
    assert "3 gols marcados" in summary
    assert "3 sofridos" in summary


def test_summarize_h2h_returns_none_when_no_valid_matches() -> None:
    assert summarize_h2h([], home_team_id=1, home_name="A", away_name="B") is None


def test_summarize_h2h_counts_wins_relative_to_home_team() -> None:
    matches = [
        {"goals": {"home": 2, "away": 0}, "teams": {"home": {"id": 1}, "away": {"id": 2}}},
        {"goals": {"home": 1, "away": 1}, "teams": {"home": {"id": 2}, "away": {"id": 1}}},
        {"goals": {"home": 0, "away": 3}, "teams": {"home": {"id": 1}, "away": {"id": 2}}},
    ]

    summary = summarize_h2h(matches, home_team_id=1, home_name="Flamengo", away_name="Palmeiras")

    assert summary is not None
    assert "1 vitórias de Flamengo" in summary
    assert "1 empates" in summary
    assert "1 vitórias de Palmeiras" in summary


def test_summarize_injuries_formats_player_and_reason() -> None:
    injuries = [{"player": {"name": "Gabigol", "reason": "lesão muscular"}}]

    assert summarize_injuries(injuries) == ["Gabigol (lesão muscular)"]


def test_summarize_injuries_handles_missing_fields() -> None:
    assert summarize_injuries([{"player": {}}]) == [
        "Jogador não identificado (motivo não informado)"
    ]
