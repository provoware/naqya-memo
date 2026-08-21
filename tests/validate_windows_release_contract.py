from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_SHA = "fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425"
WHISPER_COMMIT = "306c88f4d1286aec1bf96e544632897886af5501"

required = [
    ".gitattributes",
    "tools/build_whisper_sidecar_windows.ps1",
    "tools/generate_release_evidence.py",
    "tests/validate_platform_diagnostics.py",
    "tests/validate_release_evidence.py",
    "tests/compare_release_evidence.py",
    "release/RELEASE_EVIDENCE.schema.json",
    ".github/workflows/bundle-linux.yml",
    ".github/workflows/bundle-windows.yml",
    ".github/workflows/bundle-platforms.yml",
]
missing = [path for path in required if not (ROOT / path).is_file()]
assert not missing, f"0.5.1-D-Vertragsdateien fehlen: {missing}"

attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8")
assert "diagnostics/DIAGNOSTICS_CONTRACT.json text eol=lf" in attributes, (
    "Diagnosevertrag muss auch bei Windows-Checkout bytegenau mit LF materialisiert werden"
)

schema = json.loads((ROOT / "release/RELEASE_EVIDENCE.schema.json").read_text(encoding="utf-8"))
target = schema["properties"]["target"]
assert target["properties"]["os"]["enum"] == ["linux", "windows"]
assert target["properties"]["architecture"]["const"] == "x86_64"
assert set(target["properties"]["rust_target"]["enum"]) == {
    "x86_64-unknown-linux-gnu",
    "x86_64-pc-windows-msvc",
}
assert schema["properties"]["diagnostics_contract"]["properties"]["sha256"]["const"] == CONTRACT_SHA

platform_test = (ROOT / "tests/validate_platform_diagnostics.py").read_text(encoding="utf-8")
for marker in [CONTRACT_SHA, "NAQYA-STT-4002", "release_nachweis", "diagnostics_contract"]:
    assert marker in platform_test, f"Plattform-Diagnosevertrag unvollständig: {marker}"

generator = (ROOT / "tools/generate_release_evidence.py").read_text(encoding="utf-8")
for marker in [
    '"linux"', '"windows"', "x86_64-unknown-linux-gnu", "x86_64-pc-windows-msvc",
    "dpkg-deb-normalized-v1", "tauri-nsis-pinned-v1", CONTRACT_SHA,
    "package_reproducibility_verified", "source_sidecar_sha_matches_packaged",
]:
    assert marker in generator, f"Evidence-Generator nicht plattformneutral: {marker}"

validator = (ROOT / "tests/validate_release_evidence.py").read_text(encoding="utf-8")
for marker in [
    "TARGETS", "x86_64-pc-windows-msvc", "tauri-nsis-pinned-v1", CONTRACT_SHA,
    "package_reproducibility_verified", "package_repack_deterministic",
]:
    assert marker in validator, f"Evidence-Validator unvollständig: {marker}"

windows_script = (ROOT / "tools/build_whisper_sidecar_windows.ps1").read_text(encoding="utf-8")
for marker in [
    '$ErrorActionPreference = "Stop"', '$UpstreamTag = "v1.9.2"', WHISPER_COMMIT,
    '$TargetTriple = "x86_64-pc-windows-msvc"', 'refs/tags/${UpstreamTag}:refs/tags/${UpstreamTag}',
    "-DGGML_NATIVE=OFF", "-DBUILD_SHARED_LIBS=OFF",
    "Get-FileHash -Algorithm SHA256", "--target whisper-cli", "--help",
]:
    assert marker in windows_script, f"Windows-Sidecar-Vertrag unvollständig: {marker}"
for forbidden in ("Invoke-WebRequest", "curl ", "wget ", "latest"):
    assert forbidden.lower() not in windows_script.lower(), f"Nicht reproduzierbarer Windows-Buildmarker: {forbidden}"

linux_workflow = (ROOT / ".github/workflows/bundle-linux.yml").read_text(encoding="utf-8")
for marker in [
    "workflow_call:", "validate_platform_diagnostics.py", "--target-os linux",
    "dpkg-deb-normalized-v1", "--package-reproducibility-verified",
]:
    assert marker in linux_workflow, f"Linux-Referenzgate geschwächt: {marker}"

windows_workflow = (ROOT / ".github/workflows/bundle-windows.yml").read_text(encoding="utf-8")
for marker in [
    "workflow_call:", "windows-latest", "validate_platform_diagnostics.py",
    "build_whisper_sidecar_windows.ps1", "cargo tauri build --bundles nsis", "7z x",
    "naqya-whisper-packaged.exe", "Get-FileHash -Algorithm SHA256",
    "RELEASE_EVIDENCE.windows.json", "--target-os windows", "tauri-nsis-pinned-v1",
]:
    assert marker in windows_workflow, f"Windows-Bundle-Gate unvollständig: {marker}"

pair_workflow = (ROOT / ".github/workflows/bundle-platforms.yml").read_text(encoding="utf-8")
for marker in [
    "uses: ./.github/workflows/bundle-linux.yml", "uses: ./.github/workflows/bundle-windows.yml",
    "needs: [linux, windows]", "actions/download-artifact@v4", "compare_release_evidence.py",
]:
    assert marker in pair_workflow, f"Plattform-Evidence-Orchestrator unvollständig: {marker}"

pair_test = (ROOT / "tests/compare_release_evidence.py").read_text(encoding="utf-8")
for marker in [CONTRACT_SHA, WHISPER_COMMIT, "diagnostics_contract", "source", "whisper", "linux", "windows"]:
    assert marker in pair_test, f"Evidence-Paarvergleich unvollständig: {marker}"

status = json.loads((ROOT / "PROJEKTSTATUS.json").read_text(encoding="utf-8"))
progress = status["fortschritt"]
assert (progress["prozent"], progress["erledigt"], progress["gesamt"]) == (78, 7, 9), (
    "0.5.1-D darf vor real grünem Windows-/Paar-Gate nicht vorzeitig als erledigt markiert werden"
)

print("NAQYA 0.5.1-D Windows-/Plattform-Evidence-Vertrag: PASS")
