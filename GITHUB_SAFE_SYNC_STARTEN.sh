#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

echo "============================================================"
echo "OI - PROVOWARE - IO · V0.12.2.5 GITHUB SAFE REVIEW SYNC"
echo "============================================================"
echo ""
echo "Dieser Start prüft zuerst alles und schreibt NICHT auf main."
echo "Ziel: review/v0.12.2.5-real-viewport-20260829"
echo ""

./SYNC_PROVOWARE_V0.12.2.5_SAFE_REVIEW.sh "$PWD"

echo ""
echo "============================================================"
echo "SAFE REVIEW SYNC beendet."
echo "Wenn oben grün steht, ist der Draft-PR auf GitHub vorbereitet."
echo "============================================================"
