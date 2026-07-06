# claude — Claude Code plugins

Personal, user-scoped setup for Claude Code plugins (and their bundled MCP
servers), installed so they load in **every** project without per-launch flags
and without touching any work repo.

Documented plugin: **Postman**. The same pattern works for any Claude Code
plugin that is a git repo with `.claude-plugin/plugin.json`.

## Contents

| File                    | Purpose                                                              |
| ----------------------- | ------------------------------------------------------------------- |
| `install.sh`            | Bootstrap: sets up the marketplace, clones the plugin, merges keys.  |
| `marketplace.json`      | Local marketplace manifest (symlinked into `~/.claude/`).            |
| `settings.snippet.json` | Reference only — the keys `install.sh` merges into `settings.json`.  |

The plugin's own code is **not** versioned here — `install.sh` clones it on demand.

## Install

```bash
./claude/install.sh
```

Or call it from the top-level `install.sh`:

```bash
source "$DOTFILES/claude/install.sh"
```

It is idempotent (safe to re-run) and backs up `settings.json` to
`settings.json.bak` before editing. Paths are resolved from `$HOME` at runtime,
so nothing is hard-coded to a specific machine.

Then restart Claude Code and verify:

```
/plugin        → postman@local  should be enabled
/mcp           → the  postman  server should appear
/postman:setup → authenticate (OAuth recommended)
```

## How it works

1. Symlinks `marketplace.json` → `~/.claude/local-marketplace/.claude-plugin/marketplace.json`.
2. Clones the plugin → `~/.claude/local-marketplace/postman-claude-code-plugin/` (if missing).
3. Merges two keys into `~/.claude/settings.json`:
   - `extraKnownMarketplaces.local` → points at `$HOME/.claude/local-marketplace` (type `directory`).
   - `enabledPlugins."postman@local": true`.

> ⚠️ For a local folder the marketplace `source` type must be `directory` with a
> `path`. The `url` type fails validation (it requires a real URI, not a disk path).

## Postman notes

The plugin bundles this MCP server (`postman-claude-code-plugin/.mcp.json`):

```json
{
  "mcpServers": {
    "postman": {
      "type": "http",
      "url": "https://mcp.postman.com/${POSTMAN_MCP_MODE:-mcp}"
    }
  }
}
```

Optional env vars (add to `~/.zshrc`):

| Variable           | Purpose                                                            |
| ------------------ | ----------------------------------------------------------------- |
| `POSTMAN_API_KEY`  | Auth via API key instead of OAuth (`PMAK-...`).                   |
| `POSTMAN_MCP_MODE` | Server mode: `mcp` (default), `minimal` or `code` (fewer tokens). |

## Add another plugin

1. Add an entry to the `plugins` array in `marketplace.json`
   (`name` = the one in its `plugin.json`, `source` = `./<folder>`).
2. Add a clone line for it in `install.sh`.
3. Add `"<name>@local": true` to the `jq` merge in `install.sh`.

One `local` marketplace can host many plugins.
