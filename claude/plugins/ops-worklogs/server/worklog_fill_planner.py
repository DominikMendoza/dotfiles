import re
from collections import Counter
from collections.abc import Iterable
from datetime import date

from jira_card import JiraCard
from proposal_source import ProposalSource
from worklog_proposal import WorklogProposal

CARD_KEY_IN_DESCRIPTION = re.compile(r"\(([A-Z][A-Z0-9]+-\d+)\)")

CardChoice = tuple[JiraCard, ProposalSource]


def count_card_usage(descriptions: Iterable[str | None]) -> dict[str, int]:
    return dict(Counter(card_key for description in descriptions for card_key in CARD_KEY_IN_DESCRIPTION.findall(description or "")))


def map_descriptions_by_card(descriptions: Iterable[str | None]) -> dict[str, str]:
    descriptions_by_card = {}
    for description in descriptions:
        card_keys = CARD_KEY_IN_DESCRIPTION.findall(description or "")
        if len(card_keys) == 1:
            descriptions_by_card[card_keys[0]] = description.strip()
    return descriptions_by_card


def plan_worklog_fill(missing_dates: list[date], cards: list[JiraCard], card_usage: dict[str, int]) -> list[WorklogProposal]:
    """
    Picks one card per missing date, walking the dates in order and counting every pick as a new use.

    Per date it takes the first option that exists: an unused card active that day, an unused card
    from the closest earlier day, the least repeated card active that day or earlier, or no card.

    @param card_usage times each Jira key already appears in this month's worklogs
    @return one proposal per missing date, sorted by date
    """
    usage = Counter(card_usage)
    proposals = []
    for day in sorted(set(missing_dates)):
        choice = pick_unused_card_active_on(day, cards, usage) or pick_unused_card_from_earlier_day(day, cards, usage) or pick_least_repeated_card(day, cards, usage)
        if choice is None:
            proposals.append(WorklogProposal(day=day, source=ProposalSource.NO_CARD))
            continue
        card, source = choice
        usage[card.key] += 1
        proposals.append(WorklogProposal(day=day, source=source, card_key=card.key, card_summary=card.summary.strip()))
    return proposals


def pick_unused_card_active_on(day: date, cards: list[JiraCard], usage: Counter) -> CardChoice | None:
    candidates = [card for card in cards if usage[card.key] == 0 and day in card.active_dates]
    if not candidates:
        return None
    soonest_to_expire = min(candidates, key=lambda card: (max(card.active_dates), card.key))
    return soonest_to_expire, ProposalSource.ACTIVE_THAT_DAY


def pick_unused_card_from_earlier_day(day: date, cards: list[JiraCard], usage: Counter) -> CardChoice | None:
    candidates = [card for card in cards if usage[card.key] == 0 and last_active_date_before(card, day)]
    if not candidates:
        return None
    closest = min(candidates, key=lambda card: (-last_active_date_before(card, day).toordinal(), card.key))
    return closest, ProposalSource.UNUSED_FROM_EARLIER_DAY


def pick_least_repeated_card(day: date, cards: list[JiraCard], usage: Counter) -> CardChoice | None:
    active_that_day = [card for card in cards if day in card.active_dates]
    if active_that_day:
        return min(active_that_day, key=lambda card: (usage[card.key], card.key)), ProposalSource.REPEATED
    active_earlier = [card for card in cards if last_active_date_before(card, day)]
    if not active_earlier:
        return None
    least_repeated = min(active_earlier, key=lambda card: (usage[card.key], -last_active_date_before(card, day).toordinal(), card.key))
    return least_repeated, ProposalSource.REPEATED


def last_active_date_before(card: JiraCard, day: date) -> date | None:
    return max((active_date for active_date in card.active_dates if active_date < day), default=None)
