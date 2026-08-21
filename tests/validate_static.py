from pathlib import Path
import hashlib
import json
import re

root = Path(__file__).resolve().parents[1]
CONTRACT_SHA = 'fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425'
required = [
    '.gitignore','index.html','styles.css','styles-02.css','app.js','sw.js','manifest.webmanifest',
    'VERSION.json','PROJEKTSTATUS.json','README.md','CONTRIBUTING.md','AGENTS.md','TODO.md','CHANGELOG.md','LAIENANLEITUNG.md',
    'START_NAQYA.sh','START_NAQYA.bat','services/capabilities.js','services/diagnostics.js','services/native-bridge.js',
    'services/stt-core.js','services/audio-normalizer.js','services/live-stt.js','services/release-04.js',
    'diagnostics/DIAGNOSTICS_CONTRACT.json','docs/ARCHITEKTUR.md','docs/ENTWICKLERDOKUMENTATION.md','docs/DIAGNOSE_LOGGING.md',
    'docs/AUDIO_OFFLINE_STT.md','docs/AUDIO_NORMALISIERUNG_LIVE_STT.md','docs/NATIVE_WHISPER_DESKTOP.md',
    'docs/DATENMODELL.md','docs/PLUGIN_VERTRAG.md','docs/WHISPER_SIDECAR.md',
    'src-tauri/Cargo.toml','src-tauri/build.rs','src-tauri/tauri.conf.json','src-tauri/src/main.rs',
    'src-tauri/sidecar/whisper-runtime.json','tests/validate_text_integrity.py','tests/validate_diagnostics.py',
    'tests/diagnostics_runtime.test.js','tests/validate_dist.py','tests/validate_release_evidence.py',
    'tools/stage_desktop_frontend.py','tools/generate_release_evidence.py',
    'release/RELEASE_EVIDENCE.schema.json','.github/workflows/bundle-linux.yml'
]
missing = [p for p in required if not (root / p).exists()]
assert not missing, f'Fehlende Dateien: {missing}'

version = json.loads((root / 'VERSION.json').read_text())
status = json.loads((root / 'PROJEKTSTATUS.json').read_text())
manifest = json.loads((root / 'manifest.webmanifest').read_text())
tauri = json.loads((root / 'src-tauri/tauri.conf.json').read_text())
contract_path = root / 'diagnostics/DIAGNOSTICS_CONTRACT.json'
contract = json.loads(contract_path.read_text())

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
assert (progress['prozent'], progress['erledigt'], progress['gesamt']) == (78, 7, 9)
assert len(progress['erledigte_punkte']) == 7
assert len(progress['offene_punkte']) == 2
assert status['aktueller_arbeitsstand'] == '0.5.1-C – DIAGNOSE, LOGGING & EVIDENCE-BINDUNG'
assert status['naechster_meilenstein'] == '0.5.1-D – WINDOWS-X86_64-BUNDLE & PLATTFORMÜBERGREIFENDER EVIDENCE-NACHWEIS'

release = status['release_nachweis']
assert release['linux_bundle_validiert'] is True
assert release['diagnostics_evidence_validiert'] is True
assert release['workflow'] == 'NAQYA Linux-Bundle-Nachweis'
assert release['workflow_run_id'] == 32482553418
assert release['workflow_run_number'] == 14
assert release['qualitaetspruefung_run_id'] == 32482553363
assert release['qualitaetspruefung_run_number'] == 268
assert release['source_commit'] == '0388cda77c6696017c5b00cb795f5758af2d5e22'
assert release['artifact_id'] == 9446843382
assert release['artifact_name'] == 'naqya-linux-bundle-nachweis-14'
for key in ['artifact_sha256','desktop_package_sha256','sidecar_sha256','frontend_manifest_sha256']:
    assert re.fullmatch(r'[0-9a-f]{64}', release[key]), f'Ungültiger SHA-256: {key}'
assert release['artifact_sha256'] == '8e2efd73b581bd420f348b129e554363aaf4cdbbcb4ca65ffa7b9ba3290074f1'
assert release['desktop_package_sha256'] == '491f8d8c16683a9dd93695acfe9ad8b4a03fa3e07cb29a22184f5187491874c8'
assert release['sidecar_sha256'] == '6c4805c72c855ea5b627b10450bb3feec56ea31b8038aed052ce9260bc11529b'
assert release['frontend_manifest_sha256'] == 'b9c08e6aa6dc04ec18d0934862b58272a052f6a18740e831e1217519380d8a51'
assert release['desktop_package_bytes'] == 4989730
assert release['sidecar_bytes'] == 2828584
assert release['release_evidence_schema'] == 1

binding = release['diagnostics_contract']
assert binding['file'] == 'diagnostics/DIAGNOSTICS_CONTRACT.json'
assert binding['schema_version'] == binding['event_schema_version'] == 1
assert binding['format'] == 'NAQYA-DIAGNOSTICS'
assert binding['sha256'] == CONTRACT_SHA
assert hashlib.sha256(contract_path.read_bytes()).hexdigest() == CONTRACT_SHA
assert contract['schema_version'] == contract['event_schema_version'] == 1
assert contract['format'] == 'NAQYA-DIAGNOSTICS'
assert 'NAQYA-STT-4002' in contract['codes']

kern = status['kernfunktionen']
for key in [
    'audio_segment_recovery','audio_normalisierung_web_audio','native_live_stt_queue',
    'sprachmodell_native_materialisierung','sprachmodell_sha256_native','sprachmodell_atomare_aktivierung',
    'desktop_frontend_dist_deterministic','whisper_cpp_sidecar_bundle_configured','whisper_cpp_sidecar_linux_ci_built',
    'whisper_cpp_sidecar_release_bundle_validated','whisper_cpp_sidecar_preferred','whisper_cpp_external_cli_fallback',
    'whisper_cpp_runtime_source_diagnostic','release_evidence_linux_ci_generated','release_evidence_machine_readable',
    'release_evidence_human_readable','diagnostics_contract_versioned','diagnostics_contract_release_bound',
    'diagnostics_runtime_logging','diagnostics_ringbuffer_limited','diagnostics_deduplication','diagnostics_privacy_redaction',
    'diagnostics_json_export','diagnostics_text_export','diagnostics_safe_actions','diagnostics_retry_once'
]:
    assert kern[key] is True, f'Projektstatus unvollständig: {key}'
assert kern['audio_normalisierung_pcm_hz'] == 16000
assert kern['native_live_stt_segment_ms'] == 4000
assert 'whisper_cpp_native_runtime_bundled' not in kern

assert manifest['start_url'] == './'
assert tauri['build']['frontendDist'] == '../dist'
assert tauri['bundle']['externalBin'] == ['binaries/naqya-whisper']

agents = (root / 'AGENTS.md').read_text()
for needle in [
    'TODO.md','Qualitätsgate','Sidecar- und Runtime-Regeln','Pflichtdateien bei Änderungen',
    'Repository- und Merge-Pflicht je Iteration','Merge-Konflikt- und Textintegritätsregeln',
    'Code- und Entwicklerdokumentationsregeln','docs/ENTWICKLERDOKUMENTATION.md','ENTWICKLERHINWEIS',
    'Diagnose-, Logging- und Evidence-Regeln','Plattforminvariante ab 0.5.1-D',CONTRACT_SHA
]:
    assert needle in agents, f'AGENTS-Vertrag unvollständig: {needle}'

todo = (root / 'TODO.md').read_text()
for needle in [
    'P0 – Freigabekritisch','P1 – Hohe Priorität','P2 – Qualitätsausbau','P3 – Wartbarkeit',
    'Entwickler-Übergabecheckliste','Vor jeder künftigen Entwicklerübergabe','Erledigt','Pflegevertrag',
    'Diagnosevertrag auf Windows unverändert erzwingen',
    '0.5.1-C – Professionelles Diagnose-/Debugging-/Logging-Modul',
    '0.5.1-C – Diagnose-/Release-Evidence-Vertrag verbinden',CONTRACT_SHA
]:
    assert needle in todo, f'TODO-Vertrag unvollständig: {needle}'

readme = (root / 'README.md').read_text()
for needle in [
    'CONTRIBUTING.md','docs/ENTWICKLERDOKUMENTATION.md','docs/DIAGNOSE_LOGGING.md','Entwickler-Einstieg','frontendDist',
    'Fortschritt 0.5.1','78 %','7 von 9 Hauptpunkten','0.5.1-D – WINDOWS-X86_64-BUNDLE & PLATTFORMÜBERGREIFENDER EVIDENCE-NACHWEIS',
    '32482553418','491f8d8c16683a9dd93695acfe9ad8b4a03fa3e07cb29a22184f5187491874c8',
    '6c4805c72c855ea5b627b10450bb3feec56ea31b8038aed052ce9260bc11529b',CONTRACT_SHA,'NAQYA-STT-4002'
]:
    assert needle in readme, f'README-Status/Entwicklereinstieg unvollständig: {needle}'
assert 'noch keine reale Endgeräte-/Mikrofon-/Langzeitabnahme' in readme

contributing = (root / 'CONTRIBUTING.md').read_text()
for needle in ['In 10 Minuten arbeitsfähig','Lokale Mindestprüfung','Definition „fertig“']:
    assert needle in contributing, f'CONTRIBUTING unvollständig: {needle}'

developer = (root / 'docs/ENTWICKLERDOKUMENTATION.md').read_text()
for needle in [
    'Schnellübernahme','Repository-Landkarte','Kritische Invarianten','Code-Kommentare',
    'Lokale Qualitätsprüfung','Nächster Arbeitsblock 0.5.1','frontendDist','Definition of Done',CONTRACT_SHA,'NAQYA-STT-4002'
]:
    assert needle in developer, f'Entwicklerdokumentation unvollständig: {needle}'

gitignore = (root / '.gitignore').read_text()
for needle in ['.sidecar-build/','src-tauri/binaries/','src-tauri/target/','/dist/','RELEASE_EVIDENCE.json','*.gguf','*.bin']:
    assert needle in gitignore, f'.gitignore unvollständig: {needle}'

stage = (root / 'tools/stage_desktop_frontend.py').read_text()
for needle in ['RUNTIME_FILES','BUILD_MANIFEST.json','SOURCE_DATE_EPOCH','Symlink ist im Desktop-Staging nicht erlaubt','services/diagnostics.js','diagnostics/DIAGNOSTICS_CONTRACT.json']:
    assert needle in stage, f'Desktop-Staging unvollständig: {needle}'

release_generator = (root / 'tools/generate_release_evidence.py').read_text()
for needle in ['RELEASE_EVIDENCE.json','source_sidecar_sha_matches_packaged','runtime_dependencies_resolved','NAQYA_SOURCE_COMMIT','diagnostics_contract','DIAGNOSTICS_CONTRACT.json']:
    assert needle in release_generator, f'Release-Nachweisgenerator unvollständig: {needle}'

bundle_workflow = (root / '.github/workflows/bundle-linux.yml').read_text()
for needle in ['TAURI_CLI_VERSION',"'2.11.4'",'cargo tauri build --bundles deb','dpkg-deb -x','RELEASE_EVIDENCE.json','actions/upload-artifact@v4','validate_diagnostics.py']:
    assert needle in bundle_workflow, f'Linux-Bundle-Workflow unvollständig: {needle}'

html = (root / 'index.html').read_text()
for needle in [
    'hauptinhalt','wizard','Audio & Diktat','Einstellungen','services/capabilities.js','services/diagnostics.js',
    'services/native-bridge.js','services/stt-core.js','services/audio-normalizer.js','services/live-stt.js','services/release-04.js','styles-02.css'
]:
    assert needle in html, f'UI-Marker fehlt: {needle}'
assert html.index('services/diagnostics.js') < html.index('services/native-bridge.js')

js = (root / 'app.js').read_text()
for needle in ['indexedDB','MediaRecorder','audioSegments','audioSessions','recoverInterruptedAudioSessions','AUDIO_SLICE_MS','NAQYA-OFFLINE-BACKUP','sha256Blob','installModelFile','serviceWorker']:
    assert needle in js, f'Kernfunktion fehlt: {needle}'

normalizer = (root / 'services/audio-normalizer.js').read_text()
for needle in ['TARGET_RATE=16000','LIVE_SEGMENT_MS=4000','resampleLinear','wavBlob','LivePcmCapture','createScriptProcessor','ENTWICKLERHINWEIS']:
    assert needle in normalizer, f'Audio-Normalisierung unvollständig: {needle}'

live = (root / 'services/live-stt.js').read_text()
for needle in ['materializePreferredModel','transcribeLiveSegment','startNativeLiveDictation','stopNativeLiveDictation','nativeSttElapsedMs','Echtzeitfaktor','ENTWICKLERHINWEIS','NAQYA-STT-4002']:
    assert needle in live, f'Live-STT unvollständig: {needle}'

bridge = (root / 'services/native-bridge.js').read_text()
for needle in ['__TAURI__','naqya_capabilities','naqya_model_begin','naqya_model_append','naqya_model_finish','naqya_model_abort','MODEL_CHUNK_BYTES','naqya_transcribe','ENTWICKLERHINWEIS','NAQYA-RUNTIME-6001']:
    assert needle in bridge, f'Native Bridge unvollständig: {needle}'

diagnostics = (root / 'services/diagnostics.js').read_text()
for needle in ['NAQYA.diagnostics=','FALLBACK_MAX_EVENTS=200','FALLBACK_DEDUPE_MS=5000','retry-once','NAQYA-DIAGNOSTICS','unhandledrejection']:
    assert needle in diagnostics, f'Diagnose-Laufzeitvertrag unvollständig: {needle}'

rust = (root / 'src-tauri/src/main.rs').read_text()
for needle in [
    'naqya_capabilities','naqya_model_begin','naqya_model_append','naqya_model_finish','naqya_model_abort','naqya_transcribe',
    'NAQYA_WHISPER_CLI','whisper-cli','trusted_model_path','Sha256','WAVE','stt_temp_root','app_cache_dir',
    'write_private_temp_wav','create_new(true)','STT_TEMP_SEQUENCE','tauri_plugin_shell::ShellExt','sidecar("naqya-whisper")',
    'tauri_plugin_shell::init()','bundled_sidecar_available','bundled_sidecar_preferred','whisper.cpp-sidecar','whisper.cpp-fallback','ENTWICKLERHINWEIS'
]:
    assert needle in rust, f'Rust Desktop-Runtime unvollständig: {needle}'
assert rust.index('sidecar("naqya-whisper")') < rust.index('Command::new(&cli)')
assert 'Command::new("main")' not in rust
assert 'std::env::temp_dir()' not in rust

cargo = (root / 'src-tauri/Cargo.toml').read_text()
assert 'version = "0.5.0"' in cargo
assert 'sha2 = "0.10"' in cargo
assert 'tauri-plugin-shell = "2"' in cargo

sidecar_manifest = json.loads((root / 'src-tauri/sidecar/whisper-runtime.json').read_text())
assert sidecar_manifest['build_profile'] == 'cpu-release-static'
assert '-DBUILD_SHARED_LIBS=OFF' in sidecar_manifest['cmake_options']

sidecar_build = (root / 'tools/build_whisper_sidecar.sh').read_text()
for needle in ['UPSTREAM_TAG="v1.9.2"','306c88f4d1286aec1bf96e544632897886af5501','GGML_NATIVE=OFF','BUILD_SHARED_LIBS=OFF','ENTWICKLERHINWEIS']:
    assert needle in sidecar_build

sw = (root / 'sw.js').read_text()
for needle in ['naqya-0.5.0','services/diagnostics.js','diagnostics/DIAGNOSTICS_CONTRACT.json','services/audio-normalizer.js','services/live-stt.js','services/release-04.js','services/native-bridge.js','services/stt-core.js']:
    assert needle in sw, f'Offline-Cache unvollständig: {needle}'

for f in ['index.html','styles.css','styles-02.css','app.js','services/capabilities.js','services/diagnostics.js','services/native-bridge.js','services/stt-core.js','services/audio-normalizer.js','services/live-stt.js','services/release-04.js']:
    text = (root / f).read_text()
    assert not re.search(r'https?://(?!127\.0\.0\.1|localhost)', text), f'Externe Laufzeit-URL in {f}'

print('NAQYA 0.5.1-C statische Verträge: PASS')
