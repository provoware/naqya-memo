#!/usr/bin/env bash
# READ-ONLY preflight: do not execute native gates or modify canonical evidence.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
exec "${PYTHON:-python3}" -S "$ROOT/tools/release_gate/check_real_gate_readiness.py" "$@"
