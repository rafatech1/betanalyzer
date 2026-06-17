from datetime import datetime, timedelta, timezone

from app.services.analysis.cache_validity import is_analysis_cache_valid


def test_valid_when_fresh_and_odds_unchanged() -> None:
    now = datetime(2026, 6, 16, 12, 0, tzinfo=timezone.utc)
    created_at = now - timedelta(hours=1)

    assert is_analysis_cache_valid(
        batch_created_at=created_at,
        batch_odds={("1x2", "casa"): 2.00},
        current_odds={("1x2", "casa"): 2.00},
        ttl_hours=6,
        change_threshold=0.05,
        now=now,
    )


def test_invalid_when_older_than_ttl() -> None:
    now = datetime(2026, 6, 16, 12, 0, tzinfo=timezone.utc)
    created_at = now - timedelta(hours=7)

    assert not is_analysis_cache_valid(
        batch_created_at=created_at,
        batch_odds={("1x2", "casa"): 2.00},
        current_odds={("1x2", "casa"): 2.00},
        ttl_hours=6,
        change_threshold=0.05,
        now=now,
    )


def test_invalid_when_odd_moved_more_than_threshold() -> None:
    now = datetime(2026, 6, 16, 12, 0, tzinfo=timezone.utc)
    created_at = now - timedelta(hours=1)

    assert not is_analysis_cache_valid(
        batch_created_at=created_at,
        batch_odds={("1x2", "casa"): 2.00},
        current_odds={("1x2", "casa"): 2.20},  # +10%
        ttl_hours=6,
        change_threshold=0.05,
        now=now,
    )


def test_valid_when_odd_moved_less_than_threshold() -> None:
    now = datetime(2026, 6, 16, 12, 0, tzinfo=timezone.utc)
    created_at = now - timedelta(hours=1)

    assert is_analysis_cache_valid(
        batch_created_at=created_at,
        batch_odds={("1x2", "casa"): 2.00},
        current_odds={("1x2", "casa"): 2.04},  # +2%
        ttl_hours=6,
        change_threshold=0.05,
        now=now,
    )


def test_missing_current_odd_does_not_invalidate() -> None:
    now = datetime(2026, 6, 16, 12, 0, tzinfo=timezone.utc)
    created_at = now - timedelta(hours=1)

    assert is_analysis_cache_valid(
        batch_created_at=created_at,
        batch_odds={("1x2", "casa"): 2.00},
        current_odds={},
        ttl_hours=6,
        change_threshold=0.05,
        now=now,
    )


def test_naive_created_at_assumed_utc() -> None:
    now = datetime(2026, 6, 16, 12, 0, tzinfo=timezone.utc)
    created_at_naive = (now - timedelta(hours=1)).replace(tzinfo=None)

    assert is_analysis_cache_valid(
        batch_created_at=created_at_naive,
        batch_odds={},
        current_odds={},
        ttl_hours=6,
        change_threshold=0.05,
        now=now,
    )
