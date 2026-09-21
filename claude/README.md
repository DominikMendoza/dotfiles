# claude — Claude Code configuration

Personal, user-scoped Claude Code setup: it loads in **every** project, with no
per-launch flags and without touching any work repo.

The files live here (versioned) and are **symlinked** into `~/.claude/`. Edit
either side — it is the same file — and `git status` sees the change. No copying
by hand.

## Contents

| File / folder                   | Linked to                                       |
| ------------------------------- | ----------------------------------------------- |
| `settings.json`                 | `~/.claude/settings.json`                       |
| `statusline-command.sh`         | `~/.claude/statusline-command.sh`               |
| `skills/skill-template/`        | `~/.claude/skills/skill-template`               |
| `agents/agent-template.md`      | `~/.claude/agents/agent-template.md`            |
| `marketplace.json`              | `~/.claude/local-marketplace/.claude-plugin/`   |
| `install.sh`                    | — (creates every link above)                    |

The Postman plugin's own code is **not** versioned: `install.sh` clones it.

## Install

```bash
./claude/install.sh
```

Idempotent. If it finds a real file where a link belongs, it moves it to
`~/.claude/backups/dotfiles-<date>/` first — it never overwrites anything.

Then restart Claude Code and verify:

```
/plugin        → postman@local  enabled
/mcp           → the  postman  server shows up
/postman:setup → authenticate (OAuth recommended)
```

## What is NOT versioned (important)

`~/.claude/` is not just configuration. These must never reach the repo:

| Path                                          | What it is                    |
| --------------------------------------------- | ----------------------------- |
| `.credentials.json`, `anthropic_key.sh`       | **live tokens and API keys**  |
| `history.jsonl`                               | everything you have typed     |
| `projects/`, `sessions/`, `file-history/`     | transcripts and code          |
| `cache/`, `debug/`, `paste-cache/`, `session-env/`, `shell-snapshots/` | runtime state |
| `skills/synced/`                              | cloud-synced skills           |

That is why files are linked **one by one** instead of linking all of
`~/.claude`. The repo-root `.gitignore` blocks them as a second safety net.

## Skills and agents

Both are linked individually, not as whole folders — `~/.claude/skills/` also
holds `synced/`, managed by Claude Code itself, which must stay out of git.

- **Skill** → a folder with a `SKILL.md`; shows up as `/<name>`.
  Start from `skills/skill-template/`.
- **Agent** → a single `.md` file with frontmatter; a delegate subagent.
  Start from `agents/agent-template.md`.

For either one: copy the template, edit it, add its `link` line to
`install.sh`, re-run the script, restart Claude Code. Each template documents
its own format.

## Portability

`settings.json` uses `~` instead of absolute paths; Claude Code expands it on
read (verified on v2.1.59). The same file works on any machine, whatever the
username.

> ⚠️ Adding a marketplace from the UI (`/plugin`) makes Claude Code rewrite
> `settings.json` and **normalize the path to an absolute one**. Since it is a
> symlink, that lands in the repo: check `git diff` and put `~` back if a
> `/home/<user>/...` shows up.

> ⚠️ For a local folder the marketplace `source` must be type `directory` with a
> `path`. Type `url` fails validation (it requires a real URI, not a disk path).

## Adding another plugin

1. Add an entry to the `plugins` array in `marketplace.json`
   (`name` = the one in its `plugin.json`, `source` = `./<folder>`).
2. Add its clone line in `install.sh`.
3. Add `"<name>@local": true` to `enabledPlugins` in `settings.json`.

One `local` marketplace can host many plugins.

## Statusline

`statusline-command.sh` draws the bottom line (robbyrussell-style theme):
directory, git branch, model, context usage (`ctx`) and usage of the current
5-hour session window (`ses`). It receives a JSON payload on stdin
(`workspace.current_dir`, `model.display_name`, `context_window.used_percentage`,
`rate_limits.five_hour.used_percentage`, `session_id`, session cost, lines added
or removed). Requires `jq`.
