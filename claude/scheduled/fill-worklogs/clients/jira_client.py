import logging
import os
from typing import Any

import httpx

from errors.jira_api_error import JiraApiError

logger = logging.getLogger("ops_worklogs")

HYROS_JIRA_GATEWAY_URL = "https://api.atlassian.com/ex/jira/f751a598-45b7-4258-a2c1-e839c7f1fa32"
MYSELF_PATH = "/rest/api/3/myself"
SEARCH_PATH = "/rest/api/3/search/jql"
PAGE_SIZE = 100
REQUEST_TIMEOUT_SECONDS = 20
REQUIRED_SCOPES = "read:jira-work and read:jira-user"


class JiraClient:
    def __init__(self, api_base_url: str, email: str, api_token: str) -> None:
        self.api_base_url = api_base_url.rstrip("/")
        self.email = email
        self.api_token = api_token

    @classmethod
    def from_environment(cls) -> "JiraClient":
        email = os.environ.get("ATLASSIAN_USER_EMAIL")
        api_token = os.environ.get("ATLASSIAN_API_TOKEN")
        if not email or not api_token:
            raise JiraApiError("ATLASSIAN_USER_EMAIL and ATLASSIAN_API_TOKEN must be set.")
        return cls(os.environ.get("JIRA_API_BASE_URL") or HYROS_JIRA_GATEWAY_URL, email, api_token)

    def verify_authentication(self) -> None:
        try:
            response = httpx.get(f"{self.api_base_url}{MYSELF_PATH}", auth=(self.email, self.api_token), timeout=REQUEST_TIMEOUT_SECONDS)
        except httpx.HTTPError as error:
            logger.error("Could not reach Jira at %s: %s", self.api_base_url, error)
            raise JiraApiError(f"Could not reach Jira at {self.api_base_url}: {error}") from error
        if response.is_error:
            logger.warning("Jira rejected the API token with status %s", response.status_code)
            raise JiraApiError(f"Jira rejected the API token with {response.status_code}: {response.text[:200]}. The token needs the scopes {REQUIRED_SCOPES}.")

    def search_issue_summaries(self, jql: str) -> dict[str, str]:
        summaries = {}
        next_page_token = None
        while True:
            page = self.fetch_search_page(jql, next_page_token)
            for issue in page.get("issues") or []:
                summaries[issue["key"]] = (issue.get("fields") or {}).get("summary") or ""
            next_page_token = page.get("nextPageToken")
            if not next_page_token:
                return summaries

    def fetch_search_page(self, jql: str, next_page_token: str | None) -> dict[str, Any]:
        request_body = {"jql": jql, "fields": ["summary"], "maxResults": PAGE_SIZE}
        if next_page_token:
            request_body["nextPageToken"] = next_page_token
        try:
            response = httpx.post(f"{self.api_base_url}{SEARCH_PATH}", json=request_body, auth=(self.email, self.api_token), timeout=REQUEST_TIMEOUT_SECONDS)
        except httpx.HTTPError as error:
            logger.error("Could not reach Jira at %s: %s", self.api_base_url, error)
            raise JiraApiError(f"Could not reach Jira at {self.api_base_url}: {error}") from error
        if response.is_error:
            logger.warning("Jira answered %s for the JQL %s", response.status_code, jql)
            raise JiraApiError(f"Jira answered {response.status_code}: {response.text[:300]}")
        return response.json()
