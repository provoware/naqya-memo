#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

export PROVOWARE_NO_BROWSER=1
REQUESTED_PORT="${PROVOWARE_PORT:-8765}"

PROFILE_ID="$(python3 -S tools/startup_profile_selector.py --root "$PWD")"
if [[ "$PROFILE_ID" == "__CANCEL__" ]]; then
  echo "🟡 Start auf Wunsch abgebrochen. Es wurde nichts verändert."
  exit 0
fi
if [[ -n "$PROFILE_ID" ]]; then
  export PROVOWARE_PROFILE_ID="$PROFILE_ID"
  echo "🟢 Profil für diesen Start ausgewählt."
fi
GUARD_JSON="$(python3 -S tools/startup_port_guard.py --root "$PWD" --requested "$REQUESTED_PORT" --evidence)"
ACTION="$(python3 -S -c 'import json,sys; print(json.load(sys.stdin)["action"])' <<<"$GUARD_JSON")"
PORT="$(python3 -S -c 'import json,sys; print(json.load(sys.stdin).get("selected_port") or "")' <<<"$GUARD_JSON")"
REASON="$(python3 -S -c 'import json,sys; print(json.load(sys.stdin).get("reason") or "")' <<<"$GUARD_JSON")"

case "$ACTION" in
  REUSE)
    URL="http://127.0.0.1:${PORT}/index.html"
    echo "🟢 OI - PROVOWARE - IO läuft bereits auf Port ${PORT}."
    echo "   Bestehende Instanz wird wiederverwendet: $URL"
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
exec python3 -S app/secure_response_server.py --no-browser
