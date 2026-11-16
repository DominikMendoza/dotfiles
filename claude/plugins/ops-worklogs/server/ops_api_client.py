import logging
import os
from pathlib import Path
from typing import Any

import httpx

from ops_api_error import OpsApiError

logger = logging.getLogger("ops_worklogs")

DEFAULT_BASE_URL = "https://ops-api.ensolvers.com"
DEFAULT_TOKEN_FILE = Path.home() / ".config" / "ensolvers-ops" / "jwt"
REQUEST_TIMEOUT_SECONDS = 20
MAX_WORKLOGS_IN_A_MONTH = 31
REJECTED_TOKEN_STATUSES = {401, 403}


class OpsApiClient:
    def __init__(self, base_url: str, token_file: Path) -> None:
        self.base_url = base_url.rstrip("/")
        self.token_file = token_file

    @classmethod
    def from_environment(cls) -> "OpsApiClient":
        base_url = os.environ.get("OPS_API_BASE_URL") or DEFAULT_BASE_URL
        token_file = Path(os.environ.get("OPS_JWT_FILE") or DEFAULT_TOKEN_FILE).expanduser()
        return cls(base_url, token_file)

    def fetch_dashboard(self) -> dict[str, Any] | None:
        return self.send("GET", "/ensolvers-users/get-dashboard")

    def fetch_user(self, user_external_id: str) -> dict[str, Any] | None:
        return self.send("GET", f"/ensolvers-users/{user_external_id}")

    def fetch_assignation(self, assignation_external_id: str) -> dict[str, Any] | None:
        return self.send("GET", f"/ensolvers-ops/assignation/{assignation_external_id}")

    def fetch_holidays(self, month: int, country: str) -> list[dict[str, Any]] | None:
        return self.send("GET", f"/ensolvers-ops/holiday/month/{month}", params={"country": country})

    def fetch_paused_days(self, assignation_external_id: str, year: int, month: int) -> list[Any] | None:
        zero_based_month = month - 1
        params = {"assignationExternalId": assignation_external_id, "year": year, "month": zero_based_month}
        return self.send("GET", "/ensolvers-ops/assignation-pause/paused-days", params=params)

    def fetch_month_worklogs(self, assignation_external_id: str, year: int, month: int) -> list[dict[str, Any]]:
        zero_based_month = month - 1
        params = {"assignationExternalId": assignation_external_id, "year": year, "month": zero_based_month, "page": 0, "pageSize": MAX_WORKLOGS_IN_A_MONTH}
        page = self.send("GET", "/ensolvers-ops/work-log/filter", params=params) or {}
        return page.get("content") or []

    def create_worklog(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        return self.send("POST", "/ensolvers-ops/work-log", json=payload)

    def send(self, method: str, path: str, **request_options: Any) -> Any:
        headers = {"Authorization": f"Bearer {self.read_token()}", "Accept": "application/json"}
        try:
            response = httpx.request(method, f"{self.base_url}{path}", headers=headers, timeout=REQUEST_TIMEOUT_SECONDS, **request_options)
        except httpx.HTTPError as error:
            logger.error("Could not reach OPS on %s %s: %s", method, path, error)
            raise OpsApiError(f"Could not reach OPS at {self.base_url}: {error}") from error

        if response.status_code in REJECTED_TOKEN_STATUSES:
            logger.warning("OPS rejected the token with status %s on %s %s", response.status_code, method, path)
            raise OpsApiError(f"OPS answered {response.status_code}. The token may be expired: copy a fresh one from the localStorage key 't' on ops.ensolvers.com into {self.token_file}.")

        body = parse_body(response)
        if response.is_error or (isinstance(body, dict) and body.get("success") is False):
            message = extract_error_message(body, response.status_code)
            logger.warning("OPS answered %s on %s %s: %s", response.status_code, method, path, message)
            raise OpsApiError(message)

        return body.get("content") if isinstance(body, dict) else body

    def read_token(self) -> str:
        try:
            raw_token = self.token_file.read_text()
        except FileNotFoundError as error:
            logger.warning("Token file %s does not exist", self.token_file)
            raise OpsApiError(f"Token file {self.token_file} does not exist. Save your OPS JWT there with chmod 600.") from error

        token = raw_token.strip().strip('"').removeprefix("Bearer ").strip()
        if not token:
            logger.warning("Token file %s is empty", self.token_file)
            raise OpsApiError(f"Token file {self.token_file} is empty.")
        return token


def parse_body(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return response.text


def extract_error_message(body: Any, status_code: int) -> str:
    if isinstance(body, dict):
        return str(body.get("message") or body.get("errorCode") or f"HTTP {status_code}")
    return str(body).strip()[:300] or f"HTTP {status_code}"
