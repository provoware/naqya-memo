#!/usr/bin/env python3
from __future__ import annotations
import argparse, base64, hashlib, json, os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

VERSION = "0.3.16"
CI_REL = Path("ci/pre_autosave_v0.3.16_r3")
INDEX_NAME = "KIT_INDEX.json"
RELEASE_INDEX = Path("releases/Provoware_Naqya_Memo_Tool_2026/v0.3.16/RELEASE_INDEX_FERTIG_v0.3.16.json")
LOCK_NAME = "QUELLSTAND_LOCK_FERTIG_v0.3.16.json"
KIT_FOLDER = "Provoware_Naqya_CROSS_PLATFORM_ACCEPTANCE_KIT_v0.3.16"
RUNNER_REL = Path("ENTWICKLUNG_LOKAL_NICHT_INS_REPO/werkzeuge/cross_platform_runner_FERTIG_v0.3.16.py")
HARNESS_REL = Path("ENTWICKLUNG_LOKAL_NICHT_INS_REPO/tests/firefox_acceptance_harness_FERTIG_v0.3.16.html")
WORKER_REL = Path("ENTWICKLUNG_LOKAL_NICHT_INS_REPO/tests/transaction_kill_worker_FERTIG_v0.3.16.mjs")
EVIDENCE_REL = Path("ENTWICKLUNG_LOKAL_NICHT_INS_REPO/evidence")
MANIFEST_REL = Path("ENTWICKLUNG_LOKAL_NICHT_INS_REPO/manifeste")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_index(root: Path) -> dict:
    data = json.loads((root / CI_REL / INDEX_NAME).read_text(encoding="utf-8"))
    assert data["schemaVersion"] == 1
    assert data["version"] == VERSION
    return data


def reconstruct(root: Path, out_base: Path) -> Path:
    idx = load_index(root)
    parts_dir = root / CI_REL / "kit_parts"
    expected = idx["parts"]
    actual = sorted(p.name for p in parts_dir.glob("*.b64"))
    assert actual == sorted(expected), f"Kit part inventory drift: {actual} != {sorted(expected)}"
    sizes = [len((parts_dir / n).read_text(encoding="ascii")) for n in expected]
    assert sizes == idx["partSizes"], f"Part size drift: {sizes}"
    payload = "".join((parts_dir / n).read_text(encoding="ascii") for n in expected)
    assert len(payload) == idx["base64Characters"]
    raw = base64.b64decode(payload, validate=True)
    assert len(raw) == idx["kitSize"]
    assert sha256_bytes(raw) == idx["kitSha256"]
    work = out_base / "naqya-kit-r3"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    zip_path = work / idx["kitZip"]
    zip_path.write_bytes(raw)
    assert zipfile.is_zipfile(zip_path)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(work)
    kit = work / KIT_FOLDER
    assert kit.is_dir()
    print(json.dumps({"status":"PASS","kit":str(kit),"size":len(raw),"sha256":idx["kitSha256"]}))
    return kit


def verify_source_lock(root: Path, kit: Path) -> None:
    idx = load_index(root)
    lock = json.loads((kit / LOCK_NAME).read_text(encoding="utf-8"))
    assert lock["planId"] == idx["planId"]
    assert lock["planHash"] == idx["planHash"]
    locked = {k:v for k,v in lock.items() if k not in {"planId","planHash"}}
    assert len(locked) == 5
    for rel, want in locked.items():
        assert sha256_file(kit / rel) == want, f"Source hash drift: {rel}"
    release = json.loads((root / RELEASE_INDEX).read_text(encoding="utf-8"))
    release_map = {x["path"]:x["sha256"] for x in release["basisDateien"]}
    tx_rel = "basis/skripte/transaktion_FERTIG_v0.3.16.js"
    assert release_map[tx_rel] == idx["releaseTransactionSha256"]
    assert locked["BASIS_RELEASE/basis/skripte/transaktion_FERTIG_v0.3.16.js"] == idx["releaseTransactionSha256"]
    assert release["version"] == VERSION and release["status"] == "KANDIDAT"
    print(json.dumps({"status":"PASS","lockedSources":5,"planId":idx["planId"],"planHash":idx["planHash"],"releaseTransactionSha256":idx["releaseTransactionSha256"]}))


def node_check_text(text: str, suffix: str = ".mjs") -> None:
    node = shutil.which("node") or shutil.which("node.exe")
    assert node
    fd, raw = tempfile.mkstemp(prefix="naqya_ci_syntax_", suffix=suffix)
    os.close(fd)
    p = Path(raw)
    try:
        p.write_text(text, encoding="utf-8", newline="\n")
        subprocess.run([node, "--check", str(p)], check=True)
    finally:
        p.unlink(missing_ok=True)


def syntax_preflight(kit: Path) -> None:
    subprocess.run([sys.executable, "-m", "py_compile", str(kit / RUNNER_REL)], check=True)
    node = shutil.which("node") or shutil.which("node.exe")
    assert node
    subprocess.run([node, "--check", str(kit / "BASIS_RELEASE/basis/skripte/transaktion_FERTIG_v0.3.16.js")], check=True)
    subprocess.run([node, "--check", str(kit / WORKER_REL)], check=True)
    html = (kit / HARNESS_REL).read_text(encoding="utf-8")
    start = html.index('<script type="module">') + len('<script type="module">')
    end = html.index('</script>', start)
    node_check_text(html[start:end])
    print(json.dumps({"status":"PASS","syntax":"python+node+firefox-inline-module"}))


def default_kit() -> Path:
    temp = os.environ.get("RUNNER_TEMP")
    assert temp, "RUNNER_TEMP is required when --kit is omitted"
    return Path(temp) / "naqya-kit-r3" / KIT_FOLDER


def run_runner(kit: Path, merge_only: bool = False) -> int:
    cmd = [sys.executable, str(kit / RUNNER_REL)] + (["--merge-only"] if merge_only else [])
    p = subprocess.run(cmd)
    allowed = {0} if merge_only else {0, 2}
    assert p.returncode in allowed, f"Acceptance runner returned unexpected rc={p.returncode}"
    print(json.dumps({"status":"PASS","runnerReturnCode":p.returncode,"mergeOnly":merge_only,"strictRealProcessKill":"LOCKED_IN_R3_RUNNER"}))
    return p.returncode


def latest_platform(kit: Path, os_name: str) -> tuple[Path, dict]:
    files = sorted((kit / EVIDENCE_REL).glob(f"platform_{os_name}_*_v{VERSION}.json"), key=lambda p:p.stat().st_mtime)
    assert files, f"No platform evidence for {os_name}"
    p = files[-1]
    return p, json.loads(p.read_text(encoding="utf-8"))


def validate_host(kit: Path, os_name: str) -> Path:
    p, d = latest_platform(kit, os_name)
    assert d["version"] == VERSION and d["host"]["os"] == os_name
    assert d["hostAcceptance"] == "PASS", d
    checks = {x["id"]:x for x in d["checks"]}
    assert checks["process-kill-recovery"]["status"] == "PASS"
    assert checks["stress-5000"]["status"] == "PASS"
    details = checks["process-kill-recovery"]["details"]
    assert [x["scenario"] for x in details] == ["after_journal","after_record","after_index"]
    assert all(x["realProcessKill"] and x["killPointReached"] and x["ok"] for x in details)
    assert checks["stress-5000"]["details"].get("ok") is True
    print(json.dumps({"status":"PASS","host":os_name,"evidence":str(p),"strictRealProcessKill":True}))
    return p


def validate_firefox(kit: Path) -> Path:
    candidates=[]
    for p in (kit / EVIDENCE_REL).glob(f"platform_*_v{VERSION}.json"):
        d=json.loads(p.read_text(encoding="utf-8"))
        ff=next((x for x in d.get("checks",[]) if x.get("id")=="firefox-e2e" and x.get("status")=="PASS"),None)
        if ff:
            candidates.append((p,d,ff))
    assert candidates, "No PASS Firefox evidence"
    p,d,ff=sorted(candidates,key=lambda x:x[0].stat().st_mtime)[-1]
    z=ff["details"]
    assert d["hostAcceptance"] == "PASS"
    assert z["ok"] is True and z["probe"]["firefox"] is True
    assert z["stress5000"]["ok"] is True and z["stress5000"]["count"] == 5000
    assert [x["scenario"] for x in z["killRecovery"]] == ["after_journal","after_record","after_index"]
    assert all(x["ok"] for x in z["killRecovery"])
    print(json.dumps({"status":"PASS","firefox":z.get("executable"),"evidence":str(p)}))
    return p


def export_evidence(kit: Path, kind: str, dest: Path, os_name: str | None = None) -> Path:
    if kind == "host":
        assert os_name
        src,_=latest_platform(kit,os_name)
    else:
        src=validate_firefox(kit)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src,dest)
    print(json.dumps({"status":"PASS","exported":str(dest),"source":str(src),"sha256":sha256_file(dest)}))
    return dest


def validate_merged_manifest(root: Path, kit: Path, evaluator_path: Path, out_path: Path) -> None:
    idx=load_index(root)
    manifests=sorted((kit / MANIFEST_REL).glob(f"manifest_evidence_BEWIESEN_v{VERSION}.json"))
    assert manifests, "PASS PRE-AUTOSAVE manifest missing"
    mf=manifests[-1]
    d=json.loads(mf.read_text(encoding="utf-8"))
    assert d["status"] == "PASS" and d["v0_4_0_safe_autosave_freigabe"] is True
    assert d["planId"] == idx["planId"] and d["planHash"] == idx["planHash"]
    assert all(x["status"] == "PASS" for x in d["checks"])
    closure=json.loads(evaluator_path.read_text(encoding="utf-8"))
    assert closure["release_status"] in {"GO","NO-GO"}
    implementation_allowed=closure["release_status"]=="GO" and bool(closure["v1_rc_allowed"])
    prov={"schemaVersion":3,"productTrack":"Provoware Naqya Memo Tool 2026","version":VERSION,"preAutosaveStatus":"PASS","safeAutosaveGateLocalPrerequisitePassed":True,"safeAutosaveImplementationAllowed":implementation_allowed,"repositoryReleaseStatus":closure["release_status"],"repositoryV1RcAllowed":bool(closure["v1_rc_allowed"]),"canonicalRepositoryEvaluator":"tools/release_gate/evaluate_release_gate.py","semantics":"PRE-AUTOSAVE PASS proves only the gate-local prerequisite. SAFE AUTOSAVE implementation remains blocked unless the canonical repository evaluator permits it.","planId":d["planId"],"planHash":d["planHash"],"evidenceManifestSha256":sha256_file(mf),"evaluatorClosureSha256":sha256_file(evaluator_path),"githubRepository":os.environ.get("GITHUB_REPOSITORY"),"githubCommit":os.environ.get("GITHUB_SHA"),"githubRunId":os.environ.get("GITHUB_RUN_ID"),"githubRunAttempt":os.environ.get("GITHUB_RUN_ATTEMPT")}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(prov,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(prov,ensure_ascii=False))


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("command",choices=["reconstruct","source-lock","syntax","run-host","run-merge","validate-host","validate-firefox","export-host","export-firefox","validate-merged"])
    ap.add_argument("--out-base")
    ap.add_argument("--kit")
    ap.add_argument("--os")
    ap.add_argument("--evaluator")
    ap.add_argument("--out")
    ap.add_argument("--dest")
    args=ap.parse_args()
    root=repo_root()
    if args.command=="reconstruct":
        reconstruct(root,Path(args.out_base or os.environ.get("RUNNER_TEMP") or "."))
        return 0
    kit=Path(args.kit) if args.kit else default_kit()
    if args.command=="source-lock": verify_source_lock(root,kit)
    elif args.command=="syntax": syntax_preflight(kit)
    elif args.command=="run-host": run_runner(kit,False)
    elif args.command=="run-merge": run_runner(kit,True)
    elif args.command=="validate-host": validate_host(kit,args.os)
    elif args.command=="validate-firefox": validate_firefox(kit)
    elif args.command=="export-host": export_evidence(kit,"host",Path(args.dest),args.os)
    elif args.command=="export-firefox": export_evidence(kit,"firefox",Path(args.dest))
    elif args.command=="validate-merged": validate_merged_manifest(root,kit,Path(args.evaluator),Path(args.out))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
