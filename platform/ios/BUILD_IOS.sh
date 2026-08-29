#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
python3 "$ROOT/tools/mobile/sync_web_assets.py"
if [[ "$(uname -s)" != "Darwin" ]] || ! command -v xcodebuild >/dev/null 2>&1; then
  echo "BLOCKED: iOS Build benötigt macOS mit Xcode." >&2
  exit 2
fi
DERIVED="$HERE/build/DerivedData"
mkdir -p "$DERIVED"
ARGS=(-project "$HERE/OIProvowareIO.xcodeproj" -target OIProvowareIO -configuration Release -sdk iphoneos -derivedDataPath "$DERIVED")
if [[ -n "${PROVOWARE_DEVELOPMENT_TEAM:-}" ]]; then
  ARGS+=(DEVELOPMENT_TEAM="$PROVOWARE_DEVELOPMENT_TEAM" CODE_SIGN_STYLE=Automatic)
else
  ARGS+=(CODE_SIGNING_ALLOWED=NO)
fi
xcodebuild "${ARGS[@]}" build
APP=$(find "$DERIVED" -type d -name 'OIProvowareIO.app' | head -1 || true)
if [[ -z "$APP" ]]; then echo "FAIL: Kein .app erzeugt." >&2; exit 1; fi
echo "IOS_APP=$APP"
