import logging
from collections import defaultdict
from datetime import date

from clients.jira_client import JiraClient
from models.jira_card import JiraCard

logger = logging.getLogger("ops_worklogs")

ACTIVE_ON_DAY_JQL = 'assignee WAS currentUser() ON "{day}" AND status WAS IN ("In Progress", "Code Review") ON "{day}"'


def collect_active_cards(jira_client: JiraClient, workdays: list[date]) -> list[JiraCard]:
    logger.info("Reading Jira progress for %s workdays", len(workdays))
    jira_client.verify_authentication()
    active_dates_by_key = defaultdict(list)
    summaries_by_key = {}
    for workday in workdays:
        for card_key, summary in jira_client.search_issue_summaries(ACTIVE_ON_DAY_JQL.format(day=workday.isoformat())).items():
            active_dates_by_key[card_key].append(workday)
            summaries_by_key[card_key] = summary
    return [JiraCard(key=card_key, summary=summaries_by_key[card_key], active_dates=active_dates) for card_key, active_dates in active_dates_by_key.items()]
