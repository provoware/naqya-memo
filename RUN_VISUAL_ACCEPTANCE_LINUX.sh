#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
echo "OI - PROVOWARE - IO · reale V0.12.2.4 UI-Abnahme"
echo "Prüft alle Kernansichten bei Desktop 100/150/200 %, kompakt und Mobile."
python3 tests/ui_consistency/run_v01224_all_views_visual_acceptance.py
echo "Evidence: registry/evidence/v0.12.2.4/browser/ALL_VIEWS_VISUAL_ACCEPTANCE.json"
