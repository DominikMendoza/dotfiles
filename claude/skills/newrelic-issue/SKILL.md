---
name: newrelic-issue
description: Diagnose an error reported in New Relic down to its root cause in the code. Use when given a New Relic issue link (onenr.io, one.newrelic.com), an error class or an error message from New Relic and asked to review it, explain it or find its cause; also when asked whether a fix for it is worth shipping, or to summarize it for a lead.
---

# New Relic issue

Explain an error that New Relic reports: what fails, why, how often, what it
costs, and in which branches it is already fixed. The work runs in three
stages, and each one waits for me to ask for the next:

1. **Diagnosis.** Always.
2. **Fix and verdict.** Only when I ask for the fix or whether it is worth it.
3. **Summary for the lead.** Only when I ask for it.

This is the diagnose mode of `~/.claude/CLAUDE.md`: read anything, but write to
no repo file, and run no build, compile or test. Diffs go in the reply as text.
Scratchpad files are fine.

## 1. Diagnosis

### Read New Relic

Load the New Relic tools with ToolSearch (`newrelic`) before the first call. The
account is `1337784` (Hyros New Relic).

A short link (`onenr.io`) cannot be resolved. Work from the error class and the
message fragment I give you.

Run these queries. Adjust the fragment so it matches a stable part of the
message, not an id or a date:

```sql
-- Where it happens
SELECT count(*), latest(error.message) FROM TransactionError
WHERE error.class = '<class>' AND error.message LIKE '%<fragment>%'
FACET appName, transactionName SINCE 7 days ago

-- Raw rows: full message, host, time
SELECT timestamp, error.message, host, traceId FROM TransactionError
WHERE error.class = '<class>' AND error.message LIKE '%<fragment>%'
SINCE 30 days ago LIMIT 20

-- Trend
SELECT count(*) FROM TransactionError
WHERE error.class = '<class>' AND error.message LIKE '%<fragment>%'
FACET weekOf(timestamp) SINCE 90 days ago
```

When `TransactionError` returns nothing, try `Log` with `level = 'ERROR'` and a
fragment of the message. Event retention can be shorter than the window you ask
for. Say so when you report the trend.

The full message usually holds the real input: a URL, an id, a payload. When the
message reports a position, such as "at index 237", count it and name the exact
character.

### Find the code

Search the repo for literals in the message: hosts, paths, query parameter
names, log prefixes. In zsh, quote globs: `--include='*.java'`.

### Read the code that production runs

Production runs `master`, not the local checkout. Refresh first, then read every
file of the chain from `origin/master`:

```
bb && git fetch origin master staging develop master-hotfix
git show origin/master:<path>
git grep -n "<symbol>" origin/master -- '*.java'
```

When the local code does not produce the URL or the message that New Relic
shows, the branches have diverged. Find the commit that changed it, and check
which branches carry it:

```
git log --oneline -8 -- <path>
git merge-base --is-ancestor <commit> origin/<branch> && echo yes || echo no
```

### Trace the cause

Follow the chain on `origin/master`, from the entry point to the line that
throws. Then answer:

- Which input triggers it, and where that input comes from.
- Why nothing upstream stops it.
- Whether a helper does less than its name says. Read helpers. Do not trust
  their names.
- What the caller does with the exception: retried, swallowed, returned empty,
  or surfaced to the customer.
- Whether other callers share the same weak spot.

### Report

In Spanish, in this order:

1. The cause, in two lines.
2. **Qué dice New Relic:** app, count, dates, how many accounts or hosts, the
   failing input, the exact character when there is an index.
3. **Cómo llega ahí:** the numbered chain, with `file:line` on `origin/master`.
4. **Por qué llega ese input.** Label inference as inference.
5. **Impacto:** data lost or only noise. Flag secrets that the log or the
   exception exposes, such as API keys or tokens.
6. **Estado por rama:** master, staging, develop, and the card that fixes it
   when one exists.

Never repeat a secret from the message in the reply. Cut it off, as in
`api_key=...`.

Then stop.

## 2. Fix and verdict

When I ask for it:

- Show the smallest diff that stops the error, against `master-hotfix`, as text.
  Prefer the layer that covers every caller with the weak spot. Do not change a
  shared helper that other integrations use.
- Say what happens at runtime after the fix: same result without the error, or a
  different behaviour.
- Weigh it objectively, with **A favor** and **En contra**:
  - real impact: data lost or noise,
  - frequency and trend,
  - hotfix cost: PR, review, which apps to deploy (use the `apps-to-deploy`
    skill when the repo has it),
  - conflicts with a fix that is already on its way through develop or staging,
  - new side effects, such as extra API calls or rate limits.
- End with a verdict and the conditions that would change it.

Offer to create the branch. Do not create it until I say so.

## 3. Summary for the lead

When I ask for a version to send to my lead:

- Spanish, not technical. No class names, file paths or internal jargon.
- Natural paragraphs that tell the story: what happens, the impact, the current
  state and the possible fix. No bold section labels followed by an
  explanation.
- Pros and cons as bullet lists, under `A favor de aplicarlo:` and
  `En contra:`, with `•` items.
- A closing paragraph with the recommendation and its conditions.
- No greeting and no name, so I can adapt it.
- No emojis. No em dash and no en dash.
- No secret values.

Write it to a file in the scratchpad. Check it, copy it, and confirm the copy:

```
grep -nP '[\x{2013}\x{2014}]|[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}]' <file> || echo clean
DISPLAY=:0 xclip -selection clipboard -i <file>
DISPLAY=:0 xclip -selection clipboard -o | diff -q - <file> && echo copied
```

Tell me it is in the clipboard, give the full file path, and list its parts in a
few lines. Do not paste the whole text again.
