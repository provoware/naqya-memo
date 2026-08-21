from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {
    ".md", ".txt", ".json", ".webmanifest", ".yml", ".yaml", ".toml",
    ".js", ".html", ".css", ".sh", ".bat", ".rs"
}
SKIP_PARTS = {".git", ".sidecar-build", "dist", "target", "binaries", "node_modules"}
MERGE_MARKER = re.compile(r"^(<<<<<<<(?: .*)?|=======$|>>>>>>>(?: .*)?)$", re.MULTILINE)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise AssertionError(f"Doppelter JSON-Schlüssel: {key}")
        result[key] = value
    return result


# 1. Alle textartigen Repository-Dateien auf verbliebene Merge-Marker prüfen.
for path in ROOT.rglob("*"):
    if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
        continue
    if any(part in SKIP_PARTS for part in path.parts):
        continue
    text = path.read_text(encoding="utf-8")
    assert not MERGE_MARKER.search(text), f"Merge-Konfliktmarker in {path.relative_to(ROOT)}"

# 2. JSON muss nicht nur syntaktisch gültig, sondern auch schlüssig eindeutig sein.
for rel in [
    "VERSION.json",
    "PROJEKTSTATUS.json",
    "manifest.webmanifest",
    "src-tauri/tauri.conf.json",
    "src-tauri/sidecar/whisper-runtime.json",
]:
    json.loads(read(rel), object_pairs_hook=reject_duplicate_keys)

# 3. Zentrale Dokumente dürfen nicht durch Merge-Verklebung doppelte Hauptabschnitte enthalten.
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

readme = read("README.md")
assert readme.count("## Neu in 0.5.0") == 1
assert readme.count("## Entwickler-Einstieg") == 1
assert readme.count("## Nächster Entwicklungsblock") == 1
assert "0.5.1 – LINUX-BUNDLE-ABNAHME, RELEASE-NACHWEIS & WINDOWS-SIDECAR" in readme
assert "noch nicht als Release end-to-end abgenommen" in readme
assert "CONTRIBUTING.md" in readme
assert "docs/ENTWICKLERDOKUMENTATION.md" in readme
assert "deterministisches Desktop-Frontend-Staging" in readme

todo = read("TODO.md")
for heading in [
    "## P0 – Freigabekritisch",
    "## P1 – Hohe Priorität",
    "## P2 – Qualitätsausbau",
    "## P3 – Wartbarkeit",
    "## Entwickler-Übergabecheckliste",
    "## Erledigt",
]:
    assert todo.count(heading) == 1, f"TODO-Abschnitt fehlt oder ist doppelt: {heading}"
assert "Aktueller PR: wird" not in todo
assert "pflege/0.5.0-status-konsistenz" not in todo
assert "Vor jeder künftigen Entwicklerübergabe" in todo
assert "Deterministisches Desktop-Frontend-Staging" in todo

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
assert '"frontendDist": "../dist"' in developer
assert "tools/stage_desktop_frontend.py" in developer
assert "Produktversion ≠ Datenbankschema" in developer

version = json.loads(read("VERSION.json"), object_pairs_hook=reject_duplicate_keys)
assert version["version"] == "0.5.0"
assert version["phase"] == "TAURI-SIDECAR-INTEGRATION & REPOSITORY-KONSOLIDIERUNG"
assert version["native_stt_provider"] == "whisper.cpp-sidecar"
assert version["native_stt_fallback"] == "whisper-cli"
assert version["sidecar_bundle_configured"] is True
assert version["sidecar_linux_ci_built"] is True
assert version["sidecar_release_bundle_validated"] is False

# Eine Laufzeit-Versionsdrift darf nie unbemerkt sein: entweder synchron oder explizit als Restarbeit dokumentiert.
app = read("app.js")
app_version_match = re.search(r"const VERSION='([^']+)'", app)
assert app_version_match, "Produktversionskonstante in app.js fehlt"
app_version = app_version_match.group(1)
if app_version != version["version"]:
    assert "PWA-Produktversionskonstante mit 0.5.0 synchronisieren" in todo
    assert "app.js` verwendet intern noch die Produktversionskonstante `0.2.0`" in readme

status = json.loads(read("PROJEKTSTATUS.json"), object_pairs_hook=reject_duplicate_keys)
assert status["entwicklungsphase"] == version["phase"]
kern = status["kernfunktionen"]
assert kern["whisper_cpp_sidecar_bundle_configured"] is True
assert kern["whisper_cpp_sidecar_linux_ci_built"] is True
assert kern["whisper_cpp_sidecar_release_bundle_validated"] is False
assert "whisper_cpp_native_runtime_bundled" not in kern, "Mehrdeutiges altes Bundle-Feld darf nicht zurückkehren"

whisper_doc = read("docs/WHISPER_SIDECAR.md")
assert "bundle.externalBin" in whisper_doc
assert "Noch nicht abgeschlossen ist die vollständige Endanwender-Bundle-Abnahme" in whisper_doc
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

print("NAQYA Text-/Merge-Integrität: PASS")
