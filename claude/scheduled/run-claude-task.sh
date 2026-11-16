#!/usr/bin/env bash
set -euo pipefail

task_name="${1:?Usage: run-claude-task.sh <task-name>}"
scheduled_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
task_file="$scheduled_dir/tasks/$task_name.env"
log_dir="$HOME/.local/state/claude-tasks/$task_name"
log_retention_days=60
oauth_token_file="$HOME/.config/claude-tasks/oauth-token"

export PATH="$HOME/.local/bin:$HOME/.local/share/fnm/aliases/default/bin:$HOME/.conda/envs/hyrosenv/bin:/usr/local/bin:/usr/bin:/bin"

if [ -f "$oauth_token_file" ]; then
  CLAUDE_CODE_OAUTH_TOKEN="$(tr -d '[:space:]' < "$oauth_token_file")"
  export CLAUDE_CODE_OAUTH_TOKEN
fi

mkdir -p "$log_dir"
log_file="$log_dir/$(date +%Y-%m-%d_%H%M).log"
find "$log_dir" -name '*.log' -mtime +"$log_retention_days" -delete

if [ ! -f "$task_file" ]; then
  echo "Task file $task_file does not exist" >> "$log_file"
  exit 1
fi

source "$task_file"
read -r -a allowed_tools <<< "$TASK_ALLOWED_TOOLS"

{
  echo "Starting task $task_name at $(date --iso-8601=seconds)"
  cd "$TASK_WORKDIR"
  exit_code=0
  claude -p "$TASK_PROMPT" --model "$TASK_MODEL" --allowedTools "${allowed_tools[@]}" --no-session-persistence < /dev/null || exit_code=$?
  echo "Finished task $task_name with exit code $exit_code at $(date --iso-8601=seconds)"
  exit "$exit_code"
} >> "$log_file" 2>&1
