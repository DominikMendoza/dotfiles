#!/bin/bash
# Claude Code status line — based on robbyrussell Oh My Zsh theme

input=$(cat)

cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // "?"')
model=$(echo "$input" | jq -r '.model.display_name // "Claude"')
used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
session_pct=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')

# Current directory basename (like robbyrussell %c)
dir_name=$(basename "$cwd")

# Git branch (skip optional locks for safety)
git_branch=""
if git -C "$cwd" rev-parse --git-dir > /dev/null 2>&1; then
    git_branch=$(git -C "$cwd" -c gc.auto=0 symbolic-ref --short HEAD 2>/dev/null || git -C "$cwd" -c gc.auto=0 rev-parse --short HEAD 2>/dev/null)
fi

# Build the status line using ANSI colors (printf for proper escape handling)
# Cyan for directory, blue/red for git — matching robbyrussell palette
if [ -n "$git_branch" ]; then
    git_part=$(printf '\033[1;34mgit:(\033[0;31m%s\033[1;34m)\033[0m' "$git_branch")
    dir_part=$(printf '\033[0;36m%s\033[0m' "$dir_name")
    line="$dir_part $git_part"
else
    line=$(printf '\033[0;36m%s\033[0m' "$dir_name")
fi

# Append model name
line="$line $(printf '\033[0;35m[%s]\033[0m' "$model")"

# Append context usage if available
if [ -n "$used_pct" ]; then
    used_int=${used_pct%.*}
    line="$line $(printf '\033[0;33mctx:%s%%\033[0m' "$used_int")"
fi

if [ -n "$session_pct" ]; then
    session_int=${session_pct%.*}
    line="$line $(printf '\033[0;32mses:%s%%\033[0m' "$session_int")"
fi

printf '%b\n' "$line"
