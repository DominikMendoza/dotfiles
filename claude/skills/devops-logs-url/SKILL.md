---
name: devops-logs-url
description: Build a devops.hyros.com Log Insights link for a CloudWatch query. Use when asked for a URL, a link or direct access to a log query, to share a Logs Insights query, or to open in the devops app a query run with the hyros-devops MCP. Never answer with an AWS console link.
---

# Devops logs URL

Turn a CloudWatch Logs Insights query into a link to the devops app, with its
results already loaded. Never build an AWS console link.

## URL format

Two forms. A window that ends now, or a fixed range:

```
https://devops.hyros.com/tools/log-insights?groups=<group>&window=<minutes>&run=<run id>&q=<query>
https://devops.hyros.com/tools/log-insights?groups=<group>&run=<run id>&q=<query>&from=<start>&to=<end>
```

| Param       | Value                                                                  |
| ----------- | ---------------------------------------------------------------------- |
| `groups`    | Exact log group, such as `HYROS-PROD-AIR-PROCESSING`. One per link.    |
| `window`    | Minutes, ending now. Only in the first form.                           |
| `run`       | Id of a finished run. Required.                                        |
| `q`         | The query. Its first line is the `SOURCE` line below.                  |
| `from`/`to` | UTC, `2026-11-16T13:31:09.000Z`. Only in the second form, with no `window`. |

The `SOURCE` line of `q` matches the form:

```
SOURCE '<group>' START=-<minutes>m END=0s
SOURCE '<group>' START="2026-11-16T13:31:09.000Z" END="2026-11-16T14:01:09.000Z"
```

`q` is form encoded: space as `+`, `*` kept raw, every other symbol as `%XX`.
Do not encode it by hand. `build_url.py` does it, converts `--from`/`--to` to
UTC, and adds the `SOURCE` line when the query has none.

Use a fixed range when I ask for one, or when the link records something that
already happened and will be opened later, such as evidence for a card. A
window that ends now moves, and the events fall out of it.

## Steps

1. **Query.** Reuse the query already run in this conversation when there is
   one. Otherwise write it the way `logs_context` says: filter on the literal
   text of the log line, grepped from the code.
2. **Group.** `HYROS-PROD-*` is master, `HYROS-QA-*` is staging. When I do not
   say which, ask.
3. **Run id.** Load the tools with ToolSearch
   (`select:mcp__hyros-devops__logs_context,mcp__hyros-devops__logs_run,mcp__hyros-devops__logs_get`).
   Call `logs_context` once per task, then `logs_run` with `groups`, the query
   without the `SOURCE` line, and either `since: "<minutes>m"` or `from` and
   `to` in ISO 8601 with my offset (`date +%z`). Its `id` is the run. When its
   status is not `COMPLETE`, call `logs_get` with that id until it is.
   The MCP and the app share runs, so an id from an earlier run in this
   conversation, with the same query and window or range, also works, and so
   does an id I paste.
4. **URL and clipboard.** One command. Pass `--window <minutes>` for a window
   that ends now, or `--from <start> --to <end>` for a fixed range, with the
   same values the run used:

   ```
   url=$(python3 -I ~/.claude/skills/devops-logs-url/build_url.py --group <group> --window <minutes> --run <id> <<'EOF'
   <query>
   EOF
   ) && printf '%s' "$url" | DISPLAY=:0 xclip -selection clipboard -i && echo "$url"
   ```

## Reply

In Spanish, and short:

- The URL, in a code block.
- One line: group, window or fixed range, records matched, and that the URL
  is in the clipboard.

No results table unless I ask for the results.
