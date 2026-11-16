from dataclasses import dataclass
from datetime import date

from models.proposal_source import ProposalSource


@dataclass
class WorklogProposal:
    day: date
    source: ProposalSource
    card_key: str | None = None
    card_summary: str | None = None
