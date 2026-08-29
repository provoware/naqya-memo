#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
python3 "$ROOT/tools/mobile/sync_web_assets.py"
if [[ -z "${ANDROID_HOME:-${ANDROID_SDK_ROOT:-}}" ]]; then
  echo "BLOCKED: Android SDK fehlt. ANDROID_HOME oder ANDROID_SDK_ROOT setzen." >&2
  exit 2
fi
if [[ -x "$HERE/gradlew" ]]; then
  CMD=("$HERE/gradlew")
elif command -v gradle >/dev/null 2>&1; then
  CMD=(gradle)
else
  echo "BLOCKED: Weder Gradle Wrapper noch gradle im PATH. In Android Studio 'Gradle Wrapper' erzeugen oder Gradle bereitstellen." >&2
  exit 2
fi
cd "$HERE"
"${CMD[@]}" --no-daemon :app:assembleDebug :app:assembleRelease
DEBUG_APK=$(find "$HERE/app/build/outputs/apk/debug" -name '*.apk' -type f | head -1 || true)
RELEASE_APK=$(find "$HERE/app/build/outputs/apk/release" -name '*.apk' -type f | head -1 || true)
if [[ -z "$DEBUG_APK" || -z "$RELEASE_APK" ]]; then echo "FAIL: Debug- oder Release-APK fehlt." >&2; exit 1; fi
sha256sum "$DEBUG_APK" "$RELEASE_APK"
echo "ANDROID_ACCEPTANCE_APK=$DEBUG_APK"
echo "ANDROID_RELEASE_APK=$RELEASE_APK"
