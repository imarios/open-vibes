#!/usr/bin/env bash
# Checks that no markdown file under skills/ declares a creation or
# modification date in its YAML frontmatter. Version is the only
# temporal marker permitted.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/skills"
BANNED='^(created|updated|date|last_modified|last_updated|modified):'

if [ ! -d "$SKILLS_DIR" ]; then
  exit 0
fi

offenders=()

while IFS= read -r -d '' md; do
  frontmatter=$(awk '
    BEGIN { in_fm = 0; count = 0 }
    /^---$/ { count++; if (count == 1) { in_fm = 1; next } else { exit } }
    in_fm { print }
  ' "$md")
  [ -z "$frontmatter" ] && continue
  if echo "$frontmatter" | grep -qiE "$BANNED"; then
    offenders+=("${md#"$REPO_ROOT/"}")
  fi
done < <(find "$SKILLS_DIR" -type f -name '*.md' -print0)

if [ ${#offenders[@]} -gt 0 ]; then
  echo "ERROR: Banned date field found in frontmatter of:"
  for f in "${offenders[@]}"; do
    echo "  - $f"
  done
  echo ""
  echo "Fields created|updated|date|last_modified|last_updated|modified are not permitted."
  echo "Use the 'version' field as the only temporal marker."
  exit 1
fi

echo "No banned date fields found in skill frontmatter."
