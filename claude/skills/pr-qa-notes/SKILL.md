---
name: pr-qa-notes
description: Write a short pull request description and a Jira QA comment with the flows to test, both in English and ready to paste, and on request a short Slack message that shares the PR with the team. Use when asked for the PR description or PR comment, for the QA section of a card, for the flows or paths to test, for a Slack message to share or announce a PR, or to wrap up a card that is done.
---

# PR and QA notes

Turn the work on the current branch into two texts for me to paste:

1. a short pull request description,
2. a Jira comment with the flows QA must test.

Both are in English. When I ask for it, also write a third text: a short Slack
message that shares the PR with the team (section 4). Nothing is posted: not to
the pull request, not to Jira, not to Slack.

## 1. Gather

Read all of this before writing anything.

- **Branch and card key.** `git branch --show-current`. The key is the prefix,
  such as `HMA-8393`. When the branch carries no key, go on without it.
- **Card.** Read it through the Atlassian connector: summary, description and
  acceptance criteria. When the connector is not available, go on without it and
  say so in one line.
- **Base.** `develop`, `staging` or `master-hotfix`. When I did not say which,
  use `staging`.
- **Scope.** Against the base chosen above, after refreshing it. Read the diff
  itself, not only the stat.

  ```
  bb && git fetch origin staging
  git log --oneline origin/staging..HEAD
  git diff origin/staging...HEAD
  ```

  When `git status --porcelain` lists anything, read those changes too and say
  that they are not committed yet.
- **This session.** What was asked, what was decided and why, what was
  discarded, and what was left out of scope on purpose. A diff cannot tell this.

## 2. PR description

Short enough to read without scrolling.

- Two or three short paragraphs. No headings. Use a list only when the branch
  holds several unrelated changes.
- The first paragraph says what changes and why, in terms of behaviour, not
  which files moved.
- When there is no behaviour change, say so plainly.
- Name what a reviewer would ask about: a removed check, where a rule is still
  enforced, a test or assertion that changed.
- Wrap classes, methods, enums, fields, endpoints and config keys in backticks.
- Use **bold** for the one point a reviewer must not miss, at most twice.
- No tool names, no attribution line, no filler such as "This PR".

```
Cleans up `TrueTrackingService.shouldCreateLeadConversion`. Once the tracker
name dedup passed, every remaining branch returned `true`, so the
`EXISTING_LEADS_CONVERSION` and `VALIDATING` checks never changed the result.
Both are removed.

**No behavior change.** A lead conversion is still skipped only when the lead
already has one with the same tracker name and adspend type.
`EXISTING_LEADS_CONVERSION` is still enforced in `LeadOptInService`, before the
conversion is built.

Also updates the assertion message of
`existingLeadsConversionMetadataDoesNotRescueAnExactTrackerMatch`, which
described the removed check order.
```

## 3. Jira QA comment

The section QA reads to know which flows to test.

- Open with `**QA testing**` on its own line, then one sentence of context:
  what behaviour changes, or that it is a regression pass with no expected
  change.
- Then a numbered list of **5 items at most**. Merge cases that are variants of
  each other into one item, and keep an item generic when the detail does not
  change what QA does.
- Each item is a setup or action followed by the expected result, in one or two
  sentences.
- Write it from the point of view of QA: what they do in the app and what they
  must see. No class or method names, unless that name is what QA sets or reads.
- Wrap enums, statuses, settings and field names in backticks. Use **bold** for
  the expected result when it is the point of the item, such as **no
  duplicate**.
- Write it in Markdown, which the Jira editor turns into rich text on paste:
  `**bold**`, `` `code` ``, `1.` lists. Do not use Jira wiki markup such as
  `*bold*`, `{{code}}` or `h3.`, since the current editor shows it as literal
  text.

```
**QA testing**

Cleanup with no expected behavior change. Regression pass on lead conversions:

1. A new lead opts in through an ad click. **One** lead conversion is created.
2. The same lead opts in again. With `EXISTING_LEADS_CONVERSION` off, nothing new is created. With it on, there is still **no duplicate** for the same event.
3. The same lead matches a rule with a different event name. A second conversion is created for that event.
4. Product with two Facebook integrations on different pixels. Each pixel gets its own conversion, with **no duplicate** per pixel.
5. Deferred rules (conversion starts in `VALIDATING`) and Google Ads lead conversions are created once, with **no duplicates** on repeated events.
```

## 4. Slack message, only when I ask for it

The message I post in the team channel when the PR opens or gets an important
update. It tells the team what changes for the customer, not how the code does
it.

- **Language.** The one I ask for. When I do not say, Spanish.
- **Opening.** A greeting and the card key in one line, such as "Buenas, les
  dejo la PR de HMA-8767." or "Hi team! The PR for the Shopify expiring tokens
  card is open." I add the link myself.
- **Body.** One short paragraph about behaviour: what happens now, often
  starting with "Ahora,". Say what stays the same when the team could worry
  about it, such as "with the flag off nothing changes" or "los totales
  funcionan igual que antes". At most one concrete example.
- **Optional second paragraph.** Only facts I can confirm: where the QA flows
  or a test video are, setup already done (AWS secrets, the platform side), a
  request for review, or what was left for a follow-up card and why. Never
  claim a video exists; ask me when it matters.
- **Words.** Plain terms the team uses: conversión, venta, refund, integración,
  flag. No class names, enums, file paths or backticks.
- **Format.** About 60 to 120 words. No headings, no bold labels, no lists. No
  em or en dashes. No Unicode emojis. At most one Slack custom emoji shortcode
  at the end, the way I close, such as `:pepe-justright:` or `:peepo-love:`.

Messages I posted:

```
Buenas, les dejo la PR de HMA-8767. Ahora, cuando en BigCommerce se reembolsa
un producto puntual de una orden, el refund se aplica solo a la sale de ese
producto en lugar de repartirse entre todas. Los refunds por monto custom se
siguen repartiendo entre las sales en proporción a su precio, y los totales
funcionan igual que antes.

Tanto en la PR como en la card adjunté un video probandolo :pepe-justright:
```

```
Hi team! The PR for the Shopify expiring tokens card is open. With the
SHOPIFY_APP_ONLY_TOKENS flag on, stores connected through the public app get
short lived tokens from Shopify and renew them on their own, so syncs keep
running after a token expires. If a customer uninstalls the app, the
integration is still disabled and they get the usual notification, and a
temporary Shopify outage no longer disconnects the store. It also fixes
reconnecting a store right after reinstalling the app, which was failing. With
the flag off nothing changes for customers. Would appreciate a review when you
get a chance :peepo-love:!

The setup on the Shopify side is already done, and the AWS secrets are
configured too.
```

Write it to the scratchpad, grep it for dashes and Unicode emojis, copy it with
`DISPLAY=:0 xclip -selection clipboard -i <file>`, and read the clipboard back
to confirm.

## 5. Show

Show the two texts in this order: PR description, then Jira QA comment. Put
each one in its own fenced block, ready to copy, with nothing else inside the
fence. Talk to me in the language I wrote in; only the two texts are in English.
When I asked for the Slack message, show it after them as a quote, and say it
is already in the clipboard.

Then end with one question: whether I want a short artifact that explains this
flow and what the change implies. Do not build it unless I say yes.

When I ask for changes, redraft only the text I named and show it again.

## 6. The artifact, only when I say yes

A short page for someone new to this flow, with two columns side by side so I
can compare them:

- **Plain language.** What the flow is for, what happens before and after the
  change, and why it matters to the user. No code names.
- **Technical.** The classes, conditions and checks involved, and what the
  change removed, added or moved.

Match the two columns topic by topic, so each plain point sits next to its
technical counterpart. Stack them on a phone. Keep it to about one screen of
reading. Build and publish it with the Artifact tool, following its rules.
