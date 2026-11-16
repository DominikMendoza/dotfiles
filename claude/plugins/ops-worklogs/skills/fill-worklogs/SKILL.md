---
name: fill-worklogs
description: Fill the missing Ensolvers OPS worklogs of the current month from Jira progress, one card per day. Use when asked to fill, complete or catch up worklogs, work logs or hours in OPS, or to check which OPS days are missing.
model: claude-haiku-5-5
---

# Fill OPS worklogs from Jira

Talk to the user in their language. Nothing is written to OPS until the user
approves the table in step 3.

## 1. Find the gaps

Call `list_missing_workdays`.

- `assignations` is empty: tell the user nothing is missing this month and stop.
- More than one assignation: ask which one to fill and continue with that one only.
- The length of `missingDates` differs from `missingDaysReportedByOps`: show both
  numbers under the table. OPS may count a day this tool cannot see.

## 2. Read the Jira progress

Use only `mcp__atlassian__searchJiraIssuesUsingJql`, with
`cloudId: "markethero.atlassian.net"`. Never use the
`mcp__claude_ai_Atlassian__*` tools: that connector has no access to the Hyros
site. When `mcp__atlassian__searchJiraIssuesUsingJql` is missing or answers
that the site is not granted, stop and tell the user to add it and sign in with
the Hyros account in `/mcp`:

```
claude mcp add --scope user --transport http atlassian https://mcp.atlassian.com/v2/mcp
```

Run this JQL once for every date in `workdaysToQueryInJira`, with
`fields: ["summary"]`, all dates in parallel:

```
assignee WAS currentUser() ON "<date>" AND status WAS IN ("In Progress", "Code Review") ON "<date>"
```

Merge the results into one card per key: `key`, `summary`, and `active_dates`
with every date that returned the key.

## 3. Propose and wait

Call `propose_worklog_fill` with `missingDates`, the merged cards, and
`cardUsageThisMonth`. Keep its choices: do not reorder or replace them yourself.

Write the description of every row that has a card:

- When `descriptionsByCardThisMonth` has the key, reuse that text exactly.
- Otherwise rewrite `card_summary` as a short natural phrase, the way a person
  says what they worked on, and append ` (<KEY>)`:
  - 3 to 7 words, in English, no final period.
  - Uppercase only the first word. Every other word is lowercase, product
    names included.
  - No `:`, no separator dashes (` - `, `–`, `—`), no arrows (`->`, `→`), no
    `|`, `/`, brackets or quotes. The ` (<KEY>)` at the end is the only symbol.
  - Drop the prefix before `:` or ` - ` (project, platform, area,
    `Maintenance`), trailing explanations, dates, and code names such as class
    or endpoint names.
  - Keep the platform only when the phrase means nothing without it.
  - A title that describes a problem becomes the fix in plain words. Do not
    add details the title does not support.
- The same key keeps the same text on every day.

Examples:

| Jira title | Description |
| --- | --- |
| Maintenance: investigate PayPal legacy buttons deprecation and evaluate Hyros' ability of performing tracking with the new ones | PayPal legacy buttons deprecation (HD-5231) |
| Shopify: Expiring offline access tokens required for all public apps as of January 1, 2027 | Shopify expiring offline access tokens (HD-5201) |
| BigCommerce: process refunds by items | Process refunds by items (HMA-8767) |
| AIR Sales and Calls - Add loading animation | Add loading animation to sales and calls (HAT-1011) |
| Dynamic OpenRouter providers blacklist | Dynamic openrouter providers blacklist (HAT-1044) |
| BigCommerce - Partial refund is taken as Full refund | Fix partial refunds taken as full (HMA-8680) |
| 100% error rate in GoogleSheetsIntegrationResource/uploadCSV | Fix google sheets csv upload errors (HMA-6709) |

Follow the tone of `descriptionsByCardThisMonth` and of these texts the user
wrote: `Show loading skeleton`, `Ignore cloudflare provider in openrouter
routing`, `Format air kpi variation by browser locale`, `Block sheets upload
without a selected account`.

Show one table and stop:

| Day | Description | Jira title | Hours | Source |
| --- | ----------- | ---------- | ----- | ------ |

- Day as `Mon 16 Nov`.
- Hours as `externalHours` / `internalHours`.
- Source, translated to the user's language:
  - `active_that_day`: card active that day
  - `unused_from_earlier_day`: unused card from an earlier day
  - `repeated`: repeated, no unused card left
  - `no_card`: no Jira card, the user writes it

Wait for the user's approval. Apply every edit they give, row by row.

## 4. Create

Only after the approval, call `create_worklog` once per approved row, one row at
a time, with the description shown in the table, the assignation's
`externalHours` as `hours` and `internalHours` as `internal_hours`. Skip rows
that still have no description.

Then report the created rows, and the failed rows with the message OPS gave.
`WorkLog already created` means the day was filled meanwhile: report it as
skipped. Never retry on your own, and never change an existing worklog.
