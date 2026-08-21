from pathlib import Path
import json
import re

root = Path(__file__).resolve().parents[1]
required = [
    '.gitignore','index.html','styles.css','styles-02.css','app.js','sw.js','manifest.webmanifest',
    'VERSION.json','PROJEKTSTATUS.json','README.md','CONTRIBUTING.md','AGENTS.md','TODO.md','CHANGELOG.md','LAIENANLEITUNG.md',
    'START_NAQYA.sh','START_NAQYA.bat','services/capabilities.js','services/native-bridge.js',
    'services/stt-core.js','services/audio-normalizer.js','services/live-stt.js','services/release-04.js',
    'docs/ARCHITEKTUR.md','docs/ENTWICKLERDOKUMENTATION.md','docs/AUDIO_OFFLINE_STT.md','docs/AUDIO_NORMALISIERUNG_LIVE_STT.md',
    'docs/NATIVE_WHISPER_DESKTOP.md','docs/DATENMODELL.md','docs/PLUGIN_VERTRAG.md','docs/WHISPER_SIDECAR.md',
    'src-tauri/Cargo.toml','src-tauri/build.rs','src-tauri/tauri.conf.json','src-tauri/src/main.rs',
    'src-tauri/sidecar/whisper-runtime.json','tests/validate_text_integrity.py','tests/validate_dist.py',
    'tests/validate_release_evidence.py','tools/stage_desktop_frontend.py','tools/generate_release_evidence.py',
    'release/RELEASE_EVIDENCE.schema.json','.github/workflows/bundle-linux.yml'
]
missing = [p for p in required if not (root / p).exists()]
assert not missing, f'Fehlende Dateien: {missing}'

version = json.loads((root / 'VERSION.json').read_text())
status = json.loads((root / 'PROJEKTSTATUS.json').read_text())
manifest = json.loads((root / 'manifest.webmanifest').read_text())
tauri = json.loads((root / 'src-tauri/tauri.conf.json').read_text())

assert version['version'] == status['version'] == tauri['version'] == '0.5.0'
assert version['phase'] == status['entwicklungsphase'] == 'TAURI-SIDECAR-INTEGRATION & REPOSITORY-KONSOLIDIERUNG'
assert version['schema_version'] == 2
assert version['live_stt_segment_ms'] == 4000
assert version['stt_pcm_rate_hz'] == 16000
assert version['model_transfer_chunk_bytes'] == 4194304
assert version['native_stt_provider'] == 'whisper.cpp-sidecar'
assert version['native_stt_fallback'] == 'whisper-cli'
assert version['sidecar_bundle_configured'] is True
assert version['sidecar_linux_ci_built'] is True
assert version['sidecar_release_bundle_validated'] is True
assert version['desktop_frontend_dist_deterministic'] is True
assert version['release_evidence_schema'] == 1
assert version['release_evidence_linux_ci_generated'] is True

progress = status['fortschritt']
assert progress['bezug'] == 'Entwicklungsblock 0.5.1'
assert progress['prozent'] == 56
assert progress['erledigt'] == 5
assert progress['gesamt'] == 9
assert len(progress['erledigte_punkte']) == 5
assert len(progress['offene_punkte']) == 4
assert status['aktueller_arbeitsstand'] == '0.5.1-B – LINUX-BUNDLE & RELEASE-NACHWEIS'
assert status['naechster_meilenstein'] == '0.5.1-C – DIAGNOSE, DEBUGGING, LOGGING & EVIDENCE-BINDUNG'

release = status['release_nachweis']
assert release['linux_bundle_validiert'] is True
assert release['workflow'] == 'NAQYA Linux-Bundle-Nachweis'
assert release['workflow_run_id'] == 32477864231
assert release['workflow_run_number'] == 1
assert release['qualitaetspruefung_run_id'] == 32477864261
assert release['qualitaetspruefung_run_number'] == 216
assert release['source_commit'] == '602d0dd974abc1fe17490492c7a453bce88089fe'
assert release['artifact_id'] == 9445169821
assert release['artifact_name'] == 'naqya-linux-bundle-nachweis-1'
assert re.fullmatch(r'[0-9a-f]{64}', release['artifact_sha256'])
assert re.fullmatch(r'[0-9a-f]{64}', release['desktop_package_sha256'])
assert re.fullmatch(r'[0-9a-f]{64}', release['sidecar_sha256'])
assert re.fullmatch(r'[0-9a-f]{64}', release['frontend_manifest_sha256'])
assert release['desktop_package_bytes'] > 0
assert release['sidecar_bytes'] > 0
assert release['release_evidence_schema'] == 1

kern = status['kernfunktionen']
assert kern['audio_segment_recovery'] is True
assert kern['audio_normalisierung_web_audio'] is True
assert kern['audio_normalisierung_pcm_hz'] == 16000
assert kern['native_live_stt_segment_ms'] == 4000
assert kern['sprachmodell_native_materialisierung'] is True
assert kern['sprachmodell_sha256_native'] is True
assert kern['sprachmodell_atomare_aktivierung'] is True
assert kern['desktop_frontend_dist_deterministic'] is True
assert kern['whisper_cpp_sidecar_bundle_configured'] is True
assert kern['whisper_cpp_sidecar_linux_ci_built'] is True
assert kern['whisper_cpp_sidecar_release_bundle_validated'] is True
assert kern['whisper_cpp_sidecar_preferred'] is True
assert kern['whisper_cpp_runtime_manifest'] is True
assert kern['whisper_cpp_external_cli_fallback'] is True
assert kern['whisper_cpp_runtime_source_diagnostic'] is True
assert kern['release_evidence_linux_ci_generated'] is True
assert kern['release_evidence_machine_readable'] is True
assert kern['release_evidence_human_readable'] is True
assert 'whisper_cpp_native_runtime_bundled' not in kern

assert manifest['start_url'] == './'
assert tauri['build']['frontendDist'] == '../dist'
assert tauri['bundle']['externalBin'] == ['binaries/naqya-whisper']

agents = (root / 'AGENTS.md').read_text()
for needle in [
    'TODO.md','Qualitätsgate','Sidecar- und Runtime-Regeln','Pflichtdateien bei Änderungen',
    'Repository- und Merge-Pflicht je Iteration','Merge-Konflikt- und Textintegritätsregeln',
    'Code- und Entwicklerdokumentationsregeln','docs/ENTWICKLERDOKUMENTATION.md','ENTWICKLERHINWEIS',
    'Nach jedem Merge'
]:
    assert needle in agents, f'AGENTS-Vertrag unvollständig: {needle}'

todo = (root / 'TODO.md').read_text()
for needle in [
    'P0 – Freigabekritisch','P1 – Hohe Priorität','P2 – Qualitätsausbau','P3 – Wartbarkeit',
    'Entwickler-Übergabecheckliste','Vor jeder künftigen Entwicklerübergabe','Erledigt','Pflegevertrag',
    'Diagnose-/Release-Evidence-Vertrag','0.5.1-B – Linux-Tauri-Bundle und Sidecar paketbezogen validieren'
]:
    assert needle in todo, f'TODO-Vertrag unvollständig: {needle}'

readme = (root / 'README.md').read_text()
for needle in [
    'CONTRIBUTING.md','docs/ENTWICKLERDOKUMENTATION.md','Entwickler-Einstieg','frontendDist',
    'Fortschritt 0.5.1','56 %','5 von 9 Hauptpunkten','0.5.1-C – DIAGNOSE, DEBUGGING, LOGGING & EVIDENCE-BINDUNG',
    '32477864231','1721b92de3a23da0ece8e9833d6949bf9b9987d7cc3de69e76d1cd50fc83f2e4',
    '6c4805c72c855ea5b627b10450bb3feec56ea31b8038aed052ce9260bc11529b'
]:
    assert needle in readme, f'README-Status/Entwicklereinstieg unvollständig: {needle}'

contributing = (root / 'CONTRIBUTING.md').read_text()
for needle in ['In 10 Minuten arbeitsfähig','Lokale Mindestprüfung','Definition „fertig“']:
    assert needle in contributing, f'CONTRIBUTING unvollständig: {needle}'

developer = (root / 'docs/ENTWICKLERDOKUMENTATION.md').read_text()
for needle in [
    'Schnellübernahme','Repository-Landkarte','Kritische Invarianten','Code-Kommentare',
    'Lokale Qualitätsprüfung','Nächster Arbeitsblock 0.5.1','frontendDist','Definition of Done'
]:
    assert needle in developer, f'Entwicklerdokumentation unvollständig: {needle}'

gitignore = (root / '.gitignore').read_text()
for needle in ['.sidecar-build/','src-tauri/binaries/','src-tauri/target/','/dist/','RELEASE_EVIDENCE.json','*.gguf','*.bin']:
    assert needle in gitignore, f'.gitignore unvollständig: {needle}'

stage = (root / 'tools/stage_desktop_frontend.py').read_text()
for needle in ['RUNTIME_FILES','BUILD_MANIFEST.json','SOURCE_DATE_EPOCH','Symlink ist im Desktop-Staging nicht erlaubt']:
    assert needle in stage, f'Desktop-Staging unvollständig: {needle}'

release_generator = (root / 'tools/generate_release_evidence.py').read_text()
for needle in ['RELEASE_EVIDENCE.json','source_sidecar_sha_matches_packaged','runtime_dependencies_resolved','NAQYA_SOURCE_COMMIT']:
    assert needle in release_generator, f'Release-Nachweisgenerator unvollständig: {needle}'

bundle_workflow = (root / '.github/workflows/bundle-linux.yml').read_text()
for needle in ['TAURI_CLI_VERSION',"'2.11.4'",'cargo tauri build --bundles deb','dpkg-deb -x','RELEASE_EVIDENCE.json','actions/upload-artifact@v4']:
    assert needle in bundle_workflow, f'Linux-Bundle-Workflow unvollständig: {needle}'

html = (root / 'index.html').read_text()
for needle in [
    'hauptinhalt','wizard','Audio & Diktat','Einstellungen','services/capabilities.js',
    'services/native-bridge.js','services/stt-core.js','services/audio-normalizer.js',
    'services/live-stt.js','services/release-04.js','styles-02.css'
]:
    assert needle in html, f'UI-Marker fehlt: {needle}'

js = (root / 'app.js').read_text()
for needle in [
    'indexedDB','MediaRecorder','audioSegments','audioSessions','recoverInterruptedAudioSessions',
    'AUDIO_SLICE_MS','NAQYA-OFFLINE-BACKUP','sha256Blob','installModelFile','serviceWorker'
]:
    assert needle in js, f'Kernfunktion fehlt: {needle}'

normalizer = (root / 'services/audio-normalizer.js').read_text()
for needle in ['TARGET_RATE=16000','LIVE_SEGMENT_MS=4000','resampleLinear','wavBlob','LivePcmCapture','createScriptProcessor','ENTWICKLERHINWEIS']:
    assert needle in normalizer, f'Audio-Normalisierung unvollständig: {needle}'

live = (root / 'services/live-stt.js').read_text()
for needle in ['materializePreferredModel','transcribeLiveSegment','startNativeLiveDictation','stopNativeLiveDictation','nativeSttElapsedMs','Echtzeitfaktor','ENTWICKLERHINWEIS']:
    assert needle in live, f'Live-STT unvollständig: {needle}'

bridge = (root / 'services/native-bridge.js').read_text()
for needle in ['__TAURI__','naqya_capabilities','naqya_model_begin','naqya_model_append','naqya_model_finish','naqya_model_abort','MODEL_CHUNK_BYTES','naqya_transcribe','ENTWICKLERHINWEIS']:
    assert needle in bridge, f'Native Bridge unvollständig: {needle}'

stt = (root / 'services/stt-core.js').read_text()
for needle in ['processLocally','nativeWhisper','transcribeNative','nativeCapabilities','ausgewogen','validateModelFile']:
    assert needle in stt, f'STT-Vertrag fehlt: {needle}'

rust = (root / 'src-tauri/src/main.rs').read_text()
for needle in [
    'naqya_capabilities','naqya_model_begin','naqya_model_append','naqya_model_finish','naqya_model_abort',
    'naqya_transcribe','NAQYA_WHISPER_CLI','whisper-cli','trusted_model_path','Sha256','WAVE',
    'stt_temp_root','app_cache_dir','write_private_temp_wav','create_new(true)','STT_TEMP_SEQUENCE',
    'tauri_plugin_shell::ShellExt','sidecar("naqya-whisper")','tauri_plugin_shell::init()',
    'bundled_sidecar_available','bundled_sidecar_preferred','whisper.cpp-sidecar','whisper.cpp-fallback',
    'ENTWICKLERHINWEIS'
]:
    assert needle in rust, f'Rust Desktop-Runtime unvollständig: {needle}'
assert rust.index('sidecar("naqya-whisper")') < rust.index('Command::new(&cli)'), 'Sidecar muss vor externem CLI-Fallback versucht werden'
assert 'Command::new("main")' not in rust, 'Generische main-PATH-Auflösung darf nicht als Whisper-Runtime verwendet werden'
assert 'std::env::temp_dir()' not in rust, 'STT-Audio darf nicht im allgemeinen System-Tempverzeichnis landen'

cargo = (root / 'src-tauri/Cargo.toml').read_text()
assert 'version = "0.5.0"' in cargo
assert 'sha2 = "0.10"' in cargo
assert 'tauri-plugin-shell = "2"' in cargo

sidecar_manifest = json.loads((root / 'src-tauri/sidecar/whisper-runtime.json').read_text())
assert sidecar_manifest['build_profile'] == 'cpu-release-static'
assert '-DBUILD_SHARED_LIBS=OFF' in sidecar_manifest['cmake_options']

sidecar_build = (root / 'tools/build_whisper_sidecar.sh').read_text()
for needle in ['UPSTREAM_TAG="v1.9.2"','306c88f4d1286aec1bf96e544632897886af5501','GGML_NATIVE=OFF','BUILD_SHARED_LIBS=OFF','ENTWICKLERHINWEIS']:
    assert needle in sidecar_build, f'Sidecar-Buildvertrag unvollständig: {needle}'

sw = (root / 'sw.js').read_text()
for needle in ['naqya-0.5.0','services/audio-normalizer.js','services/live-stt.js','services/release-04.js','services/native-bridge.js','services/stt-core.js']:
    assert needle in sw, f'Offline-Cache unvollständig: {needle}'

for f in [
    'index.html','styles.css','styles-02.css','app.js','services/capabilities.js',
    'services/native-bridge.js','services/stt-core.js','services/audio-normalizer.js',
    'services/live-stt.js','services/release-04.js'
]:
    text = (root / f).read_text()
    assert not re.search(r'https?://(?!127\.0\.0\.1|localhost)', text), f'Externe Laufzeit-URL in {f}'

print('NAQYA 0.5.1-B statische Verträge: PASS')
