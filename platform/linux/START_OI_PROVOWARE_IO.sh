#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"
PY="${PYTHON:-python3}"
if ! command -v "$PY" >/dev/null 2>&1; then
  echo "FEHLER: Python 3 wurde nicht gefunden."; exit 10
fi
export PROVOWARE_PROJECT_PATH="${PROVOWARE_PROJECT_PATH:-$HERE/projektordner}"
mkdir -p "$PROVOWARE_PROJECT_PATH"
exec "$PY" app/server.py "$@"
