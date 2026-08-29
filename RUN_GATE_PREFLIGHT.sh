#!/usr/bin/env bash
set -u
ROOT="$(cd "$(dirname "$0")" && pwd)"; PY="${PYTHON:-python3}"
"$PY" -S "$ROOT/tools/release_gate/gate_01_8h_soak.py" --preflight-seconds 5 || true
for n in 02_chromium 03_firefox 04_linux_microphone 05_storage_failure 06_android_device 07_ios_iphone_x; do "$PY" -S "$ROOT/tools/release_gate/gate_${n}.py" || true; done
"$PY" -S "$ROOT/tools/release_gate/evaluate_release_gate.py" || true
