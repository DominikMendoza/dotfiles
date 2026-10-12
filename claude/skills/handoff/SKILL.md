---
name: handoff
description: Prepare the delivery of a finished card, with a Slack message and an English and Spanish summary to paste into the Jira card. Use when asked to hand off a card, to wrap up a feature, or to write the Slack message or the Jira summary for work that is done.
---

# Handoff

Turn a finished card into three texts, built from the current session and the
branch:

- a short Slack message, in English, that the skill sends after I approve it,
- a Jira summary in English, for me to paste into the card,
- the same Jira summary in Spanish, also for me to paste.

Nothing reaches Slack until I approve the exact text. Nothing is posted to Jira
by the skill.

## 1. Gather

Read all of this before writing anything.

- **Branch and card key.** `git branch --show-current`. The key is the prefix,
  such as `HAT-865`. When the branch carries no key, ask for the card.
- **Card.** Read it through the Atlassian connector: summary, description and
  acceptance criteria. When the connector is not available, go on without it and
  say so.
- **Base.** `develop`, `staging` or `master-hotfix`. When I did not say which,
  use `staging`.
- **Commits and scope.** Against the base chosen above, after refreshing it.

  ```
  bb && git fetch origin staging
  git log --oneline origin/staging..HEAD
  git diff --stat origin/staging...HEAD
  ```

- **This session.** Go through the conversation so far: what was asked, what was
  decided and why, approaches that were discarded, open questions, and anything
  left out of scope on purpose. This is the part a diff cannot tell.

## 2. Check the branch is ready

Stop at the first item that fails, give me the command, and wait.

1. **Uncommitted changes.** `git status --porcelain`. When anything is listed,
   give me the commit command, following the commit rules in
   `~/.claude/CLAUDE.md`. Do not commit.
2. **Not pushed.** Compare with the remote. When the branch has no upstream or is
   ahead of it, give me the push command. Do not push.

   ```
   bb && git push --set-upstream origin HAT-865-fix-tracking-pixel-order
   ```

## 3. Ask for the links

Ask in a single message for:

- the pull request link,
- the video link,
- the Slack channel or person, unless I already said it in this session.

When I have no video for this card, leave the video line out of every text.

## 4. Draft the Slack message

In English, short enough to read in Slack without expanding it. Use Slack
formatting: `*bold*`, plain `-` bullets, bare links.

```
*HAT-865: Fix tracking pixel on the order page*

The pixel now fires after the order is confirmed instead of on page load, so
abandoned checkouts no longer count as sales.

- Moved the pixel call into the confirmation handler
- Added a guard for orders without a customer id
- Not included: the retroactive fix for past orders, tracked in HAT-870

PR: <link>
Video: <link>
Notes for review: the guard logs a warning with the orderId when it skips.
```

Rules for the content:

- The opening sentence says what changes for the user or the system, not which
  files moved.
- Bullets come from the session and the diff together. Name decisions a
  reviewer would ask about.
- Say what was left out on purpose and where it went.
- No mention of how the work was produced, no tool names, no attribution line.
- Keep it under about 12 lines. Drop the "Notes for review" line when there is
  nothing a reviewer must know.

## 5. Draft the Jira summary

Two separate texts with the same content: one in English, one in Spanish. The
Spanish one is a natural rewrite, not a word by word translation. Keep code,
identifiers, class names, endpoints and log messages unchanged in both.

Write them in Markdown, which the Jira editor turns into rich text on paste:
`**bold**`, `` `inline code` ``, fenced code blocks with a language, `-` lists
and `###` headings. Do not use Jira wiki markup such as `{code}` or `h3.`, since
the current editor shows it as literal text.

This is the place for detail that does not fit in Slack. Leave out any section
that would be empty.

````
### Summary
The tracking pixel now fires after the order is confirmed instead of on page
load, so abandoned checkouts no longer count as sales.

### Changes
- Moved the pixel call into `OrderConfirmationService.confirmOrder`
- Added a guard for orders without a `customerId`

### Decisions
- **Fire on confirmation, not on payment callback.** The callback arrives
  twice for some gateways and would duplicate the sale.

### Out of scope
- Retroactive fix for past orders, tracked in HAT-870

### How to test
1. Place an order and abandon it on the payment step.
2. Confirm no sale is attributed.
3. Complete an order and confirm the sale appears once.

### Notes for review
The guard logs a warning when it skips an order:

```java
log.fWarn("Skipping tracking pixel for orderId {} because it has no customer", orderId);
```

**PR:** <link>
**Video:** <link>
````

## 6. Show and send

Show the three texts, in this order: Slack, Jira in English, Jira in Spanish.
Put each one in its own fenced block, ready to copy. Wrap the Jira texts in a
four-backtick fence, so the code blocks inside them stay intact.

Then wait.

- When I approve the Slack message, send it through the Slack connector, with
  the text unchanged, to the destination I named.
- When I ask for changes, redraft only the texts I named and show them again.
- When the Slack connector is not available or not authenticated, say so. The
  Slack text is already on screen to paste.
- Never post the Jira texts. I paste them into the card myself.

Never send on your own, never send a version I have not seen, and never post to
a channel I did not name.
