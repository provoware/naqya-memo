#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
"$ROOT/platform/ios/BUILD_IOS.sh"
