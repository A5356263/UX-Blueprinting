#!/usr/bin/env bash
set -euo pipefail

if command -v python >/dev/null 2>&1; then
  python -m packages "$@"
  exit 0
fi

if command -v python3 >/dev/null 2>&1; then
  python3 -m packages "$@"
  exit 0
fi

if command -v py >/dev/null 2>&1; then
  py -3 -m packages "$@"
  exit 0
fi

echo "Neither python, python3, nor py was found in PATH." >&2
exit 127
