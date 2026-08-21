from pathlib import Path
import json,re,sys
root=Path(__file__).resolve().parents[1]
required=['index.html','styles.css','app.js','sw.js','manifest.webmanifest','VERSION.json','PROJEKTSTATUS.json','README.md','START_NAQYA.sh','START_NAQYA.bat']
missing=[p for p in required if not (root/p).exists()]
assert not missing, f'Fehlende Dateien: {missing}'
version=json.loads((root/'VERSION.json').read_text())
status=json.loads((root/'PROJEKTSTATUS.json').read_text())
manifest=json.loads((root/'manifest.webmanifest').read_text())
assert version['version']==status['version']=='0.1.0'
assert manifest['start_url']=='./'
html=(root/'index.html').read_text()
for needle in ['hauptinhalt','wizard','Audio & Diktat','Einstellungen']:
    assert needle in html, f'UI-Marker fehlt: {needle}'
js=(root/'app.js').read_text()
for needle in ['indexedDB','MediaRecorder','processLocally','exportBackup','serviceWorker']:
    assert needle in js, f'Kernfunktion fehlt: {needle}'
for f in ['index.html','styles.css','app.js']:
    text=(root/f).read_text()
    assert not re.search(r'https?://(?!127\.0\.0\.1|localhost)',text), f'Externe Laufzeit-URL in {f}'
print('NAQYA static validation: PASS')
