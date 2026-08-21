from pathlib import Path
import json,re

root=Path(__file__).resolve().parents[1]
required=[
    '.gitignore','index.html','styles.css','styles-02.css','app.js','sw.js','manifest.webmanifest',
    'VERSION.json','PROJEKTSTATUS.json','README.md','AGENTS.md','TODO.md','CHANGELOG.md','START_NAQYA.sh','START_NAQYA.bat',
    'services/capabilities.js','services/native-bridge.js','services/stt-core.js',
    'services/audio-normalizer.js','services/live-stt.js','services/release-04.js',
    'docs/AUDIO_OFFLINE_STT.md','src-tauri/Cargo.toml','src-tauri/build.rs',
    'src-tauri/tauri.conf.json','src-tauri/src/main.rs'
]
missing=[p for p in required if not (root/p).exists()]
assert not missing, f'Fehlende Dateien: {missing}'

version=json.loads((root/'VERSION.json').read_text())
status=json.loads((root/'PROJEKTSTATUS.json').read_text())
manifest=json.loads((root/'manifest.webmanifest').read_text())
tauri=json.loads((root/'src-tauri/tauri.conf.json').read_text())
assert version['version']==status['version']==tauri['version']=='0.5.0'
assert version['schema_version']==2
assert version['live_stt_segment_ms']==4000
assert version['stt_pcm_rate_hz']==16000
assert version['model_transfer_chunk_bytes']==4194304
assert version['native_stt_provider']=='whisper.cpp-sidecar'
assert version['native_stt_fallback']=='whisper-cli'
assert version['native_stt_fallback']=='whisper.cpp-cli'
assert status['kernfunktionen']['audio_segment_recovery'] is True
assert status['kernfunktionen']['audio_normalisierung_web_audio'] is True
assert status['kernfunktionen']['audio_normalisierung_pcm_hz']==16000
assert status['kernfunktionen']['native_live_stt_segment_ms']==4000
assert status['kernfunktionen']['sprachmodell_native_materialisierung'] is True
assert status['kernfunktionen']['sprachmodell_sha256_native'] is True
assert status['kernfunktionen']['sprachmodell_atomare_aktivierung'] is True
assert status['kernfunktionen']['whisper_cpp_native_runtime_bundled'] is True
assert status['kernfunktionen']['whisper_cpp_sidecar_preferred'] is True
assert status['kernfunktionen']['whisper_cpp_runtime_manifest'] is True
assert status['kernfunktionen']['whisper_cpp_external_cli_fallback'] is True
assert status['kernfunktionen']['whisper_cpp_runtime_source_diagnostic'] is True
assert manifest['start_url']=='./'
assert tauri['bundle']['externalBin']==['binaries/naqya-whisper']

agents=(root/'AGENTS.md').read_text()
for needle in ['TODO.md','Qualitätsgate','Sidecar- und Runtime-Regeln','Pflichtdateien bei Änderungen','Repository- und Merge-Pflicht je Iteration']:
    assert needle in agents, f'AGENTS-Vertrag unvollständig: {needle}'

todo=(root/'TODO.md').read_text()
for needle in ['P0 – Freigabekritisch','P1 – Hohe Priorität','P2 – Qualitätsausbau','Erledigt','Pflegevertrag']:
    assert needle in todo, f'TODO-Vertrag unvollständig: {needle}'

gitignore=(root/'.gitignore').read_text()
for needle in ['.sidecar-build/','src-tauri/binaries/','src-tauri/target/','*.gguf','*.bin']:
    assert needle in gitignore, f'.gitignore unvollständig: {needle}'

html=(root/'index.html').read_text()
for needle in [
    'hauptinhalt','wizard','Audio & Diktat','Einstellungen','services/capabilities.js',
    'services/native-bridge.js','services/stt-core.js','services/audio-normalizer.js',
    'services/live-stt.js','services/release-04.js','styles-02.css'
]:
    assert needle in html, f'UI-Marker fehlt: {needle}'

js=(root/'app.js').read_text()
for needle in [
    'indexedDB','MediaRecorder','audioSegments','audioSessions','recoverInterruptedAudioSessions',
    'AUDIO_SLICE_MS','NAQYA-OFFLINE-BACKUP','sha256Blob','installModelFile','serviceWorker'
]:
    assert needle in js, f'Kernfunktion fehlt: {needle}'

normalizer=(root/'services/audio-normalizer.js').read_text()
for needle in ['TARGET_RATE=16000','LIVE_SEGMENT_MS=4000','resampleLinear','wavBlob','LivePcmCapture','createScriptProcessor']:
    assert needle in normalizer, f'Audio-Normalisierung unvollständig: {needle}'

live=(root/'services/live-stt.js').read_text()
for needle in ['materializePreferredModel','transcribeLiveSegment','startNativeLiveDictation','stopNativeLiveDictation','nativeSttElapsedMs','Echtzeitfaktor']:
    assert needle in live, f'Live-STT unvollständig: {needle}'

bridge=(root/'services/native-bridge.js').read_text()
for needle in ['__TAURI__','naqya_capabilities','naqya_model_begin','naqya_model_append','naqya_model_finish','naqya_model_abort','MODEL_CHUNK_BYTES','naqya_transcribe']:
    assert needle in bridge, f'Native Bridge unvollständig: {needle}'

stt=(root/'services/stt-core.js').read_text()
for needle in ['processLocally','nativeWhisper','transcribeNative','nativeCapabilities','ausgewogen','validateModelFile']:
    assert needle in stt, f'STT-Vertrag fehlt: {needle}'

rust=(root/'src-tauri/src/main.rs').read_text()
for needle in [
    'naqya_capabilities','naqya_model_begin','naqya_model_append','naqya_model_finish','naqya_model_abort',
    'naqya_transcribe','NAQYA_WHISPER_CLI','whisper-cli','trusted_model_path','Sha256','WAVE',
    'stt_temp_root','app_cache_dir','write_private_temp_wav','create_new(true)','STT_TEMP_SEQUENCE',
    'tauri_plugin_shell::ShellExt','sidecar("naqya-whisper")','tauri_plugin_shell::init()',
    'bundled_sidecar_available','bundled_sidecar_preferred','whisper.cpp-sidecar','whisper.cpp-fallback'
]:
    assert needle in rust, f'Rust Desktop-Runtime unvollständig: {needle}'
assert rust.index('sidecar("naqya-whisper")') < rust.index('Command::new(&cli)'), 'Gebündelter Sidecar muss vor dem externen CLI-Fallback versucht werden'
assert 'Command::new("main")' not in rust, 'Generische main-PATH-Auflösung darf nicht als Whisper-Runtime verwendet werden'
assert 'std::env::temp_dir()' not in rust, 'STT-Audio darf nicht im allgemeinen System-Tempverzeichnis landen'

cargo=(root/'src-tauri/Cargo.toml').read_text()
assert 'version = "0.5.0"' in cargo
assert 'sha2 = "0.10"' in cargo
assert 'tauri-plugin-shell = "2"' in cargo

sw=(root/'sw.js').read_text()
for needle in ['naqya-0.5.0','services/audio-normalizer.js','services/live-stt.js','services/release-04.js','services/native-bridge.js','services/stt-core.js']:
    assert needle in sw, f'Offline-Cache unvollständig: {needle}'

for f in [
    'index.html','styles.css','styles-02.css','app.js','services/capabilities.js',
    'services/native-bridge.js','services/stt-core.js','services/audio-normalizer.js',
    'services/live-stt.js','services/release-04.js'
]:
    text=(root/f).read_text()
    assert not re.search(r'https?://(?!127\.0\.0\.1|localhost)',text), f'Externe Laufzeit-URL in {f}'

print('NAQYA 0.5 static validation + Sidecar-Integration + Repository-Konsolidierung: PASS')
print('NAQYA 0.5 static validation + Sidecar-Integration + Projektsteuerung: PASS')
