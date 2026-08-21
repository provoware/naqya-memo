from pathlib import Path
import json,re

root=Path(__file__).resolve().parents[1]
required=[
    'index.html','styles.css','styles-02.css','app.js','sw.js','manifest.webmanifest',
    'VERSION.json','PROJEKTSTATUS.json','README.md','START_NAQYA.sh','START_NAQYA.bat',
    'services/capabilities.js','services/stt-core.js','docs/AUDIO_OFFLINE_STT.md'
]
missing=[p for p in required if not (root/p).exists()]
assert not missing, f'Fehlende Dateien: {missing}'

version=json.loads((root/'VERSION.json').read_text())
status=json.loads((root/'PROJEKTSTATUS.json').read_text())
manifest=json.loads((root/'manifest.webmanifest').read_text())
assert version['version']==status['version']=='0.2.0'
assert version['schema_version']==2
assert status['kernfunktionen']['audio_segment_recovery'] is True
assert status['kernfunktionen']['backup_vollstaendig_binaer'] is True
assert manifest['start_url']=='./'

html=(root/'index.html').read_text()
for needle in ['hauptinhalt','wizard','Audio & Diktat','Einstellungen','services/capabilities.js','services/stt-core.js','styles-02.css']:
    assert needle in html, f'UI-Marker fehlt: {needle}'

js=(root/'app.js').read_text()
for needle in [
    'indexedDB','MediaRecorder','audioSegments','audioSessions','recoverInterruptedAudioSessions',
    'AUDIO_SLICE_MS','NAQYA-OFFLINE-BACKUP','sha256Blob','installModelFile','serviceWorker'
]:
    assert needle in js, f'Kernfunktion fehlt: {needle}'

stt=(root/'services/stt-core.js').read_text()
for needle in ['processLocally','nativeWhisper','transcribeNative','ausgewogen','validateModelFile']:
    assert needle in stt, f'STT-Vertrag fehlt: {needle}'

sw=(root/'sw.js').read_text()
for needle in ['naqya-0.2.0','styles-02.css','services/capabilities.js','services/stt-core.js']:
    assert needle in sw, f'Offline-Cache unvollständig: {needle}'

for f in ['index.html','styles.css','styles-02.css','app.js','services/capabilities.js','services/stt-core.js']:
    text=(root/f).read_text()
    assert not re.search(r'https?://(?!127\.0\.0\.1|localhost)',text), f'Externe Laufzeit-URL in {f}'

print('NAQYA 0.2 static validation: PASS')
