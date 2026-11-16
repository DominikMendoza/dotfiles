from datetime import date, timedelta

SATURDAY = 5


def list_workdays(first_day: date, last_day: date, holiday_dates: set[date], paused_days: set[date]) -> list[date]:
    workdays = []
    day = first_day
    while day <= last_day:
        if day.weekday() < SATURDAY and day not in holiday_dates and day not in paused_days:
            workdays.append(day)
        day += timedelta(days=1)
    return workdays
