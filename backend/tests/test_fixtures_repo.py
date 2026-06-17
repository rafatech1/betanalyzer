from app.models.fixture import FixtureStatus
from app.services.fixtures_repo import map_fixture_status


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
