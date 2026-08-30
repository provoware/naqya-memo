#!/usr/bin/env bash
set -u
ROOT="$(cd "$(dirname "$0")" && pwd)"
PY="${PYTHON:-python3}"
export PROVOWARE_RELEASE_GATE_STARTED_AT="$("$PY" -S -c 'import datetime; print(datetime.datetime.now(datetime.timezone.utc).isoformat())')"
run(){ echo; echo "===== $1 ====="; shift; "$@"; rc=$?; echo "RC=$rc"; return 0; }
run "01 8H SOAK" "$PY" -S "$ROOT/tools/release_gate/gate_01_8h_soak.py" --hours 8
run "02 CHROMIUM" "$PY" -S "$ROOT/tools/release_gate/gate_02_chromium.py"
run "03 FIREFOX" "$PY" -S "$ROOT/tools/release_gate/gate_03_firefox.py"
run "04 LINUX MICROPHONE" "$PY" -S "$ROOT/tools/release_gate/gate_04_linux_microphone.py"
run "05 STORAGE FAILURE" "$PY" -S "$ROOT/tools/release_gate/gate_05_storage_failure.py"
run "06 ANDROID DEVICE" "$PY" -S "$ROOT/tools/release_gate/gate_06_android_device.py"
run "07 IOS IPHONE X" "$PY" -S "$ROOT/tools/release_gate/gate_07_ios_iphone_x.py"
"$PY" -S "$ROOT/tools/release_gate/evaluate_release_gate.py"
