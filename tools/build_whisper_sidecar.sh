#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="$ROOT_DIR/src-tauri/sidecar/whisper-runtime.json"
WORK_DIR="${NAQYA_SIDECAR_WORK_DIR:-$ROOT_DIR/.sidecar-build}"
SRC_DIR="$WORK_DIR/whisper.cpp"
BUILD_DIR="$WORK_DIR/build"
BIN_DIR="$ROOT_DIR/src-tauri/binaries"

# ENTWICKLERHINWEIS: Tag und Commit bilden gemeinsam den Supply-Chain-Vertrag; Änderungen nur synchron mit Manifest, Tests und Doku.
UPSTREAM_REPO="https://github.com/ggml-org/whisper.cpp.git"
UPSTREAM_TAG="v1.9.2"
UPSTREAM_COMMIT="306c88f4d1286aec1bf96e544632897886af5501"

command -v git >/dev/null || { echo "FEHLER: git fehlt." >&2; exit 2; }
command -v cmake >/dev/null || { echo "FEHLER: cmake fehlt." >&2; exit 2; }
command -v sha256sum >/dev/null || { echo "FEHLER: sha256sum fehlt." >&2; exit 2; }
command -v rustc >/dev/null || { echo "FEHLER: rustc fehlt; Zielplattform kann nicht bestimmt werden." >&2; exit 2; }

TARGET_TRIPLE="$(rustc --print host-tuple 2>/dev/null || rustc -vV | awk '/^host:/ {print $2}')"
[[ -n "$TARGET_TRIPLE" ]] || { echo "FEHLER: Rust-Zielplattform nicht bestimmbar." >&2; exit 3; }

case "$TARGET_TRIPLE" in
  x86_64-unknown-linux-gnu)
    OUTPUT="$BIN_DIR/naqya-whisper-$TARGET_TRIPLE"
    ;;
  x86_64-pc-windows-msvc)
    OUTPUT="$BIN_DIR/naqya-whisper-$TARGET_TRIPLE.exe"
    ;;
  *)
    echo "FEHLER: Zielplattform $TARGET_TRIPLE ist im NAQYA-Sidecar-Vertrag noch nicht freigegeben." >&2
    exit 4
    ;;
esac

rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR" "$BIN_DIR"
git clone --filter=blob:none --no-checkout "$UPSTREAM_REPO" "$SRC_DIR"
git -C "$SRC_DIR" fetch --depth 1 origin "refs/tags/$UPSTREAM_TAG:refs/tags/$UPSTREAM_TAG"
git -C "$SRC_DIR" checkout --detach "$UPSTREAM_TAG"

ACTUAL_COMMIT="$(git -C "$SRC_DIR" rev-parse HEAD)"
[[ "$ACTUAL_COMMIT" == "$UPSTREAM_COMMIT" ]] || {
  echo "FEHLER: Upstream-Commit stimmt nicht mit dem NAQYA-Vertrag überein." >&2
  echo "Soll: $UPSTREAM_COMMIT" >&2
  echo "Ist:  $ACTUAL_COMMIT" >&2
  exit 5
}

cmake -S "$SRC_DIR" -B "$BUILD_DIR" -DCMAKE_BUILD_TYPE=Release -DGGML_NATIVE=OFF
cmake --build "$BUILD_DIR" --config Release --target whisper-cli -j "${NAQYA_BUILD_JOBS:-2}"

if [[ -f "$BUILD_DIR/bin/whisper-cli" ]]; then
  BUILT="$BUILD_DIR/bin/whisper-cli"
elif [[ -f "$BUILD_DIR/bin/Release/whisper-cli.exe" ]]; then
  BUILT="$BUILD_DIR/bin/Release/whisper-cli.exe"
else
  echo "FEHLER: whisper-cli wurde nach dem Build nicht gefunden." >&2
  exit 6
fi

install -m 0755 "$BUILT" "$OUTPUT"
HASH="$(sha256sum "$OUTPUT" | awk '{print $1}')"
printf '%s  %s\n' "$HASH" "$(basename "$OUTPUT")" > "$OUTPUT.sha256"

printf 'NAQYA whisper.cpp Sidecar vorbereitet\n'
printf 'Manifest: %s\n' "$MANIFEST"
printf 'Upstream: %s @ %s\n' "$UPSTREAM_TAG" "$UPSTREAM_COMMIT"
printf 'Ziel: %s\n' "$TARGET_TRIPLE"
printf 'Binary: %s\n' "$OUTPUT"
printf 'SHA-256: %s\n' "$HASH"
