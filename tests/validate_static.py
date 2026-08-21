from pathlib import Path
import json,re

root=Path(__file__).resolve().parents[1]
required=[
    'index.html','styles.css','styles-02.css','styles-03.css','app.js','app-03.js','sw.js','manifest.webmanifest',
    'VERSION.json','PROJEKTSTATUS.json','README.md','START_NAQYA.sh','START_NAQYA.bat',
    'services/native-bridge.js','services/capabilities.js','services/stt-core.js','services/pcm-worklet.js',
    'src-tauri/Cargo.toml','src-tauri/tauri.conf.json','src-tauri/build.rs','src-tauri/src/lib.rs','src-tauri/src/main.rs',
    'src-tauri/capabilities/default.json','runtime/models/README.md','docs/AUDIO_OFFLINE_STT.md'
]
missing=[p for p in required if not (root/p).exists()]
assert not missing, f'Fehlende Dateien: {missing}'

version=json.loads((root/'VERSION.json').read_text())
status=json.loads((root/'PROJEKTSTATUS.json').read_text())
manifest=json.loads((root/'manifest.webmanifest').read_text())
tauri=json.loads((root/'src-tauri/tauri.conf.json').read_text())
assert version['version']==status['version']==tauri['version']=='0.3.0'
assert version['schema_version']==2
assert status['kernfunktionen']['audio_segment_recovery'] is True
assert status['kernfunktionen']['backup_vollstaendig_binaer'] is True
assert status['kernfunktionen']['whisper_cpp_native_runtime'] is True
assert status['kernfunktionen']['native_pcm_live_capture'] is True
assert status['kernfunktionen']['native_modellimport_chunked'] is True
assert manifest['start_url']=='./'
assert tauri['app']['withGlobalTauri'] is True

html=(root/'index.html').read_text()
for needle in ['hauptinhalt','wizard','Audio & Diktat','Einstellungen','services/native-bridge.js','services/capabilities.js','services/stt-core.js','app-03.js','styles-02.css']:
    assert needle in html, f'UI-Marker fehlt: {needle}'

js=(root/'app.js').read_text()
for needle in [
    'indexedDB','MediaRecorder','audioSegments','audioSessions','recoverInterruptedAudioSessions',
    'AUDIO_SLICE_MS','NAQYA-OFFLINE-BACKUP','sha256Blob','installModelFile','serviceWorker'
]:
    assert needle in js, f'Kernfunktion fehlt: {needle}'

patch=(root/'app-03.js').read_text()
for needle in ['NAQYA_03_VERSION','startPcmCapture','transcribeNativePcm','nativeTranscriptionQueue','mergeNativeTranscript','importNativeModel']:
    assert needle in patch, f'0.3-Liveintegration fehlt: {needle}'

native_bridge=(root/'services/native-bridge.js').read_text()
for needle in ['naqya_native_status','naqya_transcribe_pcm','naqya_model_import_begin','AudioWorkletNode','resampleLinear','16000']:
    assert needle in native_bridge, f'Native Browser-Brücke fehlt: {needle}'

stt=(root/'services/stt-core.js').read_text()
for needle in ['processLocally','nativeWhisper','transcribeNativePcm','ausgewogen','validateModelFile']:
    assert needle in stt, f'STT-Vertrag fehlt: {needle}'

rust=(root/'src-tauri/src/lib.rs').read_text()
for needle in ['whisper_rs','WhisperContext','naqya_transcribe_pcm','naqya_native_status','naqya_model_import_chunk','Sha256','RuntimeState']:
    assert needle in rust, f'Native Rust-Runtime fehlt: {needle}'

cargo=(root/'src-tauri/Cargo.toml').read_text()
for needle in ['whisper-rs = "0.16.0"','tauri = { version = "2"','sha2 = "0.10"']:
    assert needle in cargo, f'Cargo-Abhängigkeit fehlt: {needle}'

sw=(root/'sw.js').read_text()
for needle in ['naqya-0.3.0','styles-03.css','services/native-bridge.js','services/pcm-worklet.js','app-03.js']:
    assert needle in sw, f'Offline-Cache unvollständig: {needle}'

for f in ['index.html','styles.css','styles-02.css','styles-03.css','app.js','app-03.js','services/native-bridge.js','services/capabilities.js','services/stt-core.js']:
    text=(root/f).read_text()
    assert not re.search(r'https?://(?!127\.0\.0\.1|localhost)',text), f'Externe Laufzeit-URL in {f}'

print('NAQYA 0.3 static validation: PASS')
