#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
trap 'rc=$?; echo; echo "🔴 Sicherer Start fehlgeschlagen."; echo "   Schritt: ${BASH_COMMAND}"; echo "   Fehlercode: ${rc}"; exit "$rc"' ERR

echo "🟦 PROVOWARE Schnellstart"
command -v python3 >/dev/null 2>&1 || { echo "🔴 Python 3 fehlt. Benötigt wird Python 3.12.x."; exit 90; }
python3 - <<'PY'
import sys
if sys.version_info[:2] != (3,12):
    raise SystemExit(f"Python {sys.version.split()[0]} erkannt; benötigt wird Python 3.12.x.")
print(f"🟢 Python {sys.version.split()[0]}")
PY
[[ -f requirements.txt ]] || { echo "🔴 requirements.txt fehlt."; exit 91; }
python3 - <<'PY'
from pathlib import Path
lines=[x.strip() for x in Path('requirements.txt').read_text(encoding='utf-8').splitlines() if x.strip() and not x.lstrip().startswith('#')]
bad=[x for x in lines if '==' not in x]
if bad: raise SystemExit('Nicht exakt versionierte Runtime-Abhängigkeit(en): '+', '.join(bad))
if lines: raise SystemExit('Dieser Naqya-Stand ist stdlib-only; externe Runtime-Pakete sind nicht zulässig.')
print('🟢 Runtime-Abhängigkeiten: keine externen Python-Pakete')
PY
[[ -x STARTEN_LINUX.sh ]] || { echo "🔴 STARTEN_LINUX.sh fehlt oder ist nicht ausführbar."; exit 92; }
echo "🟢 Vorprüfung bestanden. Tool wird gestartet und automatisch geöffnet."
exec "$ROOT/STARTEN_LINUX.sh"
