#!/usr/bin/env bash
# Print the stable devflow key for the current project.
# Key = normalized git remote URL (origin), so all clones and worktrees
# of one repo share it and ssh/https forms converge. Fallback: repo
# root path (or cwd outside git), slugified.
set -euo pipefail

key=$(git remote get-url origin 2>/dev/null || true)
if [ -z "$key" ]; then
  key=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
fi
key=${key%.git}
printf '%s\n' "$key" \
  | sed -E 's|^[a-z+]+://||; s|^[^@/]*@||; s|[/:._~]+|-|g; s|^-+||; s|-+$||' \
  | tr '[:upper:]' '[:lower:]'
