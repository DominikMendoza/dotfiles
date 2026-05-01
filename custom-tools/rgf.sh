# rgf - Interactive text search across files
#
# Combines ripgrep (rg) for file searching with fzf for interactive filtering
# and syntax-highlighted preview (bat).
#
# Defaults:
#   - Case-sensitive search
#   - Exact match in fzf filter (no fuzzy matching)
#
# Flags:
#   -i, --ignore-case    Case-insensitive search
#   -S, --smart-case     Smart-case (insensitive unless query has uppercase)
#   -h, --help           Show help
#
# Usage:
#   rgf                          # List everything and filter in fzf
#   rgf "UserService"            # Pre-filter with rg, refine in fzf
#   rgf -i "userservice"         # Case-insensitive
#   rgf -S "userservice"         # Smart-case
#
# Operators available inside the fzf prompt:
#   ^text     starts with
#   text$     ends with
#   !text     does not contain
#   a | b     contains a or b
#   a b       contains a and b (space = AND)

rgf() {
  local case_flag="--case-sensitive"

  while [[ "$1" == -* ]]; do
    case "$1" in
      -i|--ignore-case)
        case_flag="--ignore-case"
        shift
        ;;
      -S|--smart-case)
        case_flag="--smart-case"
        shift
        ;;
      -h|--help)
        echo "Usage: rgf [-i|--ignore-case] [-S|--smart-case] [initial query]"
        echo ""
        echo "Search is case-sensitive and fzf filter uses exact match by default."
        echo ""
        echo "Flags:"
        echo "  -i, --ignore-case    Case-insensitive search"
        echo "  -S, --smart-case     Smart-case (insensitive unless query has uppercase)"
        echo "  -h, --help           Show this help"
        return 0
        ;;
      *)
        echo "Unknown flag: $1"
        echo "Run 'rgf --help' to see available options."
        return 1
        ;;
    esac
  done

  local result
  result=$(rg --line-number --no-heading --color=always "$case_flag" "${1:-}" | \
    fzf --ansi \
        --exact \
        --delimiter : \
        --nth 3.. \
        --preview 'bat --color=always {1} --highlight-line {2}' \
        --preview-window 'up,60%,border-bottom,+{2}+3/3' \
        --bind 'enter:become(echo {1}:{2})')
  [ -n "$result" ] && echo "$result"
}
