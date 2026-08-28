#!/usr/bin/env bash
set -euo pipefail

# OI - PROVOWARE - IO
# V0.12.2.3 SAFE FULL TREE SYNC
#
# Sicherheitsregeln:
# - KEIN Push auf main.
# - KEIN --force.
# - historischer main muss exakt dem erwarteten Commit entsprechen.
# - Backup-Branch muss existieren.
# - Snapshot-Branch muss existieren.
# - offensichtliche Secret-Dateien oder Secret-Muster blockieren den Lauf.
# - runtime/ und Python-Caches werden NICHT als Quellbackup synchronisiert.
# - der vollständige Projekt-Quellbaum inkl. dist-Artefakten wird auf den Safe-State-Branch gespiegelt.

REPO_URL="${PROVOWARE_GITHUB_REPO:-https://github.com/provoware/naqya-memo.git}"
REPO_SLUG="provoware/naqya-memo"
EXPECTED_MAIN="334dd2923fc01a633946137d71fdbebae34364da"
BACKUP_BRANCH="backup/pre-v0.12.2.3-20260829"
SYNC_BRANCH="sync/v0.12.2.3-safe-state-20260829"
VERSION="0.12.2.3-UI-SIMPLIFICATION-INPUT-GUIDANCE"

die(){ printf '\n🔴 FEHLER: %s\n' "$*" >&2; exit 1; }
info(){ printf '\n🔵 %s\n' "$*"; }
ok(){ printf '🟢 %s\n' "$*"; }

[[ $# -eq 1 ]] || die "Projektordner angeben: $0 /pfad/zum/V0.12.2.3-Projekt"
PROJECT="$(cd "$1" && pwd)"

for cmd in git rsync sha256sum python3; do
  command -v "$cmd" >/dev/null 2>&1 || die "$cmd fehlt."
done

[[ -f "$PROJECT/registry/VERSION.json" ]] || die "registry/VERSION.json fehlt."
ACTUAL_VERSION="$(python3 -S - "$PROJECT/registry/VERSION.json" <<'PY'
import json,sys
print(json.load(open(sys.argv[1],encoding="utf-8"))["version"])
PY
)"
[[ "$ACTUAL_VERSION" == "$VERSION" ]] || die "Falsche Projektversion: $ACTUAL_VERSION"

info "1/8 GitHub-Remote und Schutzgrenzen prüfen"
REMOTE_MAIN="$(git ls-remote "$REPO_URL" refs/heads/main | awk '{print $1}')"
[[ "$REMOTE_MAIN" == "$EXPECTED_MAIN" ]] || die "Remote main drift: erwartet $EXPECTED_MAIN, gefunden ${REMOTE_MAIN:-NICHT_GEFUNDEN}"
git ls-remote --exit-code "$REPO_URL" "refs/heads/$BACKUP_BRANCH" >/dev/null \
  || die "Backup-Branch $BACKUP_BRANCH fehlt."
git ls-remote --exit-code "$REPO_URL" "refs/heads/$SYNC_BRANCH" >/dev/null \
  || die "Safe-State-Branch $SYNC_BRANCH fehlt."
ok "Main unverändert; Backup- und Safe-State-Branch vorhanden."

info "2/8 Offensichtliche Secret-Dateien blockieren"
SECRET_FILES="$(find "$PROJECT" -type f \( \
  -name '.env' -o -name '.env.*' -o -name '*.pem' -o -name '*.p12' \
  -o -name '*.pfx' -o -name '*.jks' -o -name '*.keystore' \
  -o -name 'id_rsa' -o -name 'id_ed25519' \
\) -not -path '*/runtime/*' -not -path '*/__pycache__/*' -print || true)"
[[ -z "$SECRET_FILES" ]] || {
  printf '%s\n' "$SECRET_FILES" >&2
  die "Potenzielle Secret-Dateien gefunden. Nichts wurde gepusht."
}

if grep -RIlE \
  --exclude-dir=runtime --exclude-dir=__pycache__ --exclude='*.zip' --exclude='*.gz' \
  '(-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----|github_pat_[A-Za-z0-9_]{20,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16})' \
  "$PROJECT" >/tmp/provoware_secret_hits.$$ 2>/dev/null; then
  cat /tmp/provoware_secret_hits.$$ >&2
  rm -f /tmp/provoware_secret_hits.$$
  die "Potenzielle Zugangsdaten im Projekt gefunden. Nichts wurde gepusht."
fi
rm -f /tmp/provoware_secret_hits.$$ 2>/dev/null || true
ok "Kein offensichtliches Secret-Muster gefunden."

info "3/8 Temporären Git-Arbeitsraum anlegen"
TMP="$(mktemp -d -t provoware-github-sync-XXXXXX)"
cleanup(){ rm -rf "$TMP"; }
trap cleanup EXIT

git clone --quiet "$REPO_URL" "$TMP/repo"
cd "$TMP/repo"
git fetch --quiet origin "$SYNC_BRANCH" "$BACKUP_BRANCH" main
git checkout --quiet -B "$SYNC_BRANCH" "origin/$SYNC_BRANCH"
find . -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {} +

info "4/8 Projektbaum spiegeln"
rsync -a \
  --exclude='.git/' \
  --exclude='runtime/' \
  --exclude='__pycache__/' \
  --exclude='*.pyc' \
  --exclude='.pytest_cache/' \
  --exclude='.mypy_cache/' \
  --exclude='.ruff_cache/' \
  "$PROJECT/" "$TMP/repo/"

mkdir -p registry
python3 -S - "$PROJECT" > registry/GITHUB_FULL_TREE_PREPARED.json <<'PY'
from pathlib import Path
import json,sys,datetime
root=Path(sys.argv[1])
files=[]
total=0
for p in sorted(root.rglob("*")):
    if not p.is_file(): continue
    rel=p.relative_to(root)
    if "runtime" in rel.parts or "__pycache__" in rel.parts or p.suffix==".pyc":
        continue
    total+=p.stat().st_size
    files.append(rel.as_posix())
print(json.dumps({
  "format":"PROVOWARE_GITHUB_FULL_TREE_PREPARED",
  "generated_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
  "project_version":"0.12.2.3-UI-SIMPLIFICATION-INPUT-GUIDANCE",
  "repository":"provoware/naqya-memo",
  "target_branch":"sync/v0.12.2.3-safe-state-20260829",
  "main_targeted":False,
  "included_file_count":len(files),
  "included_bytes":total,
  "excluded":["runtime/","__pycache__/","*.pyc",".git/"],
  "release_status":"NO-GO",
  "release_gates":"1/7 PASS"
},indent=2,ensure_ascii=False))
PY

info "5/8 Dateihash-Manifest erzeugen und sofort verifizieren"
find . -type f ! -path './.git/*' ! -path './registry/GITHUB_FULL_TREE_FILESET_SHA256.txt' \
  -print0 | sort -z | xargs -0 sha256sum > registry/GITHUB_FULL_TREE_FILESET_SHA256.txt
sha256sum -c registry/GITHUB_FULL_TREE_FILESET_SHA256.txt >/dev/null
ok "Alle synchronisierten Dateien gegen SHA-256-Manifest geprüft."

info "6/8 Git-Diff prüfen"
git add -A
CHANGED="$(git diff --cached --name-only | wc -l)"
[[ "$CHANGED" -gt 0 ]] || die "Kein Unterschied zum Safe-State-Branch gefunden."
printf 'Geänderte/ersetzte Pfade: %s\n' "$CHANGED"
[[ "$(git branch --show-current)" == "$SYNC_BRANCH" ]] || die "Branch-Schutz verletzt."
git diff --cached --check || die "git diff --check fehlgeschlagen."

info "7/8 Commit auf Safe-State-Branch"
git -c user.name='PROVOWARE Safe Sync' \
    -c user.email='provoware.one@gmail.com' \
    commit -m "backup: mirror complete V0.12.2.3 project tree"

PRE_PUSH_SHA="$(git rev-parse HEAD)"
printf 'Lokaler Sync-Commit: %s\n' "$PRE_PUSH_SHA"

info "8/8 Push OHNE Force – ausschließlich Safe-State-Branch"
git push origin "HEAD:refs/heads/$SYNC_BRANCH"

REMOTE_SYNC="$(git ls-remote "$REPO_URL" "refs/heads/$SYNC_BRANCH" | awk '{print $1}')"
[[ "$REMOTE_SYNC" == "$PRE_PUSH_SHA" ]] || die "Remote-Commit stimmt nach Push nicht überein."
REMOTE_MAIN_AFTER="$(git ls-remote "$REPO_URL" refs/heads/main | awk '{print $1}')"
[[ "$REMOTE_MAIN_AFTER" == "$EXPECTED_MAIN" ]] || die "KRITISCH: main hat sich während des Laufs verändert."

cat <<EOF

════════════════════════════════════════════════════════════
🟢 FULL TREE SAFE SYNC ERFOLGREICH
════════════════════════════════════════════════════════════
Repository:      $REPO_SLUG
Version:         $VERSION
Safe Branch:     $SYNC_BRANCH
Remote Commit:   $REMOTE_SYNC
Alter Main:      $REMOTE_MAIN_AFTER (UNVERÄNDERT)
Backup Branch:   $BACKUP_BRANCH
Main Push:       NEIN
Force Push:      NEIN
Release:         NO-GO / 1 von 7 Gates

Nächster Schritt:
Draft-PR #54 prüfen. Erst nach Datei-/Hash-/Architekturaudit
darf über eine Main-Promotion entschieden werden.
════════════════════════════════════════════════════════════
EOF
