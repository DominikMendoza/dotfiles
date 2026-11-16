from enum import StrEnum


class ProposalSource(StrEnum):
    ACTIVE_THAT_DAY = "active_that_day"
    UNUSED_FROM_EARLIER_DAY = "unused_from_earlier_day"
    REPEATED = "repeated"
    NO_CARD = "no_card"
