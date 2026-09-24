#!/usr/bin/env bash
#
# Claude Code — config bootstrap via symlinks.
#
# Links the versioned files in this repo into ~/.claude/, so editing either side
# (it is the same file) shows up in git. Any real file found in the way is backed
# up first, never overwritten.
#
# Standalone:  ./claude/install.sh
# From root:   source "$DOTFILES/claude/install.sh"
#
# Idempotent: re-running it changes nothing and creates no extra backups.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

CLAUDE_DIR="$HOME/.claude"
MARKET_DIR="$CLAUDE_DIR/local-marketplace"
PLUGIN_DIR="$MARKET_DIR/postman-claude-code-plugin"
PLUGIN_REPO="https://github.com/Postman-Devrel/postman-claude-code-plugin.git"
BACKUP_DIR="$CLAUDE_DIR/backups/dotfiles-$(date +%Y%m%d-%H%M%S)"

# link <path-in-repo> <path-relative-to-~/.claude>
link() {
  local src="$SCRIPT_DIR/$1"
  local dest="$CLAUDE_DIR/$2"

  if [ ! -e "$src" ]; then
    echo "  ⚠ $1 not found in repo, skipped"
    return
  fi

  # Already pointing at the same target: nothing to do.
  if [ -L "$dest" ] && [ "$(readlink -f "$dest")" = "$(readlink -f "$src")" ]; then
    echo "  ✓ $2 already linked"
    return
  fi

  # A real file (or a stale link) is in the way: back it up, do not clobber it.
  if [ -e "$dest" ] || [ -L "$dest" ]; then
    mkdir -p "$BACKUP_DIR"
    mv "$dest" "$BACKUP_DIR/"
    echo "  ↪ $2 backed up to ${BACKUP_DIR/#$HOME/\~}/"
  fi

  mkdir -p "$(dirname "$dest")"
  ln -s "$src" "$dest"
  echo "  → $2 linked"
}

mkdir -p "$CLAUDE_DIR"

echo "▸ Linking config into ${CLAUDE_DIR/#$HOME/\~}"
link settings.json          settings.json
link statusline-command.sh  statusline-command.sh
link CLAUDE.md              CLAUDE.md

# Skills and agents are linked one by one, NOT as whole directories:
# ~/.claude/skills/ also holds synced/ (cloud-synced skills) which must stay put.
echo "▸ Linking skills and agents"
link skills/skill-template  skills/skill-template
link skills/plan-feature    skills/plan-feature
link skills/test-plan       skills/test-plan
link agents/agent-template.md  agents/agent-template.md
# To add more: drop it in claude/skills|agents/ and add its line above.

echo "▸ Setting up local marketplace at ${MARKET_DIR/#$HOME/\~}"
mkdir -p "$MARKET_DIR/.claude-plugin"
ln -sfn "$SCRIPT_DIR/marketplace.json" "$MARKET_DIR/.claude-plugin/marketplace.json"

# The plugin's own code is NOT versioned here: it is cloned on demand.
if [ -d "$PLUGIN_DIR/.git" ]; then
  echo "  ✓ Postman plugin already cloned"
else
  echo "  → cloning Postman plugin..."
  git clone --depth 1 "$PLUGIN_REPO" "$PLUGIN_DIR"
fi

# jq is not needed to install, but the statusline calls it on every refresh.
command -v jq >/dev/null 2>&1 || echo "  ⚠ 'jq' missing: the statusline stays blank until you install it"

echo "✅ Done. Restart Claude Code, then check /plugin and /mcp."
echo "   Authenticate Postman with /postman:setup (OAuth)."
