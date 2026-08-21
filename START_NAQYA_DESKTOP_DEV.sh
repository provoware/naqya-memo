#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PORT="${NAQYA_PORT:-8765}"
SERVER_PID=""

cleanup() {
  if [[ -n "${SERVER_PID:-}" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

fail() {
  printf '\n[NAQYA] FEHLER: %s\n' "$1" >&2
  exit 1
}

command -v python3 >/dev/null 2>&1 || fail "python3 fehlt. Installiere Python 3."
command -v cargo >/dev/null 2>&1 || fail "Rust/Cargo fehlt. Siehe docs/NATIVE_DESKTOP.md."
[[ -f "$ROOT/src-tauri/Cargo.toml" ]] || fail "src-tauri/Cargo.toml fehlt."

printf '[NAQYA] Prüfe Port %s …\n' "$PORT"
if python3 - "$PORT" <<'PY'
import socket,sys
s=socket.socket()
try:
    s.bind(('127.0.0.1', int(sys.argv[1])))
except OSError:
    raise SystemExit(1)
finally:
    s.close()
PY
then
  :
else
  fail "Port $PORT ist bereits belegt. Setze optional NAQYA_PORT auf einen freien Port."
fi

if [[ "$PORT" != "8765" ]]; then
  fail "Tauri devUrl ist derzeit fest auf Port 8765 eingestellt. Verwende NAQYA_PORT=8765."
fi

printf '[NAQYA] Starte lokalen Offline-Frontendserver …\n'
cd "$ROOT"
python3 -m http.server "$PORT" --bind 127.0.0.1 >"${TMPDIR:-/tmp}/naqya-http.log" 2>&1 &
SERVER_PID=$!

for _ in {1..30}; do
  if python3 - "$PORT" <<'PY'
import socket,sys
s=socket.socket();s.settimeout(.2)
try:
    s.connect(('127.0.0.1', int(sys.argv[1])))
except OSError:
    raise SystemExit(1)
finally:
    s.close()
PY
  then break; fi
  sleep .1
done

kill -0 "$SERVER_PID" 2>/dev/null || fail "Frontendserver konnte nicht gestartet werden."

printf '[NAQYA] Starte Tauri + lokale whisper.cpp-Runtime …\n'
printf '[NAQYA] Beenden der Desktop-App beendet auch den Hilfsserver.\n\n'
cargo run --manifest-path "$ROOT/src-tauri/Cargo.toml"
