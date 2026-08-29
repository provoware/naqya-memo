#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
echo "OI - PROVOWARE - IO · reale V0.12.2.5 Browser-/Viewport-Abnahme"
echo "Prüft Kernansichten mit echtem Loopback-Service bei Desktop 100/150/200 %, kompakt und Mobile."
python3 tests/ui_consistency/run_v01225_all_views_visual_acceptance.py
echo "Evidence: registry/evidence/v0.12.2.5/browser/ALL_VIEWS_VISUAL_ACCEPTANCE.json"
