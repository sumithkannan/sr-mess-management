from datetime import date, datetime, time

from app.timeutils import APP_TIMEZONE, local_datetime, meal_window


def test_local_datetime_uses_business_timezone():
    dt = local_datetime(date(2026, 1, 1), time(8, 0))
    assert dt.tzinfo is not None
    # 08:00 IST is 02:30 UTC
    assert dt.astimezone().utcoffset().total_seconds() == 5.5 * 3600
    assert dt.utcoffset().total_seconds() == 5.5 * 3600


def test_meal_window_applies_buffer():
    start, end = meal_window(date(2026, 1, 1), time(8, 0), time(9, 0), 1)
    assert start == local_datetime(date(2026, 1, 1), time(7, 0))
    assert end == local_datetime(date(2026, 1, 1), time(10, 0))


def test_meal_window_zero_buffer_is_respected():
    start, end = meal_window(date(2026, 1, 1), time(8, 0), time(9, 0), 0)
    assert start == local_datetime(date(2026, 1, 1), time(8, 0))
    assert end == local_datetime(date(2026, 1, 1), time(9, 0))


def test_meal_window_crosses_midnight():
    start, end = meal_window(date(2026, 1, 1), time(23, 0), time(0, 30), 1)
    assert start == local_datetime(date(2026, 1, 1), time(22, 0))
    assert end == local_datetime(date(2026, 1, 2), time(1, 30))
    assert end > start
