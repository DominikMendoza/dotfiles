# /// script
# requires-python = ">=3.11"
# dependencies = ["fastmcp>=2.10,<3", "httpx>=0.27,<1"]
# ///
import logging
import sys
from datetime import date
from typing import Any

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from api_dates import format_short_day, parse_api_date
from jira_card import JiraCard
from ops_api_client import OpsApiClient
from workday_calendar import list_workdays
from worklog_fill_planner import count_card_usage, map_descriptions_by_card, plan_worklog_fill
from worklog_proposal import WorklogProposal

logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("ops_worklogs")

DEFAULT_COUNTRY = "ARGENTINA"
MAX_DESCRIPTION_LENGTH = 1024

mcp = FastMCP("ops-worklogs")
ops_api_client = OpsApiClient.from_environment()


@mcp.tool
def list_missing_workdays() -> dict[str, Any]:
    """
    Lists the workdays of the current month, up to today, that have no OPS worklog, for every assignation OPS reports with missing days.

    Each assignation also returns its position hours, the workdays to query in Jira (logged and missing alike),
    how many times each Jira key already appears in this month's worklogs, and the description already written for each key.
    """
    today = date.today()
    logger.info("Listing missing workdays for %s", today.strftime("%Y-%m"))
    summaries = select_summaries_with_missing_days(ops_api_client.fetch_dashboard() or {})
    if not summaries:
        logger.info("OPS reports no missing workdays for %s", today.strftime("%Y-%m"))
        return {"year": today.year, "month": today.month, "assignations": []}

    country = resolve_user_country(summaries[0].get("userExternalId"))
    holiday_dates = fetch_holiday_dates(today, country)
    assignations = [describe_assignation_gaps(summary, today, holiday_dates) for summary in summaries]
    return {"year": today.year, "month": today.month, "country": country, "assignations": assignations}


@mcp.tool
def propose_worklog_fill(missing_dates: list[date], cards: list[JiraCard], card_usage_this_month: dict[str, int]) -> list[WorklogProposal]:
    """
    Picks one Jira card for each missing date and keeps repeated cards to a minimum.

    Per date it prefers an unused card active that day, then an unused card from the closest earlier day,
    then the least repeated card active that day or earlier. A date with no card on or before it comes back with source no_card.
    Each row carries the original Jira summary, and the caller writes the final description from it.
    Pass card_usage_this_month exactly as list_missing_workdays returned it.
    """
    logger.info("Proposing worklogs for %s missing dates with %s Jira cards", len(missing_dates), len(cards))
    return plan_worklog_fill(missing_dates, cards, card_usage_this_month)


@mcp.tool
def create_worklog(assignation_external_id: str, day: date, description: str, hours: int, internal_hours: int) -> dict[str, Any]:
    """
    Creates one OPS worklog, using the description as the internal description too. Call it only for a row the user approved.

    It never updates an existing worklog: OPS answers 'WorkLog already created' when the day already has one.
    """
    logger.info("Creating worklog for assignation %s on %s", assignation_external_id, day)
    trimmed_description = description.strip()
    if day > date.today():
        logger.warning("Refused a future worklog for assignation %s on %s", assignation_external_id, day)
        raise ToolError(f"{day} is in the future. Only past days and today can be filled.")
    if not trimmed_description or len(trimmed_description) > MAX_DESCRIPTION_LENGTH:
        logger.warning("Refused an empty or too long description for assignation %s on %s", assignation_external_id, day)
        raise ToolError(f"The description must have between 1 and {MAX_DESCRIPTION_LENGTH} characters.")

    payload = {
        "shortDay": format_short_day(day),
        "assignationExternalId": assignation_external_id,
        "description": trimmed_description,
        "internalDescription": trimmed_description,
        "hours": hours,
        "internalHours": internal_hours,
        "adjustmentHours": 0,
        "bonusHours": 0,
        "category": "REGULAR",
    }
    created_worklog = ops_api_client.create_worklog(payload) or {}
    logger.info("Created worklog %s for assignation %s on %s", created_worklog.get("externalId"), assignation_external_id, day)
    return {"externalId": created_worklog.get("externalId"), "day": day.isoformat(), "description": trimmed_description}


def select_summaries_with_missing_days(dashboard: dict[str, Any]) -> list[dict[str, Any]]:
    summaries = dashboard.get("missingWorklogsPerProject") or []
    return [summary for summary in summaries if (summary.get("missingDays") or 0) > 0 and summary.get("assignationExternalId")]


def resolve_user_country(user_external_id: str | None) -> str:
    if not user_external_id:
        logger.warning("OPS returned no user externalId, so holidays fall back to %s", DEFAULT_COUNTRY)
        return DEFAULT_COUNTRY
    user = ops_api_client.fetch_user(user_external_id) or {}
    return user.get("country") or DEFAULT_COUNTRY


def fetch_holiday_dates(today: date, country: str) -> set[date]:
    holidays = ops_api_client.fetch_holidays(today.month, country) or []
    holiday_dates = {parse_api_date(holiday["shortDate"]) for holiday in holidays if holiday.get("shortDate")}
    return {holiday_date for holiday_date in holiday_dates if holiday_date.year == today.year}


def describe_assignation_gaps(summary: dict[str, Any], today: date, holiday_dates: set[date]) -> dict[str, Any]:
    assignation_external_id = summary["assignationExternalId"]
    logger.info("Computing missing workdays for assignation %s", assignation_external_id)
    assignation = ops_api_client.fetch_assignation(assignation_external_id) or {}
    position = assignation.get("position") or {}
    first_day = latest_date(today.replace(day=1), assignation.get("shortStartDate"))
    last_day = earliest_date(today, assignation.get("shortEndDate"))
    paused_days = {parse_api_date(paused_day) for paused_day in ops_api_client.fetch_paused_days(assignation_external_id, today.year, today.month) or []}
    worklogs = ops_api_client.fetch_month_worklogs(assignation_external_id, today.year, today.month)
    logged_days = {parse_api_date(worklog["shortDay"]) for worklog in worklogs if worklog.get("shortDay")}
    workdays = list_workdays(first_day, last_day, holiday_dates, paused_days)
    missing_days = [workday for workday in workdays if workday not in logged_days]

    return {
        "assignationExternalId": assignation_external_id,
        "label": f"{summary.get('projectName')} - {summary.get('positionName')}",
        "externalHours": position.get("externalHours"),
        "internalHours": position.get("internalHours"),
        "missingDates": [missing_day.isoformat() for missing_day in missing_days],
        "missingDaysReportedByOps": summary.get("missingDays"),
        "workdaysToQueryInJira": [workday.isoformat() for workday in workdays],
        "cardUsageThisMonth": count_card_usage(worklog.get("description") for worklog in worklogs),
        "descriptionsByCardThisMonth": map_descriptions_by_card(worklog.get("description") for worklog in worklogs),
    }


def latest_date(boundary: date, api_value: str | int | None) -> date:
    return max(boundary, parse_api_date(api_value)) if api_value is not None else boundary


def earliest_date(boundary: date, api_value: str | int | None) -> date:
    return min(boundary, parse_api_date(api_value)) if api_value is not None else boundary


if __name__ == "__main__":
    mcp.run()
