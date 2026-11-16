#!/usr/bin/env bash
set -euo pipefail

task_name="${1:?Usage: run-scheduled-task.sh <task-name>}"
scheduled_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
task_file="$scheduled_dir/tasks/$task_name.env"
secrets_file="$HOME/.config/claude-tasks/secrets.env"
log_dir="$HOME/.local/state/claude-tasks/$task_name"
log_retention_days=60

export PATH="$HOME/.local/bin:$HOME/.conda/envs/hyrosenv/bin:/usr/local/bin:/usr/bin:/bin"

if [ -f "$secrets_file" ]; then
  set -a
  source "$secrets_file"
  set +a
fi

mkdir -p "$log_dir"
log_file="$log_dir/$(date +%Y-%m-%d_%H%M).log"
find "$log_dir" -name '*.log' -mtime +"$log_retention_days" -delete

if [ ! -f "$task_file" ]; then
  echo "Task file $task_file does not exist" >> "$log_file"
  exit 1
fi

set -a
source "$task_file"
set +a

{
  echo "Starting task $task_name at $(date --iso-8601=seconds)"
  cd "$HOME"
  exit_code=0
  bash -c "$TASK_COMMAND" < /dev/null || exit_code=$?
  echo "Finished task $task_name with exit code $exit_code at $(date --iso-8601=seconds)"
  exit "$exit_code"
} >> "$log_file" 2>&1
