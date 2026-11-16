from datetime import date, datetime, timezone

TIME_ZONE_SAFE_NOON_UTC = "T12:00:00.000Z"
ISO_DATE_LENGTH = 10


def parse_api_date(value: str | int | float) -> date:
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value / 1000, tz=timezone.utc).date()
    if len(value) == ISO_DATE_LENGTH:
        return date.fromisoformat(value)
    return datetime.fromisoformat(value).date()


def format_short_day(day: date) -> str:
    return f"{day.isoformat()}{TIME_ZONE_SAFE_NOON_UTC}"
