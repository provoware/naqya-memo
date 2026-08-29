#!/usr/bin/env bash
set -euo pipefail

REPO="provoware/naqya-memo"
MAIN_EXPECTED="de9f25f54bfbcecb008614402a0eb77745dcc1e7"
BASE_BRANCH="review/v0.12.2.4-release-ux-20260829"
BASE_EXPECTED="e3f63066e86325752ede2699082e9866d6847d83"
BACKUP_BRANCH="backup/pre-v0.12.2.5-20260829"
TARGET_BRANCH="review/v0.12.2.5-real-viewport-20260829"
VERSION="0.12.2.5-REAL-VIEWPORT-UX-FIX"

die(){ printf '\n🔴 FEHLER: %s\n' "$*" >&2; exit 1; }
info(){ printf '\n🔵 %s\n' "$*"; }
ok(){ printf '🟢 %s\n' "$*"; }

PROJECT="${1:-$PWD}"
PROJECT="$(cd "$PROJECT" && pwd)"
[[ -f "$PROJECT/registry/VERSION.json" ]] || die "Kein gültiger Projektordner: $PROJECT"

for cmd in gh git rsync python3 sha256sum node; do
  command -v "$cmd" >/dev/null 2>&1 || die "$cmd fehlt."
done

info "0/11 GitHub-Auth + Projektversion"
gh auth status --hostname github.com >/dev/null 2>&1 || die "Bitte zuerst `gh auth login` ausführen."
[[ "$(gh api repos/$REPO --jq '.permissions.push // false')" == "true" ]] || die "Kein Push-Zugriff."
ACTUAL="$(python3 -S - "$PROJECT/registry/VERSION.json" <<'PY'
import json,sys
print(json.load(open(sys.argv[1],encoding='utf-8'))['version'])
PY
)"
[[ "$ACTUAL" == "$VERSION" ]] || die "Falsche Version: $ACTUAL"
ok "Auth und Version korrekt."

info "1/11 Remote-Grenzen beweisen"
MAIN="$(gh api repos/$REPO/git/ref/heads/main --jq '.object.sha')"
BASE="$(gh api repos/$REPO/git/ref/heads/$BASE_BRANCH --jq '.object.sha')"
BACKUP="$(gh api repos/$REPO/git/ref/heads/$BACKUP_BRANCH --jq '.object.sha')"
TARGET="$(gh api repos/$REPO/git/ref/heads/$TARGET_BRANCH --jq '.object.sha')"
[[ "$MAIN" == "$MAIN_EXPECTED" ]] || die "main drift: $MAIN"
[[ "$BASE" == "$BASE_EXPECTED" ]] || die "V0.12.2.4 Review drift: $BASE"
[[ "$BACKUP" == "$BASE_EXPECTED" ]] || die "Pre-V0.12.2.5 Backup drift: $BACKUP"
[[ "$TARGET" == "$BASE_EXPECTED" ]] || die "V0.12.2.5 Reviewbranch ist nicht jungfräulich: $TARGET"
ok "Main, Basis, Backup und Zielbranch exakt wie erwartet."

info "2/11 Lokale Acceptance-Evidence prüfen"
python3 -S - "$PROJECT/registry/evidence/v0.12.2.5/REAL_VIEWPORT_UX_ACCEPTANCE.json" <<'PY'
import json,sys
x=json.load(open(sys.argv[1],encoding='utf-8'))
assert x['status']=='PASS'
assert x['passed']==x['total']
assert x['offline_browser_geometry']['status']=='PASS'
assert x['real_loopback_browser_e2e']=='STILL_REQUIRED_ON_REAL_LINUX'
print(f"Acceptance: {x['passed']}/{x['total']} PASS; echtes Loopback-E2E bleibt offen.")
PY

info "3/11 Kritische Source-Regression erneut prüfen"
cd "$PROJECT"
python3 -S tests/ui_consistency/test_v01222_static_ui_consistency.py
python3 -S tests/ui_consistency/test_v01223_simplification_guidance.py
python3 -S tests/ui_consistency/test_v01224_ux_control_plane.py
python3 -S tests/ui_consistency/test_v01225_real_viewport_ux.py
node --check ui/reference_web/app.js
ok "Source-Regression grün."

info "4/11 Echtes Loopback-Visual-E2E automatisch versuchen"
set +e
"$PROJECT/RUN_VISUAL_ACCEPTANCE_LINUX.sh"
VISUAL_RC=$?
set -e
case "$VISUAL_RC" in
  0)
    ok "Reales Loopback-Visual-E2E PASS."
    ;;
  3)
    echo "🟡 Reales Visual-E2E BLOCKED, weil lokale Testwerkzeuge/Browser nicht verfügbar sind."
    echo "   Kein falsches PASS; Source-Review darf fortgesetzt werden."
    ;;
  *)
    die "Reales Loopback-Visual-E2E hat einen echten Fehler gefunden. GitHub-Push wird blockiert."
    ;;
esac

info "5/11 Secrets prüfen"
SECRET_FILES="$(find "$PROJECT" -type f \( \
  -name '.env' -o -name '.env.*' -o -name '*.pem' -o -name '*.p12' \
  -o -name '*.pfx' -o -name '*.jks' -o -name '*.keystore' \
\) -not -path '*/runtime/*' -print || true)"
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

info "6/11 Temporären Clone erzeugen"
TMP="$(mktemp -d -t provoware-v01225-XXXXXX)"
trap 'rm -rf "$TMP"' EXIT
gh repo clone "$REPO" "$TMP/repo" -- --quiet
cd "$TMP/repo"
git fetch --quiet origin main "$BASE_BRANCH" "$BACKUP_BRANCH" "$TARGET_BRANCH"
git checkout --quiet -B "$TARGET_BRANCH" "origin/$TARGET_BRANCH"

info "7/11 V0.12.2.5 spiegeln"
find . -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {} +
rsync -a \
  --exclude='.git/' \
  --exclude='runtime/' \
  --exclude='__pycache__/' \
  --exclude='*.pyc' \
  --exclude='.pytest_cache/' \
  --exclude='.mypy_cache/' \
  --exclude='.ruff_cache/' \
  --exclude='registry/evidence/v0.12.2.5/offline-geometry/*.png' \
  "$PROJECT/" ./

info "8/11 GitHub-Dateimanifest erzeugen und validieren"
mkdir -p registry
find . -type f ! -path './.git/*' ! -path './registry/GITHUB_V0.12.2.5_FILESET_SHA256.txt' \
  -print0 | sort -z | xargs -0 sha256sum > registry/GITHUB_V0.12.2.5_FILESET_SHA256.txt
sha256sum -c registry/GITHUB_V0.12.2.5_FILESET_SHA256.txt >/dev/null

git add -A
COUNT="$(git diff --cached --name-only | wc -l)"
[[ "$COUNT" -gt 0 ]] || die "Kein Diff gefunden."
[[ "$(git branch --show-current)" == "$TARGET_BRANCH" ]] || die "Branchschutz verletzt."

CONFLICTS="$(mktemp)"
grep -RInE --exclude-dir=.git --exclude='*.zip' --exclude='*.gz' \
  '^(<<<<<<< |=======|>>>>>>> )' . >"$CONFLICTS" 2>/dev/null || true
if [[ -s "$CONFLICTS" ]]; then cat "$CONFLICTS" >&2; rm -f "$CONFLICTS"; die "Merge-Konfliktmarker gefunden."; fi
rm -f "$CONFLICTS"
ok "$COUNT geänderte/ergänzte Pfade, Hashmanifest grün."

info "9/11 Commit + Push ausschließlich Reviewbranch"
git -c user.name='PROVOWARE Safe Sync' \
    -c user.email='provoware.one@gmail.com' \
    commit -m "ux: V0.12.2.5 real viewport and high-magnification hardening"
LOCAL_SHA="$(git rev-parse HEAD)"
git push origin "HEAD:refs/heads/$TARGET_BRANCH"

REMOTE="$(gh api repos/$REPO/git/ref/heads/$TARGET_BRANCH --jq '.object.sha')"
[[ "$REMOTE" == "$LOCAL_SHA" ]] || die "Remote-SHA stimmt nicht."
[[ "$(gh api repos/$REPO/git/ref/heads/main --jq '.object.sha')" == "$MAIN_EXPECTED" ]] || die "main verändert."
[[ "$(gh api repos/$REPO/git/ref/heads/$BASE_BRANCH --jq '.object.sha')" == "$BASE_EXPECTED" ]] || die "V0.12.2.4 Review verändert."
[[ "$(gh api repos/$REPO/git/ref/heads/$BACKUP_BRANCH --jq '.object.sha')" == "$BASE_EXPECTED" ]] || die "Backup verändert."
ok "Reviewbranch gepusht; Main/Basis/Backup unverändert."

info "10/11 Draft-PR gegen V0.12.2.4 Review erzeugen"
PR="$(gh pr list --repo "$REPO" --head "$TARGET_BRANCH" --state open --json number --jq '.[0].number // empty')"
if [[ -z "$PR" ]]; then
  URL="$(gh pr create \
    --repo "$REPO" \
    --base "$BASE_BRANCH" \
    --head "$TARGET_BRANCH" \
    --draft \
    --title "V0.12.2.5 Real Viewport UX Fix" \
    --body "## Zweck

Screenshot-getriebene Release-UX-Härtung auf Basis von V0.12.2.4.

### Behoben
- linke Navigation lesbar + einklappbar
- keine buchstabenweisen Menüumbrüche
- Ansicht-Steuerung mit eigener voller Headerzeile
- Technik als eigener Drawer
- kompakte/einklappbare Infoleiste
- kompakteres Dashboard
- 150/200-%-High-Magnification-Modus
- mobile Schnellleiste ohne horizontalen Overflow

### Evidence
- gezielte Regression: 89/89 PASS
- Offline-Chromium-Geometrie: 8/8 PASS
- PNGs bleiben reproduzierbar im Voll-ZIP; GitHub enthält Runner + JSON-Bericht

### Sperre
Reales Loopback-Browser-E2E bleibt offen.
Release bleibt NO-GO / 1 von 7.

**Draft lassen, bis PR #56 geklärt, CI grün und reales Linux-Visual-E2E geprüft ist.**")"
  PR="${URL##*/}"
fi

info "11/11 Ergebnis"
echo
echo "════════════════════════════════════════════════════════"
echo "🟢 V0.12.2.5 SAFE REVIEW SYNC ERFOLGREICH"
echo "Branch:       $TARGET_BRANCH"
echo "Commit:       $REMOTE"
echo "Draft-PR:     #$PR"
echo "Basis V0.12.2.4: $BASE_EXPECTED (UNVERÄNDERT)"
echo "Backup:       $BACKUP_BRANCH (UNVERÄNDERT)"
echo "main:         $MAIN_EXPECTED (UNVERÄNDERT)"
echo "Release:      NO-GO / 1 von 7"
echo "════════════════════════════════════════════════════════"
