from pathlib import Path
import hashlib
import json
import re

root = Path(__file__).resolve().parents[1]
CONTRACT_SHA = 'fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425'
FINGERPRINT = '018452a4b7683cba40dbce2a2c221aa6b31e55c846470baef35e4baa13081aaf'
E6 = '0.5.1-E6 – RUNTIME-METRIKEN DIREKT IN HARDWARE-EVIDENCE'
E7 = '0.5.1-E7 – GEFÜHRTE REALE LINUX-SMOKE-HARDWAREABNAHME VORBEREITET'

version = json.loads((root / 'VERSION.json').read_text())
status = json.loads((root / 'PROJEKTSTATUS.json').read_text())
tauri = json.loads((root / 'src-tauri/tauri.conf.json').read_text())
contract_path = root / 'diagnostics/DIAGNOSTICS_CONTRACT.json'
contract = json.loads(contract_path.read_text())

assert version['version'] == status['version'] == tauri['version'] == '0.5.0'
assert version['phase'] == status['entwicklungsphase']
assert version['live_stt_segment_ms'] == 4000
assert version['stt_pcm_rate_hz'] == 16000

progress = status['fortschritt']
assert (progress['prozent'], progress['erledigt'], progress['gesamt']) == (89, 8, 9)
assert len(progress['erledigte_punkte']) == 8
assert len(progress['offene_punkte']) == 1
assert status['aktueller_arbeitsstand'] in (E6, E7)
assert status['naechster_meilenstein'].startswith('0.5.1-E7 – REALE LINUX-SMOKE-HARDWAREABNAHME')

release = status['release_nachweis']
for key in ('linux_bundle_validiert','windows_bundle_validiert','diagnostics_evidence_validiert','plattform_evidence_validiert','evidence_fingerprint_validiert'):
    assert release[key] is True
assert re.fullmatch(r'[0-9a-f]{40}', release['source_commit'])
assert release['evidence_fingerprint'] == FINGERPRINT
for key in ('plattformvergleich_artifact_sha256','linux_artifact_sha256','windows_artifact_sha256'):
    assert re.fullmatch(r'[0-9a-f]{64}', release[key])

binding = release['diagnostics_contract']
assert binding['sha256'] == CONTRACT_SHA
assert hashlib.sha256(contract_path.read_bytes()).hexdigest() == CONTRACT_SHA
assert contract['schema_version'] == contract['event_schema_version'] == 1
assert contract['format'] == 'NAQYA-DIAGNOSTICS'
assert 'NAQYA-STT-4002' in contract['codes']

kern = status['kernfunktionen']
for key in (
    'live_stt_runtime_metrics_export',
    'hardware_acceptance_contract',
    'hardware_acceptance_collector',
    'process_resource_metrics',
    'hardware_resource_metrics_import',
    'hardware_runtime_metrics_import',
):
    assert kern[key] is True
if status['aktueller_arbeitsstand'] == E7:
    assert kern['linux_hardware_smoke_harness'] is True
    assert kern['linux_hardware_smoke_fail_closed'] is True

assert tauri['build']['frontendDist'] == '../dist'
assert tauri['bundle']['externalBin'] == ['binaries/naqya-whisper']

readme = (root / 'README.md').read_text()
for needle in (
    '89 %',
    '8 von 9 Hauptpunkten',
    FINGERPRINT,
    CONTRACT_SHA,
    '0.5.1-E6',
    '0.5.1-E7',
):
    assert needle in readme

release_generator = (root / 'tools/generate_release_evidence.py').read_text()
for needle in ('evidence_fingerprint','diagnostic_codes_sha256','diagnostics_contract','NAQYA_SOURCE_COMMIT'):
    assert needle in release_generator

comparison = (root / 'tests/compare_release_evidence.py').read_text()
assert 'evidence_fingerprint' in comparison

normalizer = (root / 'services/audio-normalizer.js').read_text()
assert 'TARGET_RATE=16000' in normalizer
assert 'LIVE_SEGMENT_MS=4000' in normalizer
assert 'createScriptProcessor' in normalizer

live_stt = (root / 'services/live-stt.js').read_text()
for needle in (
    'segmentsAttempted',
    'segmentsFailed',
    'capturedAudioMs',
    'rtfMax',
    'runtimeMetricsSnapshot',
    'nativeSttRuntimeMetrics',
    'realtimeFactorAvg',
    'realtimeFactorMax',
):
    assert needle in live_stt
assert 'segmentsLost:liveState.segmentsFailed' in live_stt
assert 'realtimeFactorMax:Number(liveState.rtfMax.toFixed(6))' in live_stt

print('NAQYA statische Projektverträge: PASS – E6/E7-Übergang, 89 % und Evidence-Fingerprint konsistent; reale E7-Hardwarefreigabe bleibt separat')
