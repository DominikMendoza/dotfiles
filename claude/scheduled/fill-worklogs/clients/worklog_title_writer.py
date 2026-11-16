import json
import logging
import os
import re
from typing import Any

import httpx

from errors.title_writer_error import TitleWriterError
from models.jira_card import JiraCard

logger = logging.getLogger("ops_worklogs")

DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "anthropic/claude-haiku-5.5"
DEFAULT_API_KEY_VARIABLE = "OPENROUTER_API_KEY"
REQUEST_TIMEOUT_SECONDS = 90
TRAILING_CARD_KEY = re.compile(r"\s*\([A-Z][A-Z0-9]+-\d+\)\s*$")

TITLE_RULES = """You turn Jira issue titles into short worklog descriptions, written the way a person says what they worked on.

Rules for every description:
- 3 to 7 words, in English, no final period.
- Uppercase only the first word. Every other word is lowercase, product names included.
- No ":", no separator dashes (" - ", "–", "—"), no arrows ("->", "→"), no "|", "/", brackets or quotes.
- Drop the prefix before ":" or " - " (project, platform, area, "Maintenance"), trailing explanations, dates, and code names such as class or endpoint names.
- Keep the platform only when the phrase means nothing without it.
- A title that describes a problem becomes the fix in plain words. Do not add details the title does not support.
- Do not include the issue key.

Examples, as Jira title => description:
- Maintenance: investigate PayPal legacy buttons deprecation and evaluate Hyros' ability of performing tracking with the new ones => PayPal legacy buttons deprecation
- Shopify: Expiring offline access tokens required for all public apps as of January 1, 2027 => Shopify expiring offline access tokens
- BigCommerce: process refunds by items => Process refunds by items
- AIR Sales and Calls - Add loading animation => Add loading animation to sales and calls
- Dynamic OpenRouter providers blacklist => Dynamic openrouter providers blacklist
- BigCommerce - Partial refund is taken as Full refund => Fix partial refunds taken as full
- 100% error rate in GoogleSheetsIntegrationResource/uploadCSV => Fix google sheets csv upload errors

Follow the tone of the descriptions the user already wrote, when the input lists them.
Return exactly one description for every issue key you receive."""

DESCRIPTIONS_SCHEMA = {
    "type": "object",
    "properties": {
        "descriptions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"key": {"type": "string"}, "description": {"type": "string"}},
                "required": ["key", "description"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["descriptions"],
    "additionalProperties": False,
}


class WorklogTitleWriter:
    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    @classmethod
    def from_environment(cls) -> "WorklogTitleWriter":
        api_key_variable = os.environ.get("WORKLOG_LLM_API_KEY_VARIABLE") or DEFAULT_API_KEY_VARIABLE
        api_key = os.environ.get(api_key_variable)
        if not api_key:
            raise TitleWriterError(f"{api_key_variable} is not set.")
        return cls(os.environ.get("WORKLOG_LLM_BASE_URL") or DEFAULT_BASE_URL, api_key, os.environ.get("WORKLOG_LLM_MODEL") or DEFAULT_MODEL)

    def write_titles(self, cards: list[JiraCard], tone_examples: list[str]) -> dict[str, str]:
        logger.info("Writing worklog titles for %s Jira cards with %s", len(cards), self.model)
        issues = [{"key": card.key, "title": card.summary} for card in cards]
        request_body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": TITLE_RULES},
                {"role": "user", "content": json.dumps({"issues": issues, "descriptionsAlreadyWritten": tone_examples}, ensure_ascii=False)},
            ],
            "response_format": {"type": "json_schema", "json_schema": {"name": "worklog_descriptions", "strict": True, "schema": DESCRIPTIONS_SCHEMA}},
        }
        try:
            response = httpx.post(f"{self.base_url}/chat/completions", headers={"Authorization": f"Bearer {self.api_key}"}, json=request_body, timeout=REQUEST_TIMEOUT_SECONDS)
        except httpx.HTTPError as error:
            raise TitleWriterError(f"Could not reach {self.base_url}: {error}") from error
        if response.is_error:
            raise TitleWriterError(f"{self.base_url} answered {response.status_code}: {response.text[:300]}")

        written_titles = parse_written_titles(response.json())
        missing_keys = [card.key for card in cards if not written_titles.get(card.key)]
        if missing_keys:
            raise TitleWriterError(f"The model returned no title for {', '.join(missing_keys)}.")
        return {card.key: written_titles[card.key] for card in cards}


def parse_written_titles(completion: dict[str, Any]) -> dict[str, str]:
    try:
        content = completion["choices"][0]["message"]["content"]
        descriptions = json.loads(content)["descriptions"]
    except (KeyError, IndexError, TypeError, ValueError) as error:
        raise TitleWriterError(f"The model answer is not the expected JSON: {error}") from error
    return {item["key"]: clean_title(item["description"]) for item in descriptions if item.get("key") and item.get("description")}


def clean_title(title: str) -> str:
    return TRAILING_CARD_KEY.sub("", title).strip().rstrip(".").strip()
