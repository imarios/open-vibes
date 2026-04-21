#!/usr/bin/env bash
# Verifies .github/badges/skills.json "message" field matches the actual
# count of skills/*/ directories. Shields.io renders that JSON as the
# "skills" badge in README; if it drifts, the badge lies.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/skills"
BADGE="$REPO_ROOT/.github/badges/skills.json"

if [ ! -d "$SKILLS_DIR" ]; then
  echo "No skills/ directory — nothing to check."
  exit 0
fi

count=0
for d in "$SKILLS_DIR"/*/; do
  [ -d "$d" ] || continue
  count=$((count + 1))
done

expected='{"schemaVersion":1,"label":"skills","message":"'"$count"'","color":"blue"}'

if [ ! -f "$BADGE" ]; then
  echo "ERROR: Missing $BADGE"
  echo ""
  echo "Create it with:"
  echo "$expected"
  exit 1
fi

actual=$(grep -oE '"message"[[:space:]]*:[[:space:]]*"[0-9]+"' "$BADGE" | grep -oE '[0-9]+' || echo "")

if [ "$actual" != "$count" ]; then
  echo "ERROR: Skill count badge out of sync."
  echo "  Skills on disk: $count"
  echo "  Badge message:  ${actual:-<missing>}"
  echo ""
  echo "Update ${BADGE#"$REPO_ROOT/"} to:"
  echo "$expected"
  exit 1
fi

echo "Skill count badge in sync ($count skills)."
