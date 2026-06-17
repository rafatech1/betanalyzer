from datetime import datetime, timezone

from app.services.odds_matching import find_matching_fixture, normalize_team_name


def test_normalizes_accents_case_and_punctuation() -> None:
    assert normalize_team_name("São Paulo FC") == normalize_team_name("Sao Paulo Fc")


def test_matches_event_by_team_names_and_close_kickoff_time() -> None:
    fixtures = [
        {
            "fixture_id": 1,
            "data_hora": datetime(2026, 6, 20, 19, 0, tzinfo=timezone.utc),
            "home_name": "Flamengo",
            "away_name": "Palmeiras",
        }
    ]
    event = {
        "home_team": "Flamengo",
        "away_team": "Palmeiras",
        "commence_time": "2026-06-20T19:05:00Z",
    }

    assert find_matching_fixture(event, fixtures) == 1


def test_does_not_match_when_kickoff_time_too_far_apart() -> None:
    fixtures = [
        {
            "fixture_id": 1,
            "data_hora": datetime(2026, 6, 20, 19, 0, tzinfo=timezone.utc),
            "home_name": "Flamengo",
            "away_name": "Palmeiras",
        }
    ]
    event = {
        "home_team": "Flamengo",
        "away_team": "Palmeiras",
        "commence_time": "2026-06-21T19:05:00Z",
    }

    assert find_matching_fixture(event, fixtures) is None


def test_does_not_match_different_teams() -> None:
    fixtures = [
        {
            "fixture_id": 1,
            "data_hora": datetime(2026, 6, 20, 19, 0, tzinfo=timezone.utc),
            "home_name": "Flamengo",
            "away_name": "Palmeiras",
        }
    ]
    event = {
        "home_team": "Corinthians",
        "away_team": "Santos",
        "commence_time": "2026-06-20T19:00:00Z",
    }

    assert find_matching_fixture(event, fixtures) is None
