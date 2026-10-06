# worktree

Human documentation for the `/worktree` skill. `SKILL.md` next to this file is
what Claude reads and follows. This one explains what it does and why.

Spanish version: [README.es.md](README.es.md)

## The problem it solves

Switching branches with `git checkout` tears down everything that was warm. The
dev server stops, the incremental build is thrown away, and if the branches
declare different dependencies the install has to run again.

That cost is fine once a day. It is not fine when two small cards are in flight
and the point is that one of them keeps running while the other moves.

A worktree is a second working directory over the same `.git`. Two checkouts,
two indexes, one repository. Nothing is duplicated and nothing is re-fetched.

## Directory layout

The worktree is a sibling of the repository and is named after its branch.

```
~/Projects/
  services/                              <- main checkout
  HAT-990-expand-reconnect-tooltip/      <- worktree
  HAT-985-fix-order-total/               <- another worktree
```

## What happens when you create one

```
                     git fetch origin <base>
                              |
               git ls-remote --heads origin <branch>
                              |
         +--------------------+--------------------+
         |                                         |
   exists on origin                          does not exist
         |                                         |
  branch from origin/<branch>            branch from origin/<base>
  names match, so it tracks              with --no-track, no upstream
         |                                         |
         +--------------------+--------------------+
                              |
                    package.json present?
                              |
                   compare lockfile vs main
                              |
              identical -> symlink node_modules
              different -> npm ci
```

The base is `develop`, `staging` or `master-hotfix`, and defaults to `staging`.

Uncommitted work in the main checkout does not block any of this. `git worktree
add` never touches the main working directory.

If the branch is already checked out in another worktree, git refuses. The skill
reports which path holds it and stops rather than forcing anything.

## node_modules, and why a symlink instead of pnpm

Each worktree needs its own `node_modules`, and a full install per card is slow
and heavy.

pnpm solves this structurally, because its content addressed store makes every
install a set of hardlinks. It was considered and deliberately postponed. Its
`node_modules` is not flat, so any package that imports something it does not
declare stops resolving, which is common in frontends with some history. That is
a real risk in exchange for a benefit that is not needed while only one dev
server runs at a time.

So the skill compares the lockfile against the main checkout. Identical lockfiles
mean identical dependencies, and it symlinks the existing `node_modules`. This is
instant, costs no disk, and is safe because nothing else is using it. A different
lockfile means the branch changed its dependencies, so it gets a real `npm ci`.

If simultaneous dev servers are ever needed, pnpm with `node-linker=hoisted` is
the next step.

## The trailing slash trap

Repository `.gitignore` files normally say `node_modules/`, with a trailing
slash, which matches directories only. The symlink created above is not a
directory, so the pattern does not match it. It shows up as an untracked file,
and `git worktree remove` then refuses to delete the worktree:

```
fatal: '../HAT-990-...' contains modified or untracked files, use --force to delete it
```

The fix is `node_modules`, with no trailing slash, in the local exclude file:

```
EXCLUDE="$(git rev-parse --git-common-dir)/info/exclude"
grep -qx node_modules "$EXCLUDE" || echo node_modules >> "$EXCLUDE"
```

`.git/info/exclude` is per clone and is never pushed, so the repository and the
rest of the team see nothing. It is written once and applies to every worktree,
because `info/` lives in the shared git directory. The skill does this on its
first run.

## Getting the work back into the main checkout

Nothing has to be moved. A worktree shares the same `.git`, so every commit made
inside it is already visible from the main checkout the moment it exists. There
is no push, no cherry pick and no copying of files.

The only obstacle is that git keeps one branch checked out in one worktree at a
time. Remove the worktree and the branch is free:

```
git worktree remove ../HAT-990-expand-reconnect-tooltip
git checkout HAT-990-expand-reconnect-tooltip
```

For work that is not committed yet, the stash is shared across worktrees:
`git stash` inside the worktree, `git stash pop` from the main checkout.

## Finishing a card

```
git worktree list
git worktree remove ../HAT-990-expand-reconnect-tooltip
git worktree prune
```

`remove` refuses when the directory holds modified or untracked files. That guard
is wanted, so the skill reports what is dirty and waits instead of forcing.
Removal does not follow the `node_modules` symlink, so the main checkout keeps
its own.

`prune` clears the records of worktrees whose directory was deleted by hand.

## What it depends on

| Thing | Why |
| ----- | --- |
| `branch.autoSetupMerge = simple` | A new branch from `origin/staging` gets no upstream, while a branch whose name matches its remote tracks it. Both behaviours from one setting. |
| Network access to Bitbucket | Handled by the `bb` alias. See the repository root README. |
| `~/.claude/CLAUDE.md` | Supplies the branch naming rules: `<KEY>-<description>`, 40 characters at most. |
