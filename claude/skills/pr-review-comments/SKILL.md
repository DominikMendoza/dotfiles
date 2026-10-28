---
name: pr-review-comments
description: Draft the comments I leave on someone else's pull request, in English, few and short, in my own voice, each one with the file and line where it goes. Use when asked for the comments of a PR review, which lines to comment on, to turn review findings into PR comments, or to draft a reply to a comment on a pull request.
---

# PR review comments

A review finds many things. Only a few deserve a comment, and those must read as
if I wrote them in a minute, not as a report. `/code-review` does the analysis.
This skill distills its output into the comments I post: what survives and how
it is worded.

Nothing is posted. I paste the comments myself. Post to Bitbucket only when I
explicitly ask for it, and only after I confirm the final text.

## 1. Gather

- **The `/code-review` output.** Always run it first, through the Skill tool,
  with the PR as the target. When it already ran on this PR in this session, use
  that result instead of running it again. Wait for it to finish before
  selecting anything. Every finding goes through section 2, including the ones
  it is sure about.
- **The diff at the PR head**, from Bitbucket (`/pullrequests/{id}/diff`), not
  from a local checkout that may be on another commit. Use it to check each
  finding that survives and to take its line number.
- **Existing comments** on the PR, from people and from the bot. Never repeat a
  point that is already there. When the bot already raised it and it is right,
  a one-line reply on that thread beats a new comment: "The case the bot
  mentions is real; the suggestion to limit the scope makes sense to me."
- **My own question**, when I asked something specific about the PR, such as
  whether the tests prove anything. Answer it in the chat. It becomes a comment
  only when it passes section 2.

## 2. Select

Default to one to three comments. Zero is a valid result: then say that I can
approve as it is, and stop.

Keep:

- A behaviour bug with a concrete scenario: wrong data saved, a silent failure,
  an error that no longer reaches New Relic, a secret in a log.
- A design choice that will hurt soon, when I can say why in two sentences.
- A test that does not prove the fix, said as one instruction.
- Short team rules: a missing identifier in a log, an early return without
  `fWarn`, a comment that should not be there. One line each.

Drop:

- Anything not verified. Never write "as far as I know" or "if I'm not wrong":
  check it, or leave it out.
- Anything outside the diff. When it is serious, keep it with "Maybe out of
  scope, but".
- Efficiency micro-wins, dead code that harms nothing, test names, duplicated
  helpers, refactors nobody asked for.
- Log format rules from my personal `CLAUDE.md`, such as the PREFIX style or
  `[]` around values. The author follows the repo, not my file.
- Praise, and a summary of what the PR does.

## 3. Write

**Length follows weight.**

- A rule: one line. "Remove this comment." "Add a `fWarn` for early return
  scenarios." "Missing arguments for `: {}`. Please log the `productId`."
- A design concern: two to four sentences. What happens, then what I recommend.
- A real bug: the scenario in two or three sentences, then the fix. Under about
  120 words. A short list only when it names concrete cases.

**Voice.**

- Open with the problem. No "Nice catch", no "Great work", no context the author
  already knows about their own code.
- Plain verbs: "Add", "Remove", "Please review", "I recommend", "I suggest".
- Ask only when I am truly unsure of the intent: "Why do we add a fallback
  header? As I understand it, the previous one would work."
- Soften only when it costs the author extra work or is out of scope: "I know
  it's extra work, but...", "If this varies a lot across endpoints, you can
  disregard this comment."
- When the codebase already solves it somewhere, point there by class and
  method, or with a link.
- Do not start every comment the same way. "Could we" three times in a row reads
  like a template.
- Simple English with short sentences. No em dashes, no emojis.

**Format.**

- No labels: no `nit:`, no severity, no numbers, no headings.
- Backticks for classes, methods, fields, enums and config keys. Bold at most
  once, for the action, and only in a long comment.
- Code only for the one or two lines that are the fix, in a fenced block. No
  diffs, no full test methods.
- The same issue on another line: "Same as above." Nothing more.
- `@mention` the author only in a general comment, never inline.

### Before and after

Draft:

> The new test only checks the exception message. It does not verify that no
> integration was saved, and it does not cover the realistic case of a non-null
> profile with empty fields. This matters because `promoteTokenForUser` is
> `@Transactional` and `InvalidTokenException` is checked, so anything written
> before the throw is committed, not rolled back. A regression that saves the
> integration before the guard would still pass this test.

What I posted:

> Add an assertion to verify that no integration is persisted following the
> exception, and include a second test using a profile with blank fields.

### Comments I wrote

> If it is decided to disable TPT for a product, this metric will be set to 0 in
> all cases. I recommend removing this conditional.

> I know it's extra work, but it would be quite helpful if we could identify the
> specific parts of the response we want and log only those. If this varies
> significantly across different endpoints, you can disregard this comment.
> Here's a [reference](link) on how this was handled for Outlook
> `extractTokenExchangeError`.

> Maybe out of scope, but it would be useful to log the full stack trace instead
> of just the exception message. Keep in mind that a new path has been added
> that can throw that exception.

> When Meta responds to `/me` with an error body, the JSON is parsed
> successfully and `getUserProfileInfoFromToken` returns a profile with empty
> email, name and picture instead of `null`. The guard passes, `setEmail("")`
> overwrites the user's email and changes the integration hash, and the refresh
> ends "successfully" instead of returning the new 400.
>
> **Add an extra check:**
>
> ```java
> if (profileInfoDTO == null || StringUtils.isBlank(profileInfoDTO.getId())) {
> ```

## 4. Replies on my own PR

Same voice, shorter.

- Agree and fixed: "Good catch, fixed." Add one line only when the fix is not
  obvious from the code.
- Agree, handled elsewhere: "I completely agree, they'll be deleted in this
  [PR](link)."
- Disagree: the reason in one or two sentences, without apologising.
- Already done: "Done!"

## 5. Show

Talk to me in the language I wrote in. Only the comments are in English.

For each comment:

1. A line with `File.java:123` and the code on that line, so I can find it.
   Take the number from the new side of the PR diff at the head commit. Comment
   only on lines that are in the diff.
2. The text in its own fenced block, in Markdown, ready to paste. Bitbucket
   renders Markdown, so no Jira wiki markup such as `{{code}}`.

Then a **Descartados** list with every `/code-review` finding left out, one
line each with the reason, so I can pull one back. Do not show the full
`/code-review` report on top of this.

When I ask for a file, write the same content to `/tmp/pr-<id>-comments.md`.
When I ask for changes, redraft only the comments I named.
