from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {'.md','.txt','.json','.webmanifest','.yml','.yaml','.toml','.js','.html','.css','.sh','.bat','.rs'}
SKIP_PARTS = {'.git','.sidecar-build','target','binaries','node_modules','dist','.bundle-extract'}
MERGE_MARKER = re.compile(r'^(<<<<<<<(?: .*)?|=======$|>>>>>>>(?: .*)?)$', re.MULTILINE)
CONTRACT_SHA = 'fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425'


def read(path):
    return (ROOT / path).read_text(encoding='utf-8')


def reject_duplicate_keys(pairs):
    out = {}
    for key, value in pairs:
        assert key not in out, f'Doppelter JSON-Schlüssel: {key}'
        out[key] = value
    return out


for path in ROOT.rglob('*'):
    if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
        continue
    if any(part in SKIP_PARTS for part in path.parts):
        continue
    assert not MERGE_MARKER.search(path.read_text(encoding='utf-8')), f'Merge-Konfliktmarker in {path.relative_to(ROOT)}'

for rel in ['VERSION.json','PROJEKTSTATUS.json','manifest.webmanifest','src-tauri/tauri.conf.json','src-tauri/sidecar/whisper-runtime.json','diagnostics/DIAGNOSTICS_CONTRACT.json','release/RELEASE_EVIDENCE.schema.json']:
    json.loads(read(rel), object_pairs_hook=reject_duplicate_keys)

for rel in ['README.md','CONTRIBUTING.md','TODO.md','AGENTS.md','docs/ARCHITEKTUR.md','docs/ENTWICKLERDOKUMENTATION.md','docs/WHISPER_SIDECAR.md','docs/DIAGNOSE_LOGGING.md']:
    headings = re.findall(r'^## .+$', read(rel), flags=re.MULTILINE)
    duplicates = sorted({h for h in headings if headings.count(h) > 1})
    assert not duplicates, f'Doppelte H2-Abschnitte in {rel}: {duplicates}'

version = json.loads(read('VERSION.json'), object_pairs_hook=reject_duplicate_keys)
status = json.loads(read('PROJEKTSTATUS.json'), object_pairs_hook=reject_duplicate_keys)
contract = json.loads(read('diagnostics/DIAGNOSTICS_CONTRACT.json'), object_pairs_hook=reject_duplicate_keys)
readme = read('README.md')
todo = read('TODO.md')
agents = read('AGENTS.md')

assert version['version'] == status['version'] == '0.5.0'
assert version['phase'] == status['entwicklungsphase'] == 'TAURI-SIDECAR-INTEGRATION & REPOSITORY-KONSOLIDIERUNG'
assert version['native_stt_provider'] == 'whisper.cpp-sidecar'
assert version['sidecar_release_bundle_validated'] is True

progress = status['fortschritt']
assert (progress['prozent'], progress['erledigt'], progress['gesamt']) == (78, 7, 9)
assert len(progress['erledigte_punkte']) == 7 and len(progress['offene_punkte']) == 2
assert '**Fortschritt 0.5.1:** **78 %** – **7 von 9 Hauptpunkten erledigt**' in readme
assert '### Erledigt – 7 von 9' in readme
assert '### Offen – 2 von 9' in readme
assert '0.5.1-D – WINDOWS-X86_64-BUNDLE & PLATTFORMÜBERGREIFENDER EVIDENCE-NACHWEIS' in readme
assert status['naechster_meilenstein'] == '0.5.1-D – WINDOWS-X86_64-BUNDLE & PLATTFORMÜBERGREIFENDER EVIDENCE-NACHWEIS'

release = status['release_nachweis']
assert release['linux_bundle_validiert'] is True
assert release['diagnostics_evidence_validiert'] is True
assert release['workflow_run_id'] == 32482553418
assert release['qualitaetspruefung_run_id'] == 32482553363
assert release['source_commit'] == '0388cda77c6696017c5b00cb795f5758af2d5e22'
assert release['artifact_id'] == 9446843382
assert release['artifact_sha256'] == '8e2efd73b581bd420f348b129e554363aaf4cdbbcb4ca65ffa7b9ba3290074f1'
assert release['desktop_package_sha256'] == '491f8d8c16683a9dd93695acfe9ad8b4a03fa3e07cb29a22184f5187491874c8'
assert release['sidecar_sha256'] == '6c4805c72c855ea5b627b10450bb3feec56ea31b8038aed052ce9260bc11529b'
assert release['frontend_manifest_sha256'] == 'b9c08e6aa6dc04ec18d0934862b58272a052f6a18740e831e1217519380d8a51'

binding = release['diagnostics_contract']
assert binding['schema_version'] == binding['event_schema_version'] == 1
assert binding['format'] == 'NAQYA-DIAGNOSTICS'
assert binding['sha256'] == CONTRACT_SHA
assert hashlib.sha256((ROOT / binding['file']).read_bytes()).hexdigest() == CONTRACT_SHA
assert contract['schema_version'] == contract['event_schema_version'] == 1
assert contract['format'] == 'NAQYA-DIAGNOSTICS'

for value in [str(release['workflow_run_id']), release['desktop_package_sha256'], release['sidecar_sha256'], release['frontend_manifest_sha256'], CONTRACT_SHA]:
    assert value in readme, f'Aktueller Nachweis fehlt in README: {value}'

assert 'noch keine reale Endgeräte-/Mikrofon-/Langzeitabnahme' in readme
assert 'NAQYA-STT-4002' in readme
assert CONTRACT_SHA in agents
assert 'Plattforminvariante ab 0.5.1-D' in agents

for heading in ['## P0 – Freigabekritisch','## P1 – Hohe Priorität','## P2 – Qualitätsausbau','## P3 – Wartbarkeit','## Entwickler-Übergabecheckliste','## Erledigt']:
    assert todo.count(heading) == 1
assert 'Diagnosevertrag auf Windows unverändert erzwingen' in todo
assert '0.5.1-C – Professionelles Diagnose-/Debugging-/Logging-Modul' in todo
assert '0.5.1-C – Diagnose-/Release-Evidence-Vertrag verbinden' in todo
assert CONTRACT_SHA in todo
assert 'Vor jeder künftigen Entwicklerübergabe' in todo

contributing = read('CONTRIBUTING.md')
assert 'docs/ENTWICKLERDOKUMENTATION.md' in contributing and 'AGENTS.md' in contributing and 'TODO.md' in contributing

developer = read('docs/ENTWICKLERDOKUMENTATION.md')
for marker in ['## Schnellübernahme','## Repository-Landkarte','## Kritische Invarianten','## Code-Kommentare','## Lokale Qualitätsprüfung','## Nächster Arbeitsblock 0.5.1','## Definition of Done']:
    assert developer.count(marker) == 1
assert 'frontendDist' in developer
assert 'Produktversion ≠ Datenbankschema' in developer

app = read('app.js')
match = re.search(r"const VERSION='([^']+)'", app)
assert match and match.group(1) == version['version']
assert 'const DB_VERSION=2;' in app
assert "format:'NAQYA-OFFLINE-BACKUP'" in app and 'version:VERSION' in app

release_04 = read('services/release-04.js')
assert 'window.NAQYA.release={version:VERSION' in release_04
assert "version:'0.4.0'" not in release_04

kern = status['kernfunktionen']
for key in ['whisper_cpp_sidecar_release_bundle_validated','desktop_frontend_dist_deterministic','release_evidence_linux_ci_generated','diagnostics_contract_versioned','diagnostics_contract_release_bound','diagnostics_runtime_logging','diagnostics_ringbuffer_limited','diagnostics_deduplication','diagnostics_privacy_redaction','diagnostics_json_export','diagnostics_text_export','diagnostics_safe_actions','diagnostics_retry_once']:
    assert kern[key] is True, f'Projektstatus fehlt/false: {key}'

laien = read('LAIENANLEITUNG.md')
assert 'Der externe `whisper-cli` ist nur ein Fallback' in laien
assert 'vollständiges Endanwender-Desktop-Paket' in laien

for historical in ['docs/AUDIO_OFFLINE_STT.md','docs/AUDIO_NORMALISIERUNG_LIVE_STT.md','docs/NATIVE_WHISPER_DESKTOP.md']:
    assert 'Dokumentenstatus' in read(historical)

print('NAQYA 0.5.1-C Text-/Merge-/Statusintegrität: PASS')
