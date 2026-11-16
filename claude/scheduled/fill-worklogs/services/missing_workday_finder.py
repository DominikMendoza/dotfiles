import logging
from datetime import date
from typing import Any

from clients.ops_api_client import OpsApiClient
from services.worklog_fill_planner import count_card_usage, map_descriptions_by_card
from utils.api_dates import parse_api_date
from utils.workday_calendar import list_workdays

logger = logging.getLogger("ops_worklogs")

DEFAULT_COUNTRY = "ARGENTINA"


def find_missing_workdays(ops_api_client: OpsApiClient, today: date) -> dict[str, Any]:
    logger.info("Listing missing workdays for %s", today.strftime("%Y-%m"))
    summaries = select_summaries_with_missing_days(ops_api_client.fetch_dashboard() or {})
    if not summaries:
        logger.info("OPS reports no missing workdays for %s", today.strftime("%Y-%m"))
        return {"year": today.year, "month": today.month, "assignations": []}

    country = resolve_user_country(ops_api_client, summaries[0].get("userExternalId"))
    holiday_dates = fetch_holiday_dates(ops_api_client, today, country)
    assignations = [describe_assignation_gaps(ops_api_client, summary, today, holiday_dates) for summary in summaries]
    return {"year": today.year, "month": today.month, "country": country, "assignations": assignations}


def select_summaries_with_missing_days(dashboard: dict[str, Any]) -> list[dict[str, Any]]:
    summaries = dashboard.get("missingWorklogsPerProject") or []
    return [summary for summary in summaries if (summary.get("missingDays") or 0) > 0 and summary.get("assignationExternalId")]


def resolve_user_country(ops_api_client: OpsApiClient, user_external_id: str | None) -> str:
    if not user_external_id:
        logger.warning("OPS returned no user externalId, so holidays fall back to %s", DEFAULT_COUNTRY)
        return DEFAULT_COUNTRY
    user = ops_api_client.fetch_user(user_external_id) or {}
    return user.get("country") or DEFAULT_COUNTRY


def fetch_holiday_dates(ops_api_client: OpsApiClient, today: date, country: str) -> set[date]:
    holidays = ops_api_client.fetch_holidays(today.month, country) or []
    holiday_dates = {parse_api_date(holiday["shortDate"]) for holiday in holidays if holiday.get("shortDate")}
    return {holiday_date for holiday_date in holiday_dates if holiday_date.year == today.year}


def describe_assignation_gaps(ops_api_client: OpsApiClient, summary: dict[str, Any], today: date, holiday_dates: set[date]) -> dict[str, Any]:
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
