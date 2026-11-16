from dataclasses import dataclass
from datetime import date


@dataclass
class JiraCard:
    key: str
    summary: str
    active_dates: list[date]
