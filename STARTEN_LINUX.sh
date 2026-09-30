#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

REQUESTED_PORT="${PROVOWARE_PORT:-8765}"
GUARD_JSON="$(python3 -S tools/startup_port_guard.py --root "$PWD" --requested "$REQUESTED_PORT" --evidence)"
ACTION="$(python3 -S -c 'import json,sys; print(json.load(sys.stdin)["action"])' <<<"$GUARD_JSON")"
PORT="$(python3 -S -c 'import json,sys; print(json.load(sys.stdin).get("selected_port") or "")' <<<"$GUARD_JSON")"
REASON="$(python3 -S -c 'import json,sys; print(json.load(sys.stdin).get("reason") or "")' <<<"$GUARD_JSON")"

case "$ACTION" in
  REUSE)
    URL="http://127.0.0.1:${PORT}/index.html"
    echo "🟢 OI - PROVOWARE - IO läuft bereits auf Port ${PORT}."
    echo "   Bestehende Instanz wird wiederverwendet: $URL"
    if [[ "${PROVOWARE_NO_BROWSER:-0}" != "1" ]]; then
      if command -v xdg-open >/dev/null 2>&1; then
        xdg-open "$URL" >/dev/null 2>&1 || true
      else
        python3 -m webbrowser "$URL" >/dev/null 2>&1 || true
      fi
    fi
    exit 0
    ;;
  START)
    if [[ "$PORT" != "$REQUESTED_PORT" ]]; then
      echo "🟡 Port ${REQUESTED_PORT} ist bereits belegt."
      echo "   Es wird NICHTS beendet. Sicherer Ersatzport: ${PORT}"
      echo "   Details: runtime/startup/LAST_START_PORT.json"
    else
      echo "🟢 Port ${PORT} ist frei."
    fi
    export PROVOWARE_PORT="$PORT"
    ;;
  *)
    echo "🔴 Start nicht möglich: $REASON"
    echo "$GUARD_JSON"
    echo
    echo "Prüfen mit:"
    echo "  ss -ltnp | grep ':${REQUESTED_PORT}'"
    exit 98
    ;;
esac

echo "🔐 Desktop-Schutz aktiv: Benutzername provoware, Passwort = Profil-PIN."
exec python3 -S app/secure_response_server.py