#!/usr/bin/env bash
# Checks that every skill directory under skills/ has a corresponding row
# in the README.md skills table. Exits non-zero if any are missing.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
README="$REPO_ROOT/README.md"
SKILLS_DIR="$REPO_ROOT/skills"

if [ ! -d "$SKILLS_DIR" ]; then
  echo "No skills/ directory found — nothing to check."
  exit 0
fi

missing=()

for skill_dir in "$SKILLS_DIR"/*/; do
  [ -d "$skill_dir" ] || continue
  skill_name="$(basename "$skill_dir")"
  if ! grep -q "| \[${skill_name}\]" "$README"; then
    missing+=("$skill_name")
  fi
done

if [ ${#missing[@]} -gt 0 ]; then
  echo "ERROR: The following skills are not listed in README.md:"
  for name in "${missing[@]}"; do
    echo "  - $name"
  done
  echo ""
  echo "Add a row for each missing skill to the Skills table in README.md."
  exit 1
fi

echo "README skills table is up to date."
