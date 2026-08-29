#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
node "$ROOT/tests/mobile/test_mobile_core.mjs"
python3 -S "$ROOT/tests/mobile/test_mobile_sources.py"
node --check "$ROOT/ui/reference_web/app.js"
node --check "$ROOT/ui/reference_web/mobile/mobile_core.js"
node --check "$ROOT/ui/reference_web/mobile/mobile_bootstrap.js"
node --check "$ROOT/ui/reference_web/mobile/mobile_acceptance.js"
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
kotlinc "$ROOT/platform/android/app/src/main/java/de/provoware/naqya/BridgeEnvelope.kt" -d "$TMP/android-bridge.jar"
swiftc -parse "$ROOT/platform/ios/OIProvowareIO/BridgeContract.swift"
swiftc -frontend -parse "$ROOT/platform/ios/OIProvowareIO/AppDelegate.swift" "$ROOT/platform/ios/OIProvowareIO/NativeBridge.swift"
plutil -lint "$ROOT/platform/ios/Info.plist"
echo "MOBILE_RUNTIME_SOURCE_ACCEPTANCE=PASS"
