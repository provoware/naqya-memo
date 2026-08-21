from pathlib import Path
import json
import re

root = Path(__file__).resolve().parents[1]
manifest_path = root / "src-tauri/sidecar/whisper-runtime.json"
build_script = root / "tools/build_whisper_sidecar.sh"
tauri_path = root / "src-tauri/tauri.conf.json"
cargo_path = root / "src-tauri/Cargo.toml"
rust_path = root / "src-tauri/src/main.rs"

assert manifest_path.is_file(), "Whisper-Sidecar-Manifest fehlt"
assert build_script.is_file(), "Whisper-Sidecar-Buildskript fehlt"

manifest = json.loads(manifest_path.read_text())
tauri = json.loads(tauri_path.read_text())
cargo = cargo_path.read_text()
rust = rust_path.read_text()

assert manifest["schema_version"] == 1
assert manifest["provider"] == "ggml-org/whisper.cpp"
assert manifest["upstream_repository"] == "https://github.com/ggml-org/whisper.cpp"
assert manifest["upstream_tag"] == "v1.9.2"
assert manifest["upstream_commit"] == "306c88f4d1286aec1bf96e544632897886af5501"
assert re.fullmatch(r"[0-9a-f]{40}", manifest["upstream_commit"])
assert manifest["binary_basename"] == "naqya-whisper"
assert manifest["upstream_binary"] == "whisper-cli"
assert manifest["build_profile"] == "cpu-release-static"
assert "-DGGML_NATIVE=OFF" in manifest["cmake_options"]
assert "-DBUILD_SHARED_LIBS=OFF" in manifest["cmake_options"]
assert manifest["integrity_policy"]["source_commit_must_match"] is True
assert manifest["integrity_policy"]["binary_sha256_required_for_release"] is True
assert manifest["integrity_policy"]["allow_runtime_download"] is False
assert manifest["integrity_policy"]["allow_unverified_sidecar"] is False

expected_targets = {
    "x86_64-unknown-linux-gnu": "src-tauri/binaries/naqya-whisper-x86_64-unknown-linux-gnu",
    "x86_64-pc-windows-msvc": "src-tauri/binaries/naqya-whisper-x86_64-pc-windows-msvc.exe",
}
assert set(manifest["targets"]) == set(expected_targets)
for target, output in expected_targets.items():
    entry = manifest["targets"][target]
    assert entry["status"] == "build-required"
    assert entry["output"] == output

assert tauri["bundle"]["externalBin"] == ["binaries/naqya-whisper"]
assert tauri["build"]["frontendDist"] == "../dist"
assert 'tauri-plugin-shell = "2"' in cargo
for needle in [
    'tauri_plugin_shell::ShellExt',
    'sidecar("naqya-whisper")',
    'tauri_plugin_shell::init()',
    'bundled_sidecar_available',
    'whisper.cpp-sidecar',
    'whisper.cpp-fallback',
]:
    assert needle in rust, f"Tauri-Sidecar-Integration fehlt: {needle}"

script = build_script.read_text()
for needle in [
    "set -euo pipefail",
    "v1.9.2",
    "306c88f4d1286aec1bf96e544632897886af5501",
    "git clone --filter=blob:none --no-checkout",
    "checkout --detach",
    "GGML_NATIVE=OFF",
    "BUILD_SHARED_LIBS=OFF",
    "--target whisper-cli",
    "sha256sum",
    "naqya-whisper-$TARGET_TRIPLE",
]:
    assert needle in script, f"Sidecar-Buildvertrag unvollständig: {needle}"

assert "curl " not in script
assert "wget " not in script
assert "latest" not in script.lower()

print("NAQYA 0.5 Sidecar-Vertrag + Tauri-Integration: PASS")
