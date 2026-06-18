from datetime import datetime, time, timedelta, timezone

from app.routers.fixtures import BRASILIA_TZ, Period, _resolve_date_range


def test_today_range_covers_full_day_in_brasilia_time() -> None:
    # 14:30 UTC = 11:30 em Brasília (UTC-3) — ainda é "hoje" 17/06 em ambos.
    now = datetime(2026, 6, 17, 14, 30, tzinfo=timezone.utc)

    range_start, range_end = _resolve_date_range(Period.today, now)

    assert range_start == datetime(2026, 6, 17, 0, 0, tzinfo=BRASILIA_TZ)
    assert range_end == datetime(2026, 6, 17, 23, 59, 59, 999999, tzinfo=BRASILIA_TZ)


def test_today_range_uses_brasilia_date_not_utc_date() -> None:
    # 01:30 UTC = 22:30 do dia anterior em Brasília — "hoje" deve ser 16/06,
    # não 17/06 (a data UTC).
    now = datetime(2026, 6, 17, 1, 30, tzinfo=timezone.utc)

    range_start, range_end = _resolve_date_range(Period.today, now)

    assert range_start == datetime(2026, 6, 16, 0, 0, tzinfo=BRASILIA_TZ)
    assert range_end == datetime(2026, 6, 16, 23, 59, 59, 999999, tzinfo=BRASILIA_TZ)


def test_week_range_starts_at_now_not_midnight() -> None:
    # Janela deslizante: hoje quarta 17/06 às 14:30 -> mostra até terça 23/06
    # (hoje + 6 dias), não jogos já começados hoje.
    now = datetime(2026, 6, 17, 14, 30, tzinfo=timezone.utc)

    range_start, range_end = _resolve_date_range(Period.week, now)

    assert range_start == now
    assert range_end == datetime.combine(
        datetime(2026, 6, 17, tzinfo=BRASILIA_TZ).date() + timedelta(days=6),
        time.max,
        tzinfo=BRASILIA_TZ,
    )


def test_month_range_spans_29_days_ahead_from_midnight_in_brasilia_time() -> None:
    now = datetime(2026, 6, 1, 9, 0, tzinfo=timezone.utc)

    range_start, range_end = _resolve_date_range(Period.month, now)

    assert range_start == datetime(2026, 6, 1, 0, 0, tzinfo=BRASILIA_TZ)
    assert range_end == datetime(2026, 6, 30, 23, 59, 59, 999999, tzinfo=BRASILIA_TZ)
