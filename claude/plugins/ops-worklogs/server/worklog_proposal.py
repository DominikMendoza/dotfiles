from datetime import date

from pydantic import BaseModel

from proposal_source import ProposalSource


class WorklogProposal(BaseModel):
    day: date
    source: ProposalSource
    card_key: str | None = None
    card_summary: str | None = None
