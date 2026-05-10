#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -eq 0 ]; then
  echo "Usage: bash .codex/skills/scripts/validate_skills.sh <skill_dir> [<skill_dir> ...]" >&2
  exit 1
fi

export PYTHONUTF8=1
validator="C:/Users/HP/.codex/skills/.system/skill-creator/scripts/quick_validate.py"

for skill in "$@"; do
  python "$validator" "$skill"
done
