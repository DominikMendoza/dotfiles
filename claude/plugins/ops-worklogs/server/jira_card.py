from datetime import date

from pydantic import BaseModel, Field


class JiraCard(BaseModel):
    key: str = Field(description="Jira issue key, for example HMA-8767")
    summary: str = Field(description="Jira issue summary")
    active_dates: list[date] = Field(description="Every date the issue was assigned to the user and in In Progress or Code Review")
