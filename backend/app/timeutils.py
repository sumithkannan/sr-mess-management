"""Timezone helpers for meal windows.

Meal start/end times are stored as naive wall-clock times that admins enter in
the mess's local timezone. Servers (for example PythonAnywhere) usually run in
UTC, so comparing those times against ``datetime.now()`` produced windows that
were off by the UTC offset. All window checks must go through these helpers.
"""

from datetime import date, datetime, time, timedelta, timezone

from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .config import settings


def _load_timezone(name: str):
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError:
        # Windows does not ship the IANA database unless `tzdata` is installed.
        # India has no DST, so a fixed offset is a safe fallback.
        if name in ("Asia/Kolkata", "Asia/Calcutta"):
            return timezone(timedelta(hours=5, minutes=30), "Asia/Kolkata")
        raise


APP_TIMEZONE = _load_timezone(settings.TIMEZONE)


def local_now() -> datetime:
    """Current time in the app's business timezone."""
    return datetime.now(APP_TIMEZONE)


def local_datetime(day: date, at: time) -> datetime:
    """Combine a local date and wall-clock time into a timezone-aware datetime."""
    return datetime.combine(day, at, tzinfo=APP_TIMEZONE)


def meal_window(day: date, start: time, end: time, buffer_hours: int = 0):
    """Return the (start, end) datetimes around a meal, in local time.

    If the meal crosses midnight (end <= start) the end is moved to the next
    day, so late-night meals are not treated as permanently closed.
    """
    start_dt = local_datetime(day, start) - timedelta(hours=buffer_hours)
    end_dt = local_datetime(day, end) + timedelta(hours=buffer_hours)
    if end_dt <= start_dt:
        end_dt += timedelta(days=1)
    return start_dt, end_dt
