#!/usr/bin/env bash
set -euo pipefail

REPO="provoware/naqya-memo"
MAIN_EXPECTED="a05ea824499ca16c1b0bb5141853c19d8d7a035e"
BASE_BRANCH="backup/pre-v0.12.2.4-20260829"
BASE_EXPECTED="a05ea824499ca16c1b0bb5141853c19d8d7a035e"
TARGET_BRANCH="review/v0.12.2.4-release-ux-20260829"
VERSION="0.12.2.4-RELEASE-UX-CONTROL-PLANE"

die(){ printf '\n🔴 FEHLER: %s\n' "$*" >&2; exit 1; }
info(){ printf '\n🔵 %s\n' "$*"; }
ok(){ printf '🟢 %s\n' "$*"; }

PROJECT="${1:-$PWD}"
PROJECT="$(cd "$PROJECT" && pwd)"
[[ -f "$PROJECT/registry/VERSION.json" ]] || die "Kein gültiger Projektordner: $PROJECT"

for cmd in gh git rsync python3 sha256sum; do
  command -v "$cmd" >/dev/null 2>&1 || die "$cmd fehlt."
done

info "0/9 GitHub-Auth und Projektversion"
gh auth status --hostname github.com >/dev/null 2>&1 || die "Bitte zuerst `gh auth login` ausführen."
PUSH="$(gh api repos/$REPO --jq '.permissions.push // false')"
[[ "$PUSH" == "true" ]] || die "Kein Push-Zugriff auf $REPO."
ACTUAL="$(python3 -S - "$PROJECT/registry/VERSION.json" <<'PY'
import json,sys
print(json.load(open(sys.argv[1],encoding='utf-8'))['version'])
PY
)"
[[ "$ACTUAL" == "$VERSION" ]] || die "Falsche Version: $ACTUAL"
ok "Authentifiziert und richtige V0.12.2.4 geladen."

info "1/9 Remote-Grenzen beweisen"
MAIN="$(gh api repos/$REPO/git/ref/heads/main --jq '.object.sha')"
BASE="$(gh api repos/$REPO/git/ref/heads/$BASE_BRANCH --jq '.object.sha')"
[[ "$MAIN" == "$MAIN_EXPECTED" ]] || die "main drift: $MAIN"
[[ "$BASE" == "$BASE_EXPECTED" ]] || die "Pre-V0.12.2.4-Backup drift: $BASE"

TARGET="$(gh api repos/$REPO/git/ref/heads/$TARGET_BRANCH --jq '.object.sha' 2>/dev/null || true)"
if [[ -z "$TARGET" ]]; then
  gh api -X POST repos/$REPO/git/refs \
    -f ref="refs/heads/$TARGET_BRANCH" \
    -f sha="$BASE_EXPECTED" >/dev/null
  TARGET="$BASE_EXPECTED"
fi
[[ "$TARGET" == "$BASE_EXPECTED" ]] || die "Review-Branch ist nicht jungfräulich: $TARGET"
ok "main und V0.12.2.3-Backup unverändert; neuer Review-Branch sauber."

info "2/9 Secrets prüfen"
SECRET_FILES="$(find "$PROJECT" -type f \( -name '.env' -o -name '.env.*' -o -name '*.pem' -o -name '*.p12' -o -name '*.pfx' -o -name '*.jks' -o -name '*.keystore' \) -not -path '*/runtime/*' -print || true)"
[[ -z "$SECRET_FILES" ]] || { printf '%s\n' "$SECRET_FILES" >&2; die "Secret-Datei gefunden."; }

HITS="$(mktemp)"
if grep -RIlE --exclude-dir=.git --exclude-dir=runtime --exclude-dir=__pycache__ \
  --exclude='*.zip' --exclude='*.gz' --exclude='*.tar' \
  '(-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----|github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16})' \
  "$PROJECT" >"$HITS" 2>/dev/null; then
  cat "$HITS" >&2; rm -f "$HITS"; die "Token/Schlüssel-Muster gefunden."
fi
rm -f "$HITS"
ok "Secret-Scan grün."

info "3/9 Temporären Clone erzeugen"
TMP="$(mktemp -d -t provoware-v01224-XXXXXX)"
trap 'rm -rf "$TMP"' EXIT
gh repo clone "$REPO" "$TMP/repo" -- --quiet
cd "$TMP/repo"
git fetch --quiet origin "$BASE_BRANCH" "$TARGET_BRANCH" main
git checkout --quiet -B "$TARGET_BRANCH" "origin/$TARGET_BRANCH"

info "4/9 V0.12.2.4 spiegeln"
find . -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {} +
rsync -a \
  --exclude='.git/' \
  --exclude='runtime/' \
  --exclude='__pycache__/' \
  --exclude='*.pyc' \
  --exclude='.pytest_cache/' \
  --exclude='.mypy_cache/' \
  --exclude='.ruff_cache/' \
  "$PROJECT/" ./

info "5/9 SHA-Manifest erzeugen"
mkdir -p registry
find . -type f ! -path './.git/*' ! -path './registry/GITHUB_V0.12.2.4_FILESET_SHA256.txt' \
  -print0 | sort -z | xargs -0 sha256sum > registry/GITHUB_V0.12.2.4_FILESET_SHA256.txt
sha256sum -c registry/GITHUB_V0.12.2.4_FILESET_SHA256.txt >/dev/null
ok "SHA-Manifest lokal vollständig verifiziert."

info "6/9 Konflikte und Diff prüfen"
git add -A
[[ "$(git branch --show-current)" == "$TARGET_BRANCH" ]] || die "Branchschutz verletzt."
COUNT="$(git diff --cached --name-only | wc -l)"
[[ "$COUNT" -gt 0 ]] || die "Keine Änderungen gefunden."

CONFLICTS="$(mktemp)"
grep -RInE --exclude-dir=.git --exclude='*.zip' --exclude='*.gz' \
  '^(<<<<<<< |=======|>>>>>>> )' . >"$CONFLICTS" 2>/dev/null || true
if [[ -s "$CONFLICTS" ]]; then cat "$CONFLICTS" >&2; rm -f "$CONFLICTS"; die "Merge-Konfliktmarker gefunden."; fi
rm -f "$CONFLICTS"
echo "Geänderte/ersetzte Pfade: $COUNT"

info "7/9 Commit erzeugen"
git -c user.name='PROVOWARE Safe Sync' \
    -c user.email='provoware.one@gmail.com' \
    commit -m "ux: V0.12.2.4 release hierarchy and GitHub control plane"
LOCAL_SHA="$(git rev-parse HEAD)"
echo "Lokaler Commit: $LOCAL_SHA"

info "8/9 Nur Review-Branch pushen und Remote beweisen"
git push origin "HEAD:refs/heads/$TARGET_BRANCH"
REMOTE="$(gh api repos/$REPO/git/ref/heads/$TARGET_BRANCH --jq '.object.sha')"
[[ "$REMOTE" == "$LOCAL_SHA" ]] || die "Remote-SHA stimmt nicht."
[[ "$(gh api repos/$REPO/git/ref/heads/main --jq '.object.sha')" == "$MAIN_EXPECTED" ]] || die "main wurde verändert."
[[ "$(gh api repos/$REPO/git/ref/heads/$BASE_BRANCH --jq '.object.sha')" == "$BASE_EXPECTED" ]] || die "Pre-V0.12.2.4-Backup wurde verändert."
ok "V0.12.2.4 liegt isoliert auf Review-Branch; main und V0.12.2.3 unverändert."

info "9/9 Draft-PR erzeugen"
PR="$(gh pr list --repo "$REPO" --head "$TARGET_BRANCH" --state open --json number --jq '.[0].number // empty')"
if [[ -z "$PR" ]]; then
  URL="$(gh pr create --repo "$REPO" --base main --head "$TARGET_BRANCH" --draft \
    --title "V0.12.2.4 Release UX + GitHub Control Plane" \
    --body "## Zweck

Release-Freeze-Härtung ohne neue Produktfunktion.

### UX
- klarere Navigation und visuelle Hierarchie
- kontextspezifische Orientierung
- Hilfetiefe statt dauerhafter Hinweisflut
- reduzierte Footer-/Statuskomplexität
- 44px Touch-/Fokusziele und Reduced Motion

### GitHub Control Plane
- .gitignore / .gitattributes / .editorconfig
- neuer Source-Contract-Workflow
- CONTRIBUTING + LAIENANLEITUNG
- historische 0.5.1-E7-Evidence bleibt über Backupbranches erhalten

### Sperre
Release bleibt NO-GO / 1 von 7. Reale Browser-/Android-/iOS-/Mikrofongates werden durch CI nicht ersetzt.

**Draft lassen, bis CI + realer Visual-Runner grün und der Architektur-Diff erneut auditiert sind.**")"
  PR="${URL##*/}"
fi

echo
echo "════════════════════════════════════════════════════════"
echo "🟢 V0.12.2.4 SAFE REVIEW SYNC ERFOLGREICH"
echo "Branch: $TARGET_BRANCH"
echo "Commit: $REMOTE"
echo "Draft-PR: #$PR"
echo "main: $MAIN_EXPECTED (UNVERÄNDERT)"
echo "Pre-V0.12.2.4 Backup: $BASE_EXPECTED (UNVERÄNDERT)"
echo "Release: NO-GO / 1 von 7"
echo "════════════════════════════════════════════════════════"
