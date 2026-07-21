#!/usr/bin/env bash
# PostToolUse hook (Write|Edit): format + lint the touched TOML file with
# tombi. tombi isn't a project Python dependency (it's a standalone Rust
# toolchain, not imported by any code here), so it runs via `uvx` rather
# than `uv run`, pinned to a fixed version for reproducibility. Silent
# unless something goes wrong -- purely a formatter, never blocks the turn.
set -uo pipefail

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root" || exit 0

file="$(jq -r '.tool_response.filePath // .tool_input.file_path // empty')"

case "$file" in
  *.toml) ;;
  *) exit 0 ;;
esac

[ -f "$file" ] || exit 0

uvx tombi@1.2.4 format --quiet "$file" >/dev/null 2>&1
uvx tombi@1.2.4 lint --quiet "$file" >/dev/null 2>&1

exit 0
