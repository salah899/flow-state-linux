#!/usr/bin/env bash
# Writes the whole project source into ONE text file: PROJECT_SOURCE.txt
# (useful to share the project where .zip uploads are not accepted).
set -euo pipefail
cd "$(dirname "$0")/.."
OUT="PROJECT_SOURCE.txt"
{
  echo "# Flow State - full project source"
  echo "# Generated: $(date '+%Y-%m-%d %H:%M')"
  echo
  echo "## File tree"
  find . -type f \( -name "*.py" -o -name "*.sh" -o -name "*.md" -o -name "*.txt" -o -name "*.ini" -o -name ".gitignore" \) \
    -not -path "./.venv/*" -not -path "*/__pycache__/*" -not -path "./build/*" -not -path "./dist/*" \
    -not -name "$OUT" | sort
  find . -type f \( -name "*.py" -o -name "*.sh" -o -name "*.md" -o -name "*.txt" -o -name "*.ini" -o -name ".gitignore" \) \
    -not -path "./.venv/*" -not -path "*/__pycache__/*" -not -path "./build/*" -not -path "./dist/*" \
    -not -name "$OUT" | sort | while read -r f; do
      printf '\n===== FILE: %s =====\n' "$f"
      cat "$f"
  done
} > "$OUT"
echo "Wrote $OUT ($(wc -l < "$OUT") lines)"
