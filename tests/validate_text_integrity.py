from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {
    ".md", ".txt", ".json", ".webmanifest", ".yml", ".yaml", ".toml",
    ".js", ".html", ".css", ".sh", ".bat", ".rs"
}
SKIP_PARTS = {".git", ".sidecar-build", "target", "binaries", "node_modules", "dist", ".bundle-extract"}
MERGE_MARKER = re.compile(r"^(<<<<<<<(?: .*)?|=======$|>>>>>>>(?: .*)?)$", re.MULTILINE)
EXPECTED_DIAGNOSTICS_SHA256 = "fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise AssertionError(f"Doppelter JSON-Schlüssel: {key}")
        result[key] = value
    return result


for path in ROOT.rglob("*"):
    if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
        continue
    if any(part in SKIP_PARTS for part in path.parts):
        continue
    text = path.read_text(encoding="utf-8")
    assert not MERGE_MARKER.search(text), f"Merge-Konfliktmarker in {path.relative_to(ROOT)}"

for rel in [
    "VERSION.json",
    "PROJEKTSTATUS.json",
    "manifest.webmanifest",
    "src-tauri/tauri.conf.json",
    "src-tauri/sidecar/whisper-runtime.json",
    "diagnostics/DIAGNOSTICS_CONTRACT.json",
    "release/RELEASE_EVIDENCE.schema.json",
]:
    json.loads(read(rel), object_pairs_hook=reject_duplicate_keys)

for rel in [
    "README.md",
    "CONTRIBUTING.md",
    "TODO.md",
    "AGENTS.md",
    "docs/ARCHITEKTUR.md",
    "docs/ENTWICKLERDOKUMENTATION.md",
    "docs/WHISPER_SIDECAR.md",
]:
    headings = re.findall(r"^## .+$", read(rel), flags=re.MULTILINE)
    duplicates = sorted({heading for heading in headings if headings.count(heading) > 1})
    assert not duplicates, f"Doppelte H2-Abschnitte in {rel}: {duplicates}"

version = json.loads(read("VERSION.json"), object_pairs_hook=reject_duplicate_keys)
status = json.loads(read("PROJEKTSTATUS.json"), object_pairs_hook=reject_duplicate_keys)
readme = read("README.md")
todo = read("TODO.md")

assert version["version"] == "0.5.0"
assert version["phase"] == "TAURI-SIDECAR-INTEGRATION & REPOSITORY-KONSOLIDIERUNG"
assert version["native_stt_provider"] == "whisper.cpp-sidecar"
assert version["native_stt_fallback"] == "whisper-cli"
assert version["sidecar_bundle_configured"] is True
assert version["sidecar_linux_ci_built"] is True
assert version["sidecar_release_bundle_validated"] is True
assert version["desktop_frontend_dist_deterministic"] is True
assert version["release_evidence_schema"] == 1
assert version["release_evidence_linux_ci_generated"] is True

progress = status["fortschritt"]
assert progress["prozent"] == 78
assert progress["erledigt"] == 7
assert progress["gesamt"] == 9
assert "**Fortschritt 0.5.1:** **78 %** – **7 von 9 Hauptpunkten erledigt**" in readme
assert "### Erledigt – 7 von 9" in readme
assert "### Offen – 2 von 9" in readme
assert "0.5.1-D – WINDOWS-BUNDLE MIT IDENTISCHEM DIAGNOSEVERTRAG" in readme
assert status["naechster_meilenstein"] == "0.5.1-D – WINDOWS-BUNDLE MIT IDENTISCHEM DIAGNOSEVERTRAG"

release = status["release_nachweis"]
assert release["workflow_run_id"] == 32482553418
assert release["workflow_run_number"] == 14
assert release["qualitaetspruefung_run_id"] == 32482553363
assert release["qualitaetspruefung_run_number"] == 268
assert release["source_commit"] == "0388cda77c6696017c5b00cb795f5758af2d5e22"
assert release["diagnostics_contract_sha256"] == EXPECTED_DIAGNOSTICS_SHA256
assert release["diagnostics_schema_version"] == 1
assert release["diagnostics_event_schema_version"] == 1

assert "noch keine reale Endgeräte-/Mikrofon-/Langzeitabnahme" in readme
assert EXPECTED_DIAGNOSTICS_SHA256 in readme
assert "NAQYA-STT-4002" in readme

for heading in [
    "## P0 – Freigabekritisch",
    "## P1 – Hohe Priorität",
    "## P2 – Qualitätsausbau",
    "## P3 – Wartbarkeit",
    "## Entwickler-Übergabecheckliste",
    "## Erledigt",
]:
    assert todo.count(heading) == 1, f"TODO-Abschnitt fehlt oder ist doppelt: {heading}"
assert "Vor jeder künftigen Entwicklerübergabe" in todo
assert "0.5.1-C – Professionelles Diagnose-/Debugging-/Logging-Modul integrieren" in todo
assert "0.5.1-C – Diagnose-/Release-Evidence-Vertrag verbinden" in todo
assert "Windows-x86_64-Sidecar reproduzierbar bauen und bundeln" in todo
assert EXPECTED_DIAGNOSTICS_SHA256 in todo

contributing = read("CONTRIBUTING.md")
assert "docs/ENTWICKLERDOKUMENTATION.md" in contributing
assert "AGENTS.md" in contributing
assert "TODO.md" in contributing

developer = read("docs/ENTWICKLERDOKUMENTATION.md")
for marker in [
    "## Schnellübernahme",
    "## Repository-Landkarte",
    "## Kritische Invarianten",
    "## Code-Kommentare",
    "## Lokale Qualitätsprüfung",
    "## Nächster Arbeitsblock 0.5.1",
    "## Definition of Done",
]:
    assert developer.count(marker) == 1, f"Entwicklerdokumentation unvollständig: {marker}"
assert "frontendDist" in developer
assert "Produktversion ≠ Datenbankschema" in developer

app = read("app.js")
app_version_match = re.search(r"const VERSION='([^']+)'", app)
assert app_version_match, "Produktversionskonstante in app.js fehlt"
assert app_version_match.group(1) == version["version"]
assert "const DB_VERSION=2;" in app
assert "format:'NAQYA-OFFLINE-BACKUP'" in app
assert "version:VERSION" in app

release_04 = read("services/release-04.js")
assert "window.NAQYA.release={version:VERSION" in release_04
assert "version:'0.4.0'" not in release_04
assert "Memo Tool 2026 0.4.0" not in release_04
assert "ENTWICKLERHINWEIS" in release_04

assert status["entwicklungsphase"] == version["phase"]
kern = status["kernfunktionen"]
for key in [
    "whisper_cpp_sidecar_bundle_configured",
    "whisper_cpp_sidecar_linux_ci_built",
    "whisper_cpp_sidecar_release_bundle_validated",
    "desktop_frontend_dist_deterministic",
    "release_evidence_linux_ci_generated",
    "diagnostics_contract_versioned",
    "diagnostics_contract_release_bound",
    "diagnostics_runtime_fail_safe",
    "diagnostics_privacy_redaction",
]:
    assert kern[key] is True, f"Kernfunktion fehlt: {key}"
assert "whisper_cpp_native_runtime_bundled" not in kern

whisper_doc = read("docs/WHISPER_SIDECAR.md")
assert "bundle.externalBin" in whisper_doc
assert "Diese Stufe bündelt noch keine Binärdateien" not in whisper_doc

laien = read("LAIENANLEITUNG.md")
assert "Der externe `whisper-cli` ist nur ein Fallback" in laien
assert "vollständiges Endanwender-Desktop-Paket" in laien

for historical in [
    "docs/AUDIO_OFFLINE_STT.md",
    "docs/AUDIO_NORMALISIERUNG_LIVE_STT.md",
    "docs/NATIVE_WHISPER_DESKTOP.md",
]:
    assert "Dokumentenstatus" in read(historical), f"Historischer Status fehlt in {historical}"

print("NAQYA 0.5.1-C Text-/Merge-/Statusintegrität: PASS")
