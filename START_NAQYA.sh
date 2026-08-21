#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PORT="${NAQYA_PORT:-8765}"
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 fehlt. Installiere python3 oder öffne NAQYA über einen lokalen Webserver."
  read -r -p "Enter zum Beenden ..."
  exit 1
fi
python3 -m http.server "$PORT" --bind 127.0.0.1 >/tmp/naqya-memo-server.log 2>&1 &
PID=$!
trap 'kill "$PID" 2>/dev/null || true' EXIT
sleep 1
if command -v xdg-open >/dev/null 2>&1; then xdg-open "http://127.0.0.1:$PORT" >/dev/null 2>&1 || true; fi
echo "NAQYA läuft lokal unter http://127.0.0.1:$PORT"
echo "Dieses Fenster offen lassen. Strg+C beendet den lokalen Server."
wait "$PID"
