#!/usr/bin/env bash
# PostToolUse hook (Write|Edit): auto-fix and format the touched Python file
# with ruff + black. Silent unless something goes wrong -- purely a formatter,
# never blocks the turn.
set -uo pipefail

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root" || exit 0

file="$(jq -r '.tool_response.filePath // .tool_input.file_path // empty')"

case "$file" in
  *.py) ;;
  *) exit 0 ;;
esac

[ -f "$file" ] || exit 0

uv run ruff check --fix --quiet "$file" >/dev/null 2>&1
uv run black --quiet "$file" >/dev/null 2>&1

exit 0
