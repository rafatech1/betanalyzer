from datetime import date

from app.services.external.api_football import current_season


def test_season_for_date_in_second_half_of_year_is_same_year() -> None:
    assert current_season(date(2025, 9, 15)) == 2025


def test_season_for_date_in_first_half_of_year_is_previous_year() -> None:
    assert current_season(date(2026, 3, 1)) == 2025


def test_season_boundary_in_july_rolls_to_current_year() -> None:
    assert current_season(date(2025, 7, 1)) == 2025
    assert current_season(date(2025, 6, 30)) == 2024
