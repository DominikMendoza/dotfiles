# rgv - Search with rgf and open the selected match in Neovim
#
# Uses rgf to interactively pick a match (file:line) and then opens
# that file in Neovim positioned at the matching line.
#
# All flags are forwarded to rgf, so you can use:
#   -i, --ignore-case
#   -S, --smart-case
#   -h, --help
#
# Usage:
#   rgv                          # Pick a match and open it in nvim
#   rgv "UserService"            # Pre-filter with rg, then open in nvim
#   rgv -i "userservice"
#
# Requires the rgf function to be loaded in the current shell.

rgv() {
  if ! command -v nvim >/dev/null 2>&1; then
    echo "Error: nvim is not installed or not in PATH."
    return 1
  fi

  if ! typeset -f rgf >/dev/null 2>&1 && ! declare -f rgf >/dev/null 2>&1; then
    echo "Error: rgf function is not loaded. Source rgf.sh first."
    return 1
  fi

  local result
  result=$(rgf "$@")

  # Exit silently if the user cancelled the picker (Esc / Ctrl-C).
  [ -z "$result" ] && return 0

  # rgf output format: <file>:<line>
  local file="${result%%:*}"
  local line="${result##*:}"

  if [ ! -f "$file" ]; then
    echo "Error: file not found: $file"
    return 1
  fi

  nvim "+${line}" "$file"
}
