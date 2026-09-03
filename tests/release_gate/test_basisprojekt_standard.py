from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "manifeste" / "MANIFEST_BASISPROJEKT__STATUS-AKTIV__V1.0.json"
WORKFLOW = ROOT / ".github" / "workflows" / "quality.yml"
BUILDER = ROOT / "tools" / "build_basisprojekt.py"
VERIFIER = ROOT / "tools" / "verify_basisprojekt_artifact.py"


def git_head():
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def run(*args):
    return subprocess.run(
        [sys.executable, "-S", *map(str, args)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def test_manifest_requires_current_lineage_identity():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert data["schema_version"] == 1 and data["status"] == "AKTIV"
    assert data["artifact_policy"]["output"] == "vollstaendiges_basisprojekt"
    assert data["artifact_policy"]["include_logs"] is False
    assert data["artifact_policy"]["include_runtime_data"] is False
    assert data["artifact_policy"]["generated_manifest_name"] == "BASISPROJEKT_MANIFEST.json"
    assert data["lineage_export"]["required"] is True
    assert data["lineage_export"]["source_file"] == "registry/PRODUCT_BASELINE.json"
    assert "registry/PRODUCT_BASELINE.json" in data["include_files"]
    assert data["ci_export"]["upload_action_sha"] == "ea165f8d65b6e75b540449e92b4886f43607fa02"
    assert data["ci_export"]["source_sha_policy"] == "pull_request_head_or_push_sha"


def test_schnellstart_is_stdlib_only_and_click_start():
    for rel in ("SCHNELLSTART.sh", "requirements.txt", "tools/build_basisprojekt.py", "tools/verify_basisprojekt_artifact.py"):
        assert (ROOT / rel).is_file(), rel
    script = (ROOT / "SCHNELLSTART.sh").read_text(encoding="utf-8")
    assert "STARTEN_LINUX.sh" in script
    assert "Python 3.12.x" in script
    assert "requirements.txt" in script
    assert 'exec "$ROOT/STARTEN_LINUX.sh"' in script
    active = [
        line.strip()
        for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    assert active == []


def test_ci_publishes_only_after_current_quality_boundary():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "Build and independently verify basis project" in workflow
    assert "Publish verified basis project" in workflow
    assert "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02" in workflow
    assert "if-no-files-found: error" in workflow
    assert "SOURCE_SHA: ${{ github.event.pull_request.head.sha || github.sha }}" in workflow
    assert "ref: ${{ env.SOURCE_SHA }}" in workflow
    assert '--expected-head "$SOURCE_SHA"' in workflow
    assert "name: PROVOWARE-Naqya-Memo-Basisprojekt-${{ env.SOURCE_SHA }}" in workflow
    assert workflow.index("Evidence boundary") < workflow.index("Basisproject standard")
    assert workflow.index("Basisproject standard") < workflow.index("Build and independently verify basis project")
    assert workflow.index("Build and independently verify basis project") < workflow.index("Publish verified basis project")
    for forbidden in (
        "Error UX browser interaction boundary",
        "Visual status badge consistency",
        "Local HTTP request normalization security",
    ):
        assert forbidden not in workflow


def test_builder_contract_check_passes():
    result = run(BUILDER, "--check")
    assert result.returncode == 0, result.stderr or result.stdout
    assert "PASS basis project contract" in result.stdout


def test_builder_rejects_symlink_in_allowed_source_tree():
    resources = ROOT / "resources"
    link = resources / ".basisproject_symlink_guard_test"
    with tempfile.TemporaryDirectory(prefix="naqya-basis-symlink-target-") as tmp:
        target = Path(tmp) / "outside.txt"
        target.write_text("outside", encoding="utf-8")
        try:
            link.symlink_to(target)
            result = run(BUILDER, "--check")
            assert result.returncode != 0
            assert "Symlink" in (result.stderr + result.stdout)
        finally:
            if link.is_symlink() or link.exists():
                link.unlink()


def test_builder_refuses_output_inside_exported_root():
    forbidden = ROOT / "resources" / ".basisproject-output-must-not-exist"
    if forbidden.exists():
        shutil.rmtree(forbidden)
    result = run(BUILDER, "--output-dir", forbidden)
    assert result.returncode != 0
    assert "Ausgabeordner liegt in einem exportierten Quellordner" in (result.stderr + result.stdout)
    assert not forbidden.exists()


def build_verified_zip(outdir):
    result = run(BUILDER, "--output-dir", outdir)
    assert result.returncode == 0, result.stderr or result.stdout
    zips = sorted(Path(outdir).glob("PROVOWARE_Naqya-Memo_BASISPROJEKT_STATUS-AKTIV_*.zip"))
    assert len(zips) == 1, zips
    verify = run(VERIFIER, zips[0], "--expected-head", git_head())
    assert verify.returncode == 0, verify.stderr or verify.stdout
    assert "PASS verified basis project" in verify.stdout
    return zips[0]


def test_artifact_binds_product_acceptance_lineage_and_sha():
    with tempfile.TemporaryDirectory(prefix="naqya-basis-contract-") as tmp:
        archive = build_verified_zip(tmp)
        with zipfile.ZipFile(archive) as zf:
            manifest = json.loads(zf.read("BASISPROJEKT_MANIFEST.json").decode("utf-8"))
            baseline = json.loads(zf.read("registry/PRODUCT_BASELINE.json").decode("utf-8"))
        assert manifest["source_git_head"] == git_head()
        assert manifest["product_version"] == baseline["product_version"]
        assert manifest["product_revision"] == baseline["product_revision"]
        assert manifest["ui_contract_version"] == baseline["ui_contract_version"]
        assert manifest["acceptance"]["track"] == baseline["acceptance"]["track"]
        assert manifest["acceptance"]["revision"] == baseline["acceptance"]["revision"]
        assert manifest["required_ancestor_sha"] == baseline["lineage"]["required_ancestor_sha"]


def test_independent_verifier_rejects_unexpected_archive_member():
    with tempfile.TemporaryDirectory(prefix="naqya-basis-tamper-") as tmp:
        tmp = Path(tmp)
        archive = build_verified_zip(tmp)
        tampered = tmp / "tampered.zip"
        with zipfile.ZipFile(archive, "r") as src, zipfile.ZipFile(tampered, "w") as dst:
            for info in src.infolist():
                dst.writestr(info, src.read(info.filename))
            dst.writestr("UNEXPECTED.txt", b"must fail")
        verify = run(VERIFIER, tampered, "--expected-head", git_head())
        assert verify.returncode != 0
        assert "weicht" in (verify.stderr + verify.stdout)


def main():
    tests = sorted(
        (name, value)
        for name, value in globals().items()
        if name.startswith("test_") and callable(value)
    )
    failed = 0
    for name, test in tests:
        try:
            test()
            print(f"PASS {name}")
        except Exception as exc:
            failed += 1
            print(f"FAIL {name} {exc!r}")
    print(f"SUMMARY total={len(tests)} passed={len(tests)-failed} failed={failed}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
