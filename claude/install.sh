#!/usr/bin/env bash
#
# Claude Code plugins bootstrap.
# Sets up the local marketplace + Postman plugin, and non-destructively merges
# the required keys into ~/.claude/settings.json. Safe to run multiple times.
#
# Run standalone:      ./claude/install.sh
# Or from install.sh:  source "$DOTFILES/claude/install.sh"

set -euo pipefail

# Directory this script lives in (the dotfiles "claude/" folder).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

CLAUDE_DIR="$HOME/.claude"
MARKET_DIR="$CLAUDE_DIR/local-marketplace"
PLUGIN_DIR="$MARKET_DIR/postman-claude-code-plugin"
PLUGIN_REPO="https://github.com/Postman-Devrel/postman-claude-code-plugin.git"
SETTINGS="$CLAUDE_DIR/settings.json"

command -v jq >/dev/null 2>&1 || { echo "❌ jq is required (install it and re-run)."; exit 1; }

echo "▸ Setting up Claude Code marketplace at $MARKET_DIR"
mkdir -p "$MARKET_DIR/.claude-plugin"

# Symlink the marketplace manifest from dotfiles (edits in the repo propagate).
ln -sf "$SCRIPT_DIR/marketplace.json" "$MARKET_DIR/.claude-plugin/marketplace.json"

# Clone the plugin only if missing (it is NOT versioned in dotfiles).
if [ -d "$PLUGIN_DIR/.git" ]; then
  echo "▸ Plugin already cloned, skipping."
else
  echo "▸ Cloning Postman plugin..."
  git clone --depth 1 "$PLUGIN_REPO" "$PLUGIN_DIR"
fi

# Merge the required keys into settings.json without clobbering existing config.
echo "▸ Merging keys into $SETTINGS"
[ -f "$SETTINGS" ] || echo '{}' > "$SETTINGS"
cp "$SETTINGS" "$SETTINGS.bak"   # backup before editing

tmp="$(mktemp)"
jq --arg mp "$MARKET_DIR" '
  .extraKnownMarketplaces.local = { source: { source: "directory", path: $mp } }
  | .enabledPlugins["postman@local"] = true
' "$SETTINGS" > "$tmp" && mv "$tmp" "$SETTINGS"

echo "✅ Done. Restart Claude Code, then run /plugin and /mcp to verify."
echo "   Authenticate Postman with /postman:setup (OAuth)."
