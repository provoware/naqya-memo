from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {'.md','.txt','.json','.webmanifest','.yml','.yaml','.toml','.js','.html','.css','.sh','.bat','.rs'}
SKIP_PARTS = {'.git','.sidecar-build','target','binaries','node_modules','dist','.bundle-extract'}
MERGE_MARKER = re.compile(r'^(<<<<<<<(?: .*)?|=======$|>>>>>>>(?: .*)?)$', re.MULTILINE)
CONTRACT_SHA = 'fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425'
FINGERPRINT = '018452a4b7683cba40dbce2a2c221aa6b31e55c846470baef35e4baa13081aaf'
E6_STAGE = '0.5.1-E6'
E7_STAGE = '0.5.1-E7'


def read(path):
    return (ROOT / path).read_text(encoding='utf-8')


def reject_duplicate_keys(pairs):
    out = {}
    for key, value in pairs:
        assert key not in out, f'Doppelter JSON-Schlüssel: {key}'
        out[key] = value
    return out

for path in ROOT.rglob('*'):
    if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES and not any(part in SKIP_PARTS for part in path.parts):
        assert not MERGE_MARKER.search(path.read_text(encoding='utf-8')), f'Merge-Konfliktmarker in {path.relative_to(ROOT)}'

for rel in ['VERSION.json','PROJEKTSTATUS.json','manifest.webmanifest','src-tauri/tauri.conf.json','src-tauri/sidecar/whisper-runtime.json','diagnostics/DIAGNOSTICS_CONTRACT.json','release/RELEASE_EVIDENCE.schema.json']:
    json.loads(read(rel), object_pairs_hook=reject_duplicate_keys)

for rel in ['README.md','CONTRIBUTING.md','TODO.md','AGENTS.md','docs/ARCHITEKTUR.md','docs/ENTWICKLERDOKUMENTATION.md','docs/WHISPER_SIDECAR.md','docs/DIAGNOSE_LOGGING.md','docs/HARDWARE_ACCEPTANCE.md']:
    headings = re.findall(r'^## .+$', read(rel), flags=re.MULTILINE)
    duplicates = sorted({h for h in headings if headings.count(h) > 1})
    assert not duplicates, f'Doppelte H2-Abschnitte in {rel}: {duplicates}'

version = json.loads(read('VERSION.json'), object_pairs_hook=reject_duplicate_keys)
status = json.loads(read('PROJEKTSTATUS.json'), object_pairs_hook=reject_duplicate_keys)
contract = json.loads(read('diagnostics/DIAGNOSTICS_CONTRACT.json'), object_pairs_hook=reject_duplicate_keys)
readme = read('README.md')
todo = read('TODO.md')
agents = read('AGENTS.md')
developer = read('docs/ENTWICKLERDOKUMENTATION.md')
hardware_doc = read('docs/HARDWARE_ACCEPTANCE.md')
changelog = read('CHANGELOG.md')

assert version['version'] == status['version'] == '0.5.0'
assert version['phase'] == status['entwicklungsphase']
progress = status['fortschritt']
assert (progress['prozent'], progress['erledigt'], progress['gesamt']) == (89, 8, 9)
assert len(progress['erledigte_punkte']) == 8 and len(progress['offene_punkte']) == 1
assert '**Fortschritt 0.5.1:** **89 %** – **8 von 9 Hauptpunkten erledigt**' in readme
assert '### Erledigt – 8 von 9' in readme
assert '### Offen – 1 von 9' in readme

stage = status['aktueller_arbeitsstand']
assert stage.startswith((E6_STAGE, E7_STAGE)), f'Unerwarteter Arbeitsstand: {stage}'

if stage.startswith(E6_STAGE):
    assert status['naechster_meilenstein'] == '0.5.1-E7 – REALE LINUX-SMOKE-HARDWAREABNAHME'
    assert '**Aktueller Entwicklungsstand:** 0.5.1-E6 – Runtime-Metriken direkt in Hardware-Evidence' in readme
    assert '**Nächster Schritt:** 0.5.1-E7 – reale Linux-Smoke-Hardwareabnahme' in readme
    assert 'Aktueller Arbeitsstand: **0.5.1-E6 – Runtime-Metriken direkt in Hardware-Evidence**' in todo
    assert 'Nächster Entwicklungsblock: **0.5.1-E7 – Reale Linux-Smoke-Hardwareabnahme**' in todo
else:
    assert status['naechster_meilenstein'].startswith('0.5.1-E7 – REALE LINUX-SMOKE-HARDWAREABNAHME')
    assert status['kernfunktionen'].get('linux_hardware_smoke_harness') is True
    assert status['kernfunktionen'].get('linux_hardware_smoke_fail_closed') is True
    assert '**Aktueller Entwicklungsstand:** 0.5.1-E7' in readme
    assert 'reale Linux-Smoke-Hardwareabnahme' in readme
    assert 'Aktueller Arbeitsstand: **0.5.1-E7' in todo
    assert 'HARDWARE_ACCEPTANCE.json' in todo
    assert 'tools/run_linux_hardware_smoke.py --self-check' in hardware_doc
    assert '--runtime-metrics /pfad/RUNTIME_METRICS.json' in hardware_doc
    assert '--resource-metrics /pfad/RESOURCE_METRICS.json' in hardware_doc
    assert 'keine hardwarefreigabe' in hardware_doc.lower()

assert 'Fortschritt 0.5.1: **89 % – 8 von 9 Hauptpunkten erledigt**' in todo
for stage_name in ('0.5.1-E2', '0.5.1-E3', '0.5.1-E4', '0.5.1-E5', '0.5.1-E6'):
    assert f'### [erledigt] {stage_name}' in todo, f'Erledigter Entwicklungsstand fehlt in TODO: {stage_name}'
assert '**0.5.1-E6 – Runtime-Metriken direkt in Hardware-Evidence, 89 % / 8 von 9 Hauptpunkten**' in agents
assert '**0.5.1-E7 – Reale Linux-Smoke-Hardwareabnahme**' in agents
assert 'runtime_metrics_export' not in status['kernfunktionen']
for key in ('live_stt_runtime_metrics_export','hardware_acceptance_contract','hardware_acceptance_collector','process_resource_metrics','hardware_resource_metrics_import','hardware_runtime_metrics_import'):
    assert status['kernfunktionen'][key] is True, f'E6-Kernfunktion fehlt im Projektstatus: {key}'

assert '## 0.5.1-D – WINDOWS-BUNDLE, PLATTFORM-EVIDENCE & FINGERPRINT' in changelog
for document in (readme, todo, agents, developer, changelog):
    assert FINGERPRINT in document, 'Evidence-Fingerprint fehlt in aktueller Dokumentation'

release = status['release_nachweis']
for key in ('linux_bundle_validiert','windows_bundle_validiert','diagnostics_evidence_validiert','plattform_evidence_validiert','evidence_fingerprint_validiert'):
    assert release[key] is True
assert release['evidence_fingerprint'] == FINGERPRINT
binding = release['diagnostics_contract']
assert binding['sha256'] == CONTRACT_SHA
assert hashlib.sha256((ROOT / binding['file']).read_bytes()).hexdigest() == CONTRACT_SHA
assert contract['schema_version'] == contract['event_schema_version'] == 1
assert contract['format'] == 'NAQYA-DIAGNOSTICS'
for value in [CONTRACT_SHA, FINGERPRINT, str(release['workflow_run_id'])]:
    assert value in readme, f'Aktueller Nachweis fehlt in README: {value}'

app = read('app.js')
match = re.search(r"const VERSION='([^']+)'", app)
assert match and match.group(1) == version['version']
assert 'const DB_VERSION=2;' in app
assert "format:'NAQYA-OFFLINE-BACKUP'" in app and 'version:VERSION' in app

release_04 = read('services/release-04.js')
assert 'window.NAQYA.release={version:VERSION' in release_04
assert "version:'0.4.0'" not in release_04

print('NAQYA 0.5.1 E6/E7 Text-/Merge-/Dokumentations-/Statusintegrität: PASS')
