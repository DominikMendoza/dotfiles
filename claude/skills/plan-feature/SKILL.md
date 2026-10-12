---
name: plan-feature
description: Plan a feature or change before any code is written. Use when asked to plan an implementation, to evaluate a proposed approach, or to scope work before implementing it.
---

# Plan a feature

Produce an implementation plan and stop there. Present it and wait for approval.

## Out of scope for this first iteration

- Test cases. They come later, through `/test-plan`.
- Module compilation, builds, and verification commands of any kind, on the
  backend and on the frontend alike.

## Steps

1. Read the proposal and the code it touches.
2. Evaluate the proposal on its merits. If a different approach is better, say
   so and explain why. Do not silently plan something other than what was asked.
3. Ask the questions that matter before planning: anything ambiguous, and any
   decision that would change the shape of the plan.
4. Present the plan and wait.

The conventions in `~/.claude/CLAUDE.md` apply to everything the plan proposes,
in particular the naming rules, the absence of comments, and the logging that
each new implementation must carry.

## Assertions

Any test code the plan touches follows the repository's `.ai-pr-reviews` rule,
and that includes a mechanical update made only to keep a test compiling. Every
`assertTrue` carries a message that states the expected condition and its
context: the ids, the inputs, or the actual value. The PR review flags an
`assertTrue` without one as a `MUST`.

```
assertTrue(blacklist.automaticallyBlacklistedProviders().isEmpty(),
    "The returned blacklist reflects the removal; got " + blacklist.automaticallyBlacklistedProviders());
```
