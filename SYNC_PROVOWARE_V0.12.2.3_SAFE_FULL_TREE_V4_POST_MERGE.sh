#!/usr/bin/env bash
set -euo pipefail

# OI - PROVOWARE - IO
# V0.12.2.3 SAFE FULL TREE SYNC · V4 POST-MERGE
#
# Situation:
# - PR #54 wurde bereits gemergt.
# - main enthält NUR Safe-State-/Backup-Metadaten, noch nicht den Full Tree.
# - historischer Main 0.5.1-E7 bleibt auf eigenem Backup-Branch erhalten.
# - aktueller Post-PR54-main wird zusätzlich auf einem zweiten Backup-Branch eingefroren.
# - der vollständige V0.12.2.3-Baum geht ausschließlich auf einen NEUEN Sync-Branch.
#
# Sicherheitsregeln:
# - KEIN Push auf main.
# - KEIN --force.
# - beide Backup-Branches müssen exakt auf den erwarteten Commits stehen.
# - GitHub-Schreibauthentifizierung wird VOR Clone/Mirror/Commit geprüft.
# - Secrets und Merge-Konfliktmarker blockieren.
# - vorhandene Markdown-/Whitespace-Formatierung bleibt bytegetreu erhalten.
# - runtime/, Python-Caches und lokale Testcaches werden nicht synchronisiert.
# - nach Push wird main erneut geprüft.
# - erst danach wird ein NEUER Draft-PR erstellt; niemals automatisch gemergt.

REPO_SLUG="provoware/naqya-memo"
REPO_HTTPS="https://github.com/provoware/naqya-memo.git"
REPO_SSH="git@github.com:provoware/naqya-memo.git"

HISTORIC_MAIN="334dd2923fc01a633946137d71fdbebae34364da"
CURRENT_MAIN="a2e4767ea0017f5df38eeb72142005441b02ecb2"

HISTORIC_BACKUP="backup/pre-v0.12.2.3-20260829"
POST_MERGE_BACKUP="backup/pre-full-tree-v0.12.2.3-20260829"
SYNC_BRANCH="sync/v0.12.2.3-full-tree-20260829"

VERSION="0.12.2.3-UI-SIMPLIFICATION-INPUT-GUIDANCE"

die(){ printf '\n🔴 FEHLER: %s\n' "$*" >&2; exit 1; }
info(){ printf '\n🔵 %s\n' "$*"; }
ok(){ printf '🟢 %s\n' "$*"; }

ref_sha(){
  git ls-remote "$REPO_URL" "refs/heads/$1" | awk '{print $1}'
}

auth_preflight(){
  info "0/9 GitHub-Schreibzugang prüfen"

  command -v gh >/dev/null 2>&1 || {
    cat >&2 <<'EOF'
GitHub CLI `gh` fehlt.

Ubuntu/Kubuntu:
  sudo apt update
  sudo apt install gh
  gh auth login --hostname github.com
EOF
    exit 20
  }

  gh auth status --hostname github.com >/dev/null 2>&1 \
    || die "GitHub CLI ist nicht angemeldet. Bitte zuerst: gh auth login --hostname github.com"

  PUSH_ALLOWED="$(gh api "repos/$REPO_SLUG" --jq '.permissions.push // false' 2>/dev/null || echo false)"
  [[ "$PUSH_ALLOWED" == "true" ]] || die "Das angemeldete GitHub-Konto besitzt keinen Push-Zugriff auf $REPO_SLUG."

  PROTOCOL="$(gh config get git_protocol --host github.com 2>/dev/null || echo https)"
  if [[ "$PROTOCOL" == "ssh" ]]; then
    REPO_URL="$REPO_SSH"
    export REPO_URL
    GIT_SSH_COMMAND='ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new' \
      git ls-remote "$REPO_URL" HEAD >/dev/null 2>&1 \
      || die "GitHub ist auf SSH gestellt, aber der SSH-Git-Zugriff funktioniert noch nicht."
    ok "GitHub CLI authentifiziert; SSH-Schreibweg und Push-Berechtigung bestätigt."
  else
    REPO_URL="$REPO_HTTPS"
    export REPO_URL
    gh auth setup-git >/dev/null 2>&1 || die "gh auth setup-git fehlgeschlagen."
    git ls-remote "$REPO_URL" HEAD >/dev/null 2>&1 \
      || die "Authentifizierter HTTPS-Git-Zugriff funktioniert nicht."
    ok "GitHub CLI authentifiziert; HTTPS-Schreibweg und Push-Berechtigung bestätigt."
  fi
}

# Komfort: ohne Argument wird der aktuelle Ordner benutzt.
if [[ $# -eq 0 ]]; then
  PROJECT="$PWD"
elif [[ $# -eq 1 ]]; then
  PROJECT="$(cd "$1" && pwd)"
else
  die "Benutzung: $0 [Projektordner]"
fi

[[ -f "$PROJECT/registry/VERSION.json" ]] || die "registry/VERSION.json fehlt in $PROJECT."

auth_preflight

ACTUAL_VERSION="$(python3 -S - "$PROJECT/registry/VERSION.json" <<'PY'
import json,sys
print(json.load(open(sys.argv[1],encoding="utf-8"))["version"])
PY
)"
[[ "$ACTUAL_VERSION" == "$VERSION" ]] || die "Falsche Projektversion: $ACTUAL_VERSION"

info "1/9 Remote-Sicherheitsgrenzen prüfen"
REMOTE_MAIN="$(ref_sha main)"
[[ "$REMOTE_MAIN" == "$CURRENT_MAIN" ]] \
  || die "Remote main drift: erwartet $CURRENT_MAIN, gefunden ${REMOTE_MAIN:-NICHT_GEFUNDEN}"

HIST_SHA="$(ref_sha "$HISTORIC_BACKUP")"
[[ "$HIST_SHA" == "$HISTORIC_MAIN" ]] \
  || die "Historischer Backup-Branch stimmt nicht: $HIST_SHA"

POST_SHA="$(ref_sha "$POST_MERGE_BACKUP")"
[[ "$POST_SHA" == "$CURRENT_MAIN" ]] \
  || die "Post-Merge-Backup stimmt nicht: erwartet $CURRENT_MAIN, gefunden ${POST_SHA:-NICHT_GEFUNDEN}"

SYNC_SHA="$(ref_sha "$SYNC_BRANCH")"
[[ "$SYNC_SHA" == "$CURRENT_MAIN" ]] \
  || die "Full-Tree-Sync-Branch ist nicht mehr jungfräulich: erwartet Basis $CURRENT_MAIN, gefunden ${SYNC_SHA:-NICHT_GEFUNDEN}"

ok "Main und beide Backup-Ebenen stimmen exakt; neuer Full-Tree-Branch ist unverändert."

info "2/9 Offensichtliche Secret-Dateien und Tokens blockieren"
SECRET_FILES="$(find "$PROJECT" -type f \( \
  -name '.env' -o -name '.env.*' -o -name '*.pem' -o -name '*.p12' \
  -o -name '*.pfx' -o -name '*.jks' -o -name '*.keystore' \
  -o -name 'id_rsa' -o -name 'id_ed25519' \
\) -not -path '*/runtime/*' -not -path '*/__pycache__/*' -print || true)"
[[ -z "$SECRET_FILES" ]] || {
  printf '%s\n' "$SECRET_FILES" >&2
  die "Potenzielle Secret-Dateien gefunden. Nichts wurde gepusht."
}

SECRET_HITS="$(mktemp -t provoware-secret-hits-XXXXXX)"
if grep -RIlE \
  --exclude-dir=runtime --exclude-dir=__pycache__ --exclude-dir=.git \
  --exclude='*.zip' --exclude='*.gz' --exclude='*.tar' \
  '(-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----|github_pat_[A-Za-z0-9_]{20,}|ghp_[A-Za-z0-9]{20,}|gho_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16})' \
  "$PROJECT" >"$SECRET_HITS" 2>/dev/null; then
  cat "$SECRET_HITS" >&2
  rm -f "$SECRET_HITS"
  die "Potenzielle Zugangsdaten im Projekt gefunden. Nichts wurde gepusht."
fi
rm -f "$SECRET_HITS"
ok "Kein offensichtliches Secret-/Token-Muster gefunden."

info "3/9 Temporären Git-Arbeitsraum anlegen"
TMP="$(mktemp -d -t provoware-full-tree-v4-XXXXXX)"
cleanup(){ rm -rf "$TMP"; }
trap cleanup EXIT

git clone --quiet "$REPO_URL" "$TMP/repo"
cd "$TMP/repo"
git fetch --quiet origin main "$HISTORIC_BACKUP" "$POST_MERGE_BACKUP" "$SYNC_BRANCH"
git checkout --quiet -B "$SYNC_BRANCH" "origin/$SYNC_BRANCH"

[[ "$(git rev-parse HEAD)" == "$CURRENT_MAIN" ]] \
  || die "Lokale Branch-Basis driftete nach Clone."

find . -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {} +

info "4/9 Vollständigen V0.12.2.3-Projektbaum spiegeln"
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

# GitHub-Backupstatus auf den neuen echten Full-Tree-Safe-State korrigieren.
python3 -S - "$TMP/repo" <<'PY'
from pathlib import Path
import json,datetime,re,sys
root=Path(sys.argv[1])
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()

status={
  "format":"PROVOWARE_GITHUB_BACKUP_STATUS",
  "version":2,
  "generated_at_utc":stamp,
  "repository":"provoware/naqya-memo",
  "project_version":"0.12.2.3-UI-SIMPLIFICATION-INPUT-GUIDANCE",
  "historic_backup_branch":"backup/pre-v0.12.2.3-20260829",
  "historic_main_commit":"334dd2923fc01a633946137d71fdbebae34364da",
  "post_pr54_backup_branch":"backup/pre-full-tree-v0.12.2.3-20260829",
  "post_pr54_main_commit":"a2e4767ea0017f5df38eeb72142005441b02ecb2",
  "full_tree_branch":"sync/v0.12.2.3-full-tree-20260829",
  "main_targeted":False,
  "force_push":False,
  "full_source_tree_in_this_commit":True,
  "release_status":"NO-GO",
  "passed_real_release_gates":1,
  "required_real_release_gates":7,
  "main_promotion_allowed":False
}
(root/"registry/GITHUB_BACKUP_STATUS.json").write_text(
    json.dumps(status,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

readme=root/"README.md"
text=readme.read_text(encoding="utf-8")
block=f"""# 🧷 GITHUB FULL-TREE BACKUP-ZUSTAND

> **Repository:** `provoware/naqya-memo`  
> **Projektstand:** `0.12.2.3-UI-SIMPLIFICATION-INPUT-GUIDANCE`  
> **Historischer 0.5.1-E7-Stand:** `backup/pre-v0.12.2.3-20260829` → `334dd292…`  
> **Stand direkt nach PR #54:** `backup/pre-full-tree-v0.12.2.3-20260829` → `a2e4767…`  
> **Vollständiger Projektbaum:** `sync/v0.12.2.3-full-tree-20260829`  
> **Main-Push:** **NEIN**  
> **Force-Push:** **NEIN**  
> **Release:** 🔴 `NO-GO` · **1/7 reale Gates**

Dieser Branch ist der vollständige, isolierte GitHub-Backup-/Reviewstand von V0.12.2.3. `main` wird erst nach Hash-, Datei- und Architekturaudit weiter verändert.

---

"""
if text.startswith("# 🧷 GITHUB-BACKUP-ZUSTAND") or text.startswith("# 🧷 GITHUB FULL-TREE BACKUP-ZUSTAND"):
    pos=text.find("\n---\n")
    if pos!=-1:
        text=block+text[pos+5:]
    else:
        text=block+text
else:
    text=block+text
readme.write_text(text,encoding="utf-8")
PY

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
  "base_main":"a2e4767ea0017f5df38eeb72142005441b02ecb2",
  "target_branch":"sync/v0.12.2.3-full-tree-20260829",
  "main_targeted":False,
  "included_source_file_count":len(files),
  "included_source_bytes":total,
  "excluded":["runtime/","__pycache__/","*.pyc",".git/"],
  "release_status":"NO-GO",
  "release_gates":"1/7 PASS"
},indent=2,ensure_ascii=False))
PY

info "5/9 Hashmanifest erzeugen und sofort verifizieren"
find . -type f ! -path './.git/*' ! -path './registry/GITHUB_FULL_TREE_FILESET_SHA256.txt' \
  -print0 | sort -z | xargs -0 sha256sum > registry/GITHUB_FULL_TREE_FILESET_SHA256.txt
sha256sum -c registry/GITHUB_FULL_TREE_FILESET_SHA256.txt >/dev/null
ok "Alle synchronisierten Dateien gegen SHA-256-Manifest geprüft."

info "6/9 Diff, Konfliktmarker und Branchschutz prüfen"
git add -A
CHANGED="$(git diff --cached --name-only | wc -l)"
[[ "$CHANGED" -gt 0 ]] || die "Kein Full-Tree-Unterschied gefunden."
printf 'Geänderte/ersetzte Pfade: %s\n' "$CHANGED"

[[ "$(git branch --show-current)" == "$SYNC_BRANCH" ]] || die "Branch-Schutz verletzt."

CONFLICT_HITS="$TMP/conflict-markers.txt"
: > "$CONFLICT_HITS"
while IFS= read -r -d '' file; do
  case "$file" in
    *.zip|*.gz|*.tar|*.png|*.jpg|*.jpeg|*.webp|*.pdf|*.pyc) continue ;;
  esac
  grep -nHE '^(<<<<<<< |=======|>>>>>>> )' "$file" >> "$CONFLICT_HITS" 2>/dev/null || true
done < <(find . -type f ! -path './.git/*' -print0)

if [[ -s "$CONFLICT_HITS" ]]; then
  cat "$CONFLICT_HITS" >&2
  die "Merge-Konfliktmarker gefunden. Nichts wurde gepusht."
fi

WHITESPACE_REPORT="$TMP/whitespace-report.txt"
git diff --cached --check > "$WHITESPACE_REPORT" 2>&1 || true
if [[ -s "$WHITESPACE_REPORT" ]]; then
  COUNT="$(grep -Ec 'trailing whitespace|new blank line at EOF|space before tab' "$WHITESPACE_REPORT" || true)"
  echo "ℹ️  Format-Hinweise: ${COUNT:-0}; für Backup-Snapshot bewusst nicht automatisch verändert."
fi
ok "Keine Merge-Konfliktmarker; Branchschutz aktiv."

info "7/9 Commit auf NEUEM Full-Tree-Safe-Branch"
git -c user.name='PROVOWARE Safe Sync' \
    -c user.email='provoware.one@gmail.com' \
    commit -m "backup: mirror complete V0.12.2.3 project tree after PR54"

LOCAL_SHA="$(git rev-parse HEAD)"
printf 'Lokaler Full-Tree-Commit: %s\n' "$LOCAL_SHA"

info "8/9 Push ausschließlich auf Full-Tree-Safe-Branch"
git push origin "HEAD:refs/heads/$SYNC_BRANCH"

REMOTE_SYNC="$(ref_sha "$SYNC_BRANCH")"
[[ "$REMOTE_SYNC" == "$LOCAL_SHA" ]] || die "Remote-Sync-SHA stimmt nach Push nicht."

REMOTE_MAIN_AFTER="$(ref_sha main)"
[[ "$REMOTE_MAIN_AFTER" == "$CURRENT_MAIN" ]] \
  || die "KRITISCH: main wurde während des Full-Tree-Laufs verändert."

[[ "$(ref_sha "$HISTORIC_BACKUP")" == "$HISTORIC_MAIN" ]] \
  || die "KRITISCH: historischer Backup-Branch driftete."
[[ "$(ref_sha "$POST_MERGE_BACKUP")" == "$CURRENT_MAIN" ]] \
  || die "KRITISCH: Post-Merge-Backup driftete."

ok "Remote Full-Tree-Commit bestätigt; main und beide Backups unverändert."

info "9/9 Neuen Draft-PR als Review-Gate anlegen"
EXISTING_PR="$(gh pr list --repo "$REPO_SLUG" --head "$SYNC_BRANCH" --state open --json number --jq '.[0].number // empty')"
if [[ -n "$EXISTING_PR" ]]; then
  PR_NUMBER="$EXISTING_PR"
  echo "ℹ️  Draft-/Review-PR existiert bereits: #$PR_NUMBER"
else
  PR_URL="$(gh pr create \
    --repo "$REPO_SLUG" \
    --base main \
    --head "$SYNC_BRANCH" \
    --draft \
    --title "V0.12.2.3 Full-Tree Safe-State – Review vor Main" \
    --body "## Full-Tree-Safe-State

Dieser PR enthält den vollständigen V0.12.2.3-Projektbaum auf einem isolierten Branch.

### Sicherungen
- historischer Stand: \`$HISTORIC_BACKUP\` → \`$HISTORIC_MAIN\`
- Main direkt nach PR #54: \`$POST_MERGE_BACKUP\` → \`$CURRENT_MAIN\`
- Full Tree: \`$SYNC_BRANCH\` → \`$REMOTE_SYNC\`

### Vertrag
- kein Force-Push
- kein automatischer Main-Push
- SHA-256-Dateimanifest im Branch erfolgreich lokal validiert
- Release bleibt NO-GO / 1 von 7 Gates

**Nicht mergen, bevor Remote-Dateibaum, Hashmanifest und Architektur-Diff auditiert wurden.**")"
  PR_NUMBER="${PR_URL##*/}"
fi

cat <<EOF

════════════════════════════════════════════════════════════
🟢 V0.12.2.3 FULL TREE SAFE SYNC ERFOLGREICH
════════════════════════════════════════════════════════════
Repository:             $REPO_SLUG
Version:                $VERSION

Historisches Backup:    $HISTORIC_BACKUP
                         $HISTORIC_MAIN

Post-PR54-Backup:       $POST_MERGE_BACKUP
                         $CURRENT_MAIN

Full-Tree-Branch:       $SYNC_BRANCH
Full-Tree-Commit:       $REMOTE_SYNC

Main:                   $REMOTE_MAIN_AFTER (UNVERÄNDERT)
Main Push:              NEIN
Force Push:             NEIN
Draft-PR:               #$PR_NUMBER

Release:                NO-GO / 1 von 7 Gates

Nächster Schritt:
Remote-Dateibaum + SHA-Manifest + Architektur-Diff auditieren.
Erst danach über Main entscheiden.
════════════════════════════════════════════════════════════
EOF
