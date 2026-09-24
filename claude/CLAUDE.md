# Conventions

These apply to every project.

## Branching from a card

When I give you a card key such as `HAT-865`, settle the branch before anything
else, before diagnosing or planning.

1. Read the current branch. If its name starts with that key, it is already the
   right branch. Stay on it.
2. Otherwise, look for an existing branch for that key, locally and on origin.
   If one exists, switch to it. Never open a second branch for the same card.
3. Only when none exists, create it.

### Before creating

Run `git status --porcelain`. If anything is uncommitted, stop there. List the
dirty files and wait for me to decide whether to stash, commit or discard them.
Do not stash on your own, and do not carry the changes onto a different base.

### Creating

Always fetch the base branch first, and branch from the remote ref, so the new
branch starts from what origin has and not from a stale local copy.

Pass `--no-track`. Without it git sets the upstream to the base branch, and a
later `git push` either refuses or offers to push the work straight into
`staging`. The new branch must stand on its own, with no upstream, until I push
it with `--set-upstream`.

```
git fetch origin staging
git checkout -b HAT-865-fix-tracking-pixel --no-track origin/staging
```

The base is `develop`, `staging` or `master-hotfix`. When I do not say which one,
use `staging`.

### Name

`<KEY>-<short-description>`, 40 characters at most in total, the key included.
The description is lowercase kebab case, in English, taken from the card summary
and shortened until it fits. Drop filler words rather than cutting a word in
half, and keep it readable.

```
HAT-865-fix-tracking-pixel-order              32   ok
HAT-865-fix-the-tracking-pixel-on-order-page  44   too long
```

## Reviewing, diagnosing, answering

When I ask you to evaluate review comments, to diagnose something, or whether
something is right, the deliverable is the verdict, not the change. Even when my
own message says to apply the fixes afterwards, that is my intent for later, not
permission for now.

In this mode:

- Read whatever you need. Reading is always free.
- Answer comment by comment: valid or not, and why.
- For every fix you would make, show the diff in the reply, as text.
- Write to no file, and run no build, no compile and no test.

Then stop. Nothing is applied until I say `apply`, or name the fixes I want, and
that message authorizes only what it names.

## Naming

Use descriptive names for methods, variables, classes and fields. Avoid generic
ones such as `handle`, `sync`, `process`, `data` or `manager`, unless the name
genuinely describes the whole behaviour.

## Comments

Do not add comments. The code must be readable on its own, and a comment on
self-explanatory code is counterproductive.

The only exception is logic a developer cannot follow from the code itself.
Write one short line, in English, in plain ASD-STE100 wording, that says *why*
the code is there. Never restate *what* it does, and never reference a ticket,
card or issue.

## Javadoc

| Case                      | What to write                             |
| ------------------------- | ----------------------------------------- |
| Self-explanatory method   | Nothing. Skip it.                         |
| Non-obvious method        | One line: what it does, or why it exists. |
| Genuinely complex method  | The flow, plus `@param` and `@return`.    |

Keep it short, enough to follow the flow and no more. Document a parameter only
when the term is unfamiliar or specific to the class, such as an integration id
or an external key. Do not document obvious ones like `productId`.

## One type per file

Every DTO, record and enum lives in its own file, on the backend and on the
frontend alike.

## Logging

Add logs as part of the implementation. They are valuable when applied well.

| Level    | When                                                      |
| -------- | --------------------------------------------------------- |
| `fInfo`  | Entering a method, to record that a process was called.   |
| `fWarn`  | An early return that may not be expected.                 |
| `fError` | Unexpected exceptions. It notifies New Relic.             |

Every log carries an identifier that lets the operation be traced: `productId`,
the `external_id` of an integration, and so on.

Write them as natural, readable sentences. Keep every logger call inline, never
break the line to add parameters. Do not use the PREFIX style found in older
code. Avoid decorative formatting: no values wrapped in `()`, no `->`, no `[]`,
and never a long dash — the em dash below is exactly what to avoid.

```
Good:  "Starting product sync for productId {} and integration {}"
Bad:   "[SYNC] -> Starting product sync (productId: {}) — integration [{}]"
```
