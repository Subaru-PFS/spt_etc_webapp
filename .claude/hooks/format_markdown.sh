#!/usr/bin/env bash
# PostToolUse hook (Write|Edit): lint + auto-fix the touched Markdown file
# with markdownlint-cli2 (rules in .markdownlint.jsonc, file selection in
# .markdownlint-cli2.jsonc). Silent unless something goes wrong -- purely a
# formatter, never blocks the turn.
set -uo pipefail

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root" || exit 0

file="$(jq -r '.tool_response.filePath // .tool_input.file_path // empty')"

case "$file" in
  *.md) ;;
  *) exit 0 ;;
esac

[ -f "$file" ] || exit 0

# --no-globs is required: markdownlint-cli2 otherwise merges the explicit
# file argument with .markdownlint-cli2.jsonc's "globs" (**/*.md) rather
# than replacing it, silently reformatting every Markdown file in the repo
# on every single-file edit.
if [ -x "$repo_root/node_modules/.bin/markdownlint-cli2" ]; then
  "$repo_root/node_modules/.bin/markdownlint-cli2" --no-globs --fix "$file" >/dev/null 2>&1
elif command -v markdownlint-cli2 >/dev/null 2>&1; then
  markdownlint-cli2 --no-globs --fix "$file" >/dev/null 2>&1
elif command -v npx >/dev/null 2>&1; then
  npx --yes markdownlint-cli2 --no-globs --fix "$file" >/dev/null 2>&1
fi

exit 0
