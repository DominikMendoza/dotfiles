from datetime import date
from typing import Any

from utils.api_dates import format_short_day


def build_worklog_payload(assignation_external_id: str, day: date, description: str, hours: int, internal_hours: int) -> dict[str, Any]:
    return {
        "shortDay": format_short_day(day),
        "assignationExternalId": assignation_external_id,
        "description": description,
        "internalDescription": description,
        "hours": hours,
        "internalHours": internal_hours,
        "adjustmentHours": 0,
        "bonusHours": 0,
        "category": "REGULAR",
    }
