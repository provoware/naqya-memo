#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
exec "${PYTHON:-python3}" -S "$ROOT/tools/release_gate/gate_01_8h_soak.py" --hours 8
