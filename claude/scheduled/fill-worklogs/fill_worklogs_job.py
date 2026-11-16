# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx>=0.27,<1"]
# ///
import logging
import sys
from datetime import date
from typing import Any

from clients.jira_client import JiraClient
from clients.ops_api_client import OpsApiClient
from clients.worklog_title_writer import WorklogTitleWriter
from errors.ops_api_error import OpsApiError
from models.jira_card import JiraCard
from models.worklog_proposal import WorklogProposal
from services.jira_progress import collect_active_cards
from services.missing_workday_finder import find_missing_workdays
from services.worklog_fill_planner import plan_worklog_fill
from utils.worklog_payload import build_worklog_payload

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("ops_worklogs")

ALREADY_CREATED_MESSAGE = "WorkLog already created"


def main(arguments: list[str]) -> int:
    dry_run = "--dry-run" in arguments
    today = date.today()
    logger.info("Starting the worklog fill for %s with dry run %s", today, dry_run)
    try:
        return fill_missing_worklogs(today, dry_run)
    except Exception:
        logger.exception("The worklog fill for %s stopped on an unexpected error", today)
        return 1


def fill_missing_worklogs(today: date, dry_run: bool) -> int:
    ops_api_client = OpsApiClient.from_environment()
    assignations = find_missing_workdays(ops_api_client, today)["assignations"]
    if not assignations:
        logger.info("Nothing to fill for %s", today.strftime("%Y-%m"))
        return 0
    if len(assignations) > 1:
        logger.warning("Found %s assignations with missing days, so nothing was filled", len(assignations))
        return 1

    assignation = assignations[0]
    missing_dates = [date.fromisoformat(value) for value in assignation["missingDates"]]
    if not missing_dates:
        logger.warning("OPS reports %s missing days for assignation %s, but none of them is a workday this tool can see", assignation["missingDaysReportedByOps"], assignation["assignationExternalId"])
        return 0

    workdays = [date.fromisoformat(value) for value in assignation["workdaysToQueryInJira"]]
    cards = collect_active_cards(JiraClient.from_environment(), workdays)
    proposals = plan_worklog_fill(missing_dates, cards, assignation["cardUsageThisMonth"])
    descriptions_by_card = complete_descriptions_by_card(proposals, cards, assignation["descriptionsByCardThisMonth"])
    return create_proposed_worklogs(ops_api_client, assignation, proposals, descriptions_by_card, dry_run)


def complete_descriptions_by_card(proposals: list[WorklogProposal], cards: list[JiraCard], existing_descriptions: dict[str, str]) -> dict[str, str]:
    descriptions_by_card = dict(existing_descriptions)
    proposed_keys = {proposal.card_key for proposal in proposals if proposal.card_key}
    cards_to_describe = [card for card in cards if card.key in proposed_keys and card.key not in descriptions_by_card]
    if cards_to_describe:
        written_titles = WorklogTitleWriter.from_environment().write_titles(cards_to_describe, list(existing_descriptions.values()))
        descriptions_by_card.update({card_key: f"{title} ({card_key})" for card_key, title in written_titles.items()})
    return descriptions_by_card


def create_proposed_worklogs(ops_api_client: OpsApiClient, assignation: dict[str, Any], proposals: list[WorklogProposal], descriptions_by_card: dict[str, str], dry_run: bool) -> int:
    assignation_external_id = assignation["assignationExternalId"]
    failed_days = 0
    for proposal in proposals:
        description = descriptions_by_card.get(proposal.card_key) if proposal.card_key else None
        if not description:
            logger.warning("No Jira card was active on or before %s for assignation %s, so the day stays empty", proposal.day, assignation_external_id)
            continue
        if dry_run:
            logger.info("Would create %s on %s for assignation %s, chosen as %s", description, proposal.day, assignation_external_id, proposal.source)
            continue

        payload = build_worklog_payload(assignation_external_id, proposal.day, description, assignation["externalHours"], assignation["internalHours"])
        try:
            created_worklog = ops_api_client.create_worklog(payload) or {}
            logger.info("Created worklog %s on %s for assignation %s with %s", created_worklog.get("externalId"), proposal.day, assignation_external_id, description)
        except OpsApiError as error:
            if ALREADY_CREATED_MESSAGE in str(error):
                logger.info("Skipped %s for assignation %s because the day already has a worklog", proposal.day, assignation_external_id)
                continue
            logger.error("Could not create the worklog on %s for assignation %s: %s", proposal.day, assignation_external_id, error)
            failed_days += 1
    return 1 if failed_days else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
