#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
export PROVOWARE_PROJECT_PATH="${PROVOWARE_PROJECT_PATH:-$HERE/projektordner}"
export PROVOWARE_PORT="${PROVOWARE_PORT:-8765}"
mkdir -p "$PROVOWARE_PROJECT_PATH"
exec python3 "$HERE/app/server.py"
