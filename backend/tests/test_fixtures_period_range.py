from datetime import datetime, time, timedelta, timezone

from app.routers.fixtures import Period, _resolve_date_range


def test_today_range_starts_at_now_not_midnight() -> None:
    now = datetime(2026, 6, 17, 14, 30, tzinfo=timezone.utc)

    range_start, range_end = _resolve_date_range(Period.today, now)

    assert range_start == now
    assert range_end == datetime.combine(now.date(), time.max, tzinfo=timezone.utc)


def test_week_range_starts_at_now_not_midnight() -> None:
    # Janela deslizante: hoje quarta 17/06 às 14:30 -> mostra até terça 23/06
    # (hoje + 6 dias), não jogos já começados hoje.
    now = datetime(2026, 6, 17, 14, 30, tzinfo=timezone.utc)

    range_start, range_end = _resolve_date_range(Period.week, now)

    assert range_start == now
    assert range_end == datetime.combine(
        now.date() + timedelta(days=6), time.max, tzinfo=timezone.utc
    )


def test_month_range_spans_29_days_ahead_from_midnight() -> None:
    now = datetime(2026, 6, 1, 9, 0, tzinfo=timezone.utc)

    range_start, range_end = _resolve_date_range(Period.month, now)

    assert range_start == datetime.combine(now.date(), time.min, tzinfo=timezone.utc)
    assert range_end == datetime(2026, 6, 30, 23, 59, 59, 999999, tzinfo=timezone.utc)
