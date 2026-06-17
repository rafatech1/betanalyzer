from datetime import timezone

from app.models.fixture import FixtureStatus
from app.services.fixtures_repo import (
    _league_info_from_sport_key,
    _parse_commence_time,
    map_fixture_status,
)


def test_maps_not_started_to_agendada() -> None:
    assert map_fixture_status("NS") == FixtureStatus.AGENDADA


def test_maps_in_progress_codes_to_em_andamento() -> None:
    for code in ("1H", "HT", "2H", "ET", "LIVE"):
        assert map_fixture_status(code) == FixtureStatus.EM_ANDAMENTO


def test_maps_finished_codes_to_finalizada() -> None:
    for code in ("FT", "AET", "PEN"):
        assert map_fixture_status(code) == FixtureStatus.FINALIZADA


def test_maps_postponed_to_postergada() -> None:
    assert map_fixture_status("PST") == FixtureStatus.POSTERGADA


def test_maps_cancelled_codes_to_cancelada() -> None:
    for code in ("CANC", "ABD", "AWD", "WO"):
        assert map_fixture_status(code) == FixtureStatus.CANCELADA


def test_unknown_code_defaults_to_agendada() -> None:
    assert map_fixture_status("???") == FixtureStatus.AGENDADA


def test_known_sport_key_returns_mapped_label() -> None:
    assert _league_info_from_sport_key("soccer_brazil_campeonato") == (
        "Brasileirão Série A",
        "Brasil",
    )


def test_unknown_sport_key_falls_back_to_derived_label() -> None:
    nome, pais = _league_info_from_sport_key("soccer_some_new_league")
    assert nome == "Some New League"
    assert pais == "Desconhecido"


def test_parse_commence_time_handles_zulu_suffix() -> None:
    parsed = _parse_commence_time("2026-03-01T18:00:00Z")
    assert parsed.tzinfo is not None
    assert parsed.astimezone(timezone.utc).hour == 18
