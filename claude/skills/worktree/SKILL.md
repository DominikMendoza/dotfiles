---
name: worktree
description: Create, reuse and clean up a git worktree for a card, so work on several cards runs in parallel. Use when asked to open a worktree for a card, to list them, to remove one, or to move a worktree's work back into the main checkout.
---

# Worktrees

`README.md` and `README.es.md` in this folder document all of this for a
human reader. They are not needed to run the skill, so do not read them
unless I ask about them.

A worktree gives a second working directory over the same `.git`. Use it to keep
one card's state warm while another moves.

## Once per clone

Add `node_modules`, with no trailing slash, to the local exclude file. The
repository `.gitignore` says `node_modules/`, and a trailing slash matches
directories only, so the symlink created below would otherwise show up as an
untracked file and block `git worktree remove`.

```
EXCLUDE="$(git rev-parse --git-common-dir)/info/exclude"
grep -qx node_modules "$EXCLUDE" || echo node_modules >> "$EXCLUDE"
```

This file is per clone and is never pushed, so nothing reaches the team.

## Creating

The branch name follows the rules in `~/.claude/CLAUDE.md`: `<KEY>-<description>`,
40 characters at most. The worktree directory is a sibling of the repository and
carries the same name as the branch.

Uncommitted work in the main checkout does not block anything here, because
`git worktree add` never touches the main working directory. Do not stop for it.

1. Refresh the remote.

   ```
   git fetch origin staging
   ```

2. Ask origin whether the branch is already there.

   ```
   git ls-remote --heads origin HAT-990-expand-reconnect-tooltip
   ```

3. Create the worktree with the case that applies.

   The branch exists on origin. Fetch it and branch from it. The names match, so
   `branch.autoSetupMerge=simple` sets the upstream on its own and `git push`
   works with no further flags.

   ```
   git fetch origin HAT-990-expand-reconnect-tooltip
   git worktree add -b HAT-990-expand-reconnect-tooltip \
       ../HAT-990-expand-reconnect-tooltip origin/HAT-990-expand-reconnect-tooltip
   ```

   The branch is new. Branch from the base, `develop`, `staging` or
   `master-hotfix`, and default to `staging`. Pass `--no-track` so it is born
   independent, with no upstream, and is never pushed by accident into the base.

   ```
   git worktree add -b HAT-990-expand-reconnect-tooltip \
       ../HAT-990-expand-reconnect-tooltip --no-track origin/staging
   ```

   A local branch already exists and is not checked out anywhere. Reuse it,
   without `-b`.

   ```
   git worktree add ../HAT-990-expand-reconnect-tooltip HAT-990-expand-reconnect-tooltip
   ```

   Git refuses a branch that is already checked out in another worktree. Run
   `git worktree list`, report the path, and stop. Do not pass `--force`.

## node_modules

Only when the worktree has a `package.json`.

Compare the lockfile against the main checkout. When they are identical, symlink
the existing `node_modules` instead of installing. It is instant and costs no
disk, and it is safe because only one dev server runs at a time.

```
MAIN="$(git worktree list --porcelain | awk 'NR==1 {print $2}')"
if cmp -s "$MAIN/package-lock.json" package-lock.json; then
    ln -s "$MAIN/node_modules" node_modules
else
    npm ci
fi
```

When the lockfiles differ the branch changed its dependencies, so it needs a real
install of its own. Say which of the two paths was taken.

## Moving the work back

Nothing has to be transported. A worktree shares the same `.git`, so every commit
made there is already visible from the main checkout. Never push, cherry pick or
copy files to move work across.

The only thing that blocks `git checkout` in the main directory is that git keeps
one branch in one worktree at a time. So:

```
git worktree remove ../HAT-990-expand-reconnect-tooltip
git checkout HAT-990-expand-reconnect-tooltip
```

For work that is not committed yet, the stash is shared across worktrees.
`git stash` in the worktree, then `git stash pop` from the main checkout.

## Finishing a card

`git worktree remove` refuses to delete a directory holding modified or
untracked files. That guard is wanted. When it fires, report what is dirty and
wait. Never reach for `--force` on your own.

A symlinked `node_modules` is not followed on removal, so the main checkout keeps
its own.

```
git worktree list
git worktree remove ../HAT-990-expand-reconnect-tooltip
git worktree prune
```

`prune` clears the records of worktrees whose directory was deleted by hand.
