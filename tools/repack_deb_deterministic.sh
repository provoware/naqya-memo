#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Verwendung: $0 <eingabe.deb> <ausgabe.deb>" >&2
  exit 2
fi

INPUT="$(realpath "$1")"
OUTPUT="$(realpath -m "$2")"
SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-946684800}"

command -v dpkg-deb >/dev/null || { echo "FEHLER: dpkg-deb fehlt." >&2; exit 3; }
command -v sha256sum >/dev/null || { echo "FEHLER: sha256sum fehlt." >&2; exit 3; }
command -v realpath >/dev/null || { echo "FEHLER: realpath fehlt." >&2; exit 3; }
[[ -f "$INPUT" ]] || { echo "FEHLER: Eingabepaket fehlt: $INPUT" >&2; exit 4; }
[[ "$SOURCE_DATE_EPOCH" =~ ^[0-9]+$ ]] || { echo "FEHLER: SOURCE_DATE_EPOCH muss eine Ganzzahl sein." >&2; exit 5; }

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
ROOT="$WORK/root"
FIRST="$WORK/first.deb"
SECOND="$WORK/second.deb"
mkdir -p "$ROOT" "$(dirname "$OUTPUT")"

dpkg-deb -R "$INPUT" "$ROOT"

# ENTWICKLERHINWEIS: Manche Dateisysteme vererben setgid; dpkg-deb lehnt DEBIAN/ mit 2755 ab.
chmod g-s "$ROOT/DEBIAN" || true
chmod 0755 "$ROOT/DEBIAN"

# Archivzeitstempel auf denselben reproduzierbaren Zeitpunkt normieren.
find "$ROOT" -exec touch -h -d "@$SOURCE_DATE_EPOCH" {} +

build_once() {
  local target="$1"
  SOURCE_DATE_EPOCH="$SOURCE_DATE_EPOCH" \
    dpkg-deb --build --root-owner-group --uniform-compression -Zgzip -z9 \
    "$ROOT" "$target" >/dev/null
}

# Zweimal bauen und bytegenau vergleichen: Der Repacker muss bereits innerhalb eines Laufs deterministisch sein.
build_once "$FIRST"
build_once "$SECOND"
cmp -s "$FIRST" "$SECOND" || {
  echo "FEHLER: Deterministisches DEB-Repacking lieferte unterschiedliche Bytes." >&2
  exit 6
}

install -m 0644 "$FIRST" "$OUTPUT"
HASH="$(sha256sum "$OUTPUT" | awk '{print $1}')"
printf 'NAQYA deterministisches DEB-Repacking: PASS\n'
printf 'SOURCE_DATE_EPOCH: %s\n' "$SOURCE_DATE_EPOCH"
printf 'Ausgabe: %s\n' "$OUTPUT"
printf 'SHA-256: %s\n' "$HASH"
