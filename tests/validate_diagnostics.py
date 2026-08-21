from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / 'diagnostics/DIAGNOSTICS_CONTRACT.json'
JS_PATH = ROOT / 'services/diagnostics.js'

contract = json.loads(CONTRACT_PATH.read_text(encoding='utf-8'))
js = JS_PATH.read_text(encoding='utf-8')

assert contract['schema_version'] == 1
assert contract['event_schema_version'] == 1
assert contract['format'] == 'NAQYA-DIAGNOSTICS'
assert contract['max_events'] == 200
assert contract['dedupe_window_ms'] == 5000
pattern = re.compile(contract['code_pattern'])
assert contract['privacy']['persist_sanitized_only'] is True
assert contract['privacy']['full_paths_allowed'] is False
assert contract['privacy']['audio_content_allowed'] is False
assert contract['privacy']['transcript_content_allowed'] is False
assert contract['privacy']['document_content_allowed'] is False
assert contract['privacy']['max_string_length'] == 240

required_actions = {'close','settings','export-json','export-text','retry-once'}
assert set(contract['safe_actions']) == required_actions
assert contract['safe_actions']['retry-once']['max_attempts'] == 1

codes = contract['codes']
assert len(codes) == len(set(codes))
for code, meta in codes.items():
    assert pattern.fullmatch(code), f'Ungültiger Diagnosecode: {code}'
    assert meta['severity'] in {'info','warning','error'}
    assert meta['category'] in {'app','data','audio','stt','model','runtime','bundle','release'}
    assert meta['what'].strip()
    assert set(meta['options']).issubset(required_actions)

for code in [
    'NAQYA-APP-1002','NAQYA-APP-1003','NAQYA-APP-1101','NAQYA-APP-1102',
    'NAQYA-STT-4002','NAQYA-STT-4003','NAQYA-STT-4004','NAQYA-STT-4005',
    'NAQYA-MODEL-5001','NAQYA-RUNTIME-6001','NAQYA-RUNTIME-6002','NAQYA-RUNTIME-6003',
    'NAQYA-RELEASE-8001'
]:
    assert code in codes

for marker in [
    "STORAGE_KEY='naqya-diagnostics-v1'",
    "CONTRACT_URL='./diagnostics/DIAGNOSTICS_CONTRACT.json'",
    'FALLBACK_MAX_EVENTS=200',
    'FALLBACK_DEDUPE_MS=5000',
    "return '[REDACTED]'",
    'repeat_count',
    'correlation_id',
    'parent_event_id',
    'release_binding',
    'retryCallbacks.delete(eventId)',
    "format:'NAQYA-DIAGNOSTICS'",
    'NAQYA.diagnostics=',
    "root.addEventListener('unhandledrejection'",
    "b.id='openDiagnostics'",
]:
    assert marker in js, f'Diagnose-Laufzeitvertrag fehlt: {marker}'

index = (ROOT / 'index.html').read_text(encoding='utf-8')
assert '<script src="services/diagnostics.js" defer></script>' in index
assert index.index('services/diagnostics.js') < index.index('services/native-bridge.js')

sw = (ROOT / 'sw.js').read_text(encoding='utf-8')
assert './services/diagnostics.js' in sw
assert './diagnostics/DIAGNOSTICS_CONTRACT.json' in sw

stage = (ROOT / 'tools/stage_desktop_frontend.py').read_text(encoding='utf-8')
assert 'services/diagnostics.js' in stage
assert 'diagnostics/DIAGNOSTICS_CONTRACT.json' in stage

bridge = (ROOT / 'services/native-bridge.js').read_text(encoding='utf-8')
for code in ['NAQYA-RUNTIME-6001','NAQYA-RUNTIME-6002','NAQYA-RUNTIME-6003','NAQYA-MODEL-5001']:
    assert code in bridge

live = (ROOT / 'services/live-stt.js').read_text(encoding='utf-8')
for code in ['NAQYA-STT-4002','NAQYA-STT-4003','NAQYA-STT-4004','NAQYA-STT-4005']:
    assert code in live

release_generator = (ROOT / 'tools/generate_release_evidence.py').read_text(encoding='utf-8')
for marker in ['diagnostics_contract','DIAGNOSTICS_CONTRACT.json','diagnostics_contract_sha256','event_schema_version']:
    assert marker in release_generator

release_schema = json.loads((ROOT / 'release/RELEASE_EVIDENCE.schema.json').read_text(encoding='utf-8'))
assert 'diagnostics_contract' in release_schema['required']
assert 'diagnostics_contract' in release_schema['properties']

contract_sha = hashlib.sha256(CONTRACT_PATH.read_bytes()).hexdigest()
assert re.fullmatch(r'[0-9a-f]{64}', contract_sha)

print('NAQYA Diagnose-/Evidence-Vertrag: PASS')
