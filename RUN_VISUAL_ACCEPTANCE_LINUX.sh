#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
echo "OI - PROVOWARE - IO · reale UI-Abnahme"
echo "Prüft 10 Ansichten bei Desktop 100/150/200 %, kompakt und Mobile."
python3 tests/ui_consistency/run_v01223_all_views_visual_acceptance.py
echo "Evidence: registry/evidence/v0.12.2.3/browser/ALL_VIEWS_VISUAL_ACCEPTANCE.json"
