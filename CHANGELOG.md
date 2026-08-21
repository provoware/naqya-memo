# Änderungsprotokoll

## 0.5.1-D – WINDOWS-BUNDLE, PLATTFORM-EVIDENCE & FINGERPRINT

- whisper.cpp `v1.9.2` aus Commit `306c88f4d1286aec1bf96e544632897886af5501` für Windows x86_64/MSVC reproduzierbar gebaut
- echtes Tauri-NSIS-Bundle erzeugt und den daraus extrahierten `naqya-whisper.exe` gestartet
- Build- und Paket-Sidecar bytegenau per SHA-256 verglichen
- Linux- und Windows-Release-Evidence automatisiert auf gemeinsamen Quellstand, whisper.cpp-Provenienz und identischen Diagnosevertrag geprüft
- plattformübergreifenden Evidence-Fingerprint eingeführt; Paket- und Sidecar-Binärhashes bleiben bewusst plattformspezifisch
- validierter Evidence-Fingerprint: `018452a4b7683cba40dbce2a2c221aa6b31e55c846470baef35e4baa13081aaf`
- Diagnosevertrag unverändert gebunden: SHA-256 `fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425`
- Projektstatus auf **89 % / 8 von 9 Hauptpunkten** synchronisiert
- statischen Vertragsmarker `error_catalog_sha256` auf den tatsächlich verwendeten Namen `diagnostic_codes_sha256` korrigiert
- nächster Block: 0.5.1-E mit realer Hardware-/Mikrofonabnahme, Langzeitmessungen und anschließendem AudioWorklet-Vergleich

## 0.5.1-C – DIAGNOSE, LOGGING & EVIDENCE-BINDUNG

- `diagnostics/DIAGNOSTICS_CONTRACT.json` als kanonischen versionierten Diagnosevertrag eingeführt
- stabile NAQYA-Codefamilien für App, Daten, Audio, STT, Modell, Runtime, Bundle und Release festgelegt
- `services/diagnostics.js` mit fail-safe Offline-Ringpuffer, Deduplizierung und `repeat_count` integriert
- Privacy-Redaktion für Audio/Base64, Transkripte, Dokument-/Notiztexte, Tokens, Secrets und vollständige Benutzerpfade eingeführt
- Ereignisse führen `event_id`, `correlation_id`, optional `parent_event_id` sowie Was/Wann/Wo/Wie/Ergebnis/Optionen
- laienverständlichen Diagnose-/Fehlerdialog mit sichtbarem Fehlercode und ausschließlich registrierten Safe Actions ergänzt
- JSON- und TXT-Diagnoseexport vollständig offline integriert
- `retry-once` auf einen expliziten einmaligen Versuch begrenzt; keine automatischen Retry-Endlosschleifen
- Native-Bridge- und Live-STT-Fehlerpfade mit stabilen Codes instrumentiert
- echten Node-Laufzeittest für Ringpuffer, Deduplizierung, Privacy und Retry-Verhalten ergänzt
- Diagnosevertrag in Offline-Cache und deterministisches Desktop-`dist/` aufgenommen
- `RELEASE_EVIDENCE.json` bindet Diagnoseformat, Schema, Ereignisschema und Contract-SHA
- validierter Diagnosevertrag: SHA-256 `fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425`

## 0.5.1-B1 – DETERMINISTISCHE DEB-REPRODUZIERBARKEIT

- Zeit-/Archivmetadaten des Tauri-DEB normalisiert
- festes `SOURCE_DATE_EPOCH` und deterministisches `dpkg-deb`-Profil eingeführt
- Repacker baut intern zweimal und verlangt Bytegleichheit
- Regressionstest verlangt identische normalisierte Pakete aus inhaltlich identischen Roh-DEBs
- Release Evidence führt `dpkg-deb-normalized-v1` und `package_repack_deterministic=true`

## 0.5.1-B – LINUX-BUNDLE & RELEASE-NACHWEIS

- Tauri-`frontendDist` auf deterministisch gestagtes `../dist` umgestellt
- explizite Desktop-Runtime-Allowlist und `BUILD_MANIFEST.json` mit SHA-256 eingeführt
- whisper.cpp-Buildprofil auf `cpu-release-static` und `BUILD_SHARED_LIBS=OFF` gehärtet
- separaten Linux-Bundle-Workflow mit pfadbasierten Triggern eingeführt
- Tauri CLI auf 2.11.4 gepinnt
- reales Linux-DEB gebaut und extrahiert
- enthaltenen `naqya-whisper` aus dem Paketkontext gestartet
- Laufzeitabhängigkeiten geprüft und Build-/Paket-Sidecar per SHA-256 abgeglichen
- `RELEASE_EVIDENCE.schema.json`, JSON- und Textnachweis eingeführt

## 0.5.1-A – PRODUKTVERSIONS-KONSISTENZ

- PWA-Produktversion in `app.js` auf 0.5.0 synchronisiert
- Gleichheit gegen `VERSION.json` automatisiert abgesichert
- Backup-Metadaten an dieselbe `VERSION`-Konstante gebunden
- historischen `services/release-04.js`-Override gegen Rückfall auf 0.4.0 gehärtet
- `DB_VERSION=2` bewusst unverändert gelassen, da Produktversion und IndexedDB-Schema getrennte Verträge sind

## 0.5.0 – TAURI-SIDECAR-INTEGRATION & REPOSITORY-KONSOLIDIERUNG

- reproduzierbaren whisper.cpp-Runtimevertrag mit festem Tag und Commit eingeführt
- Tauri `externalBin` und `tauri-plugin-shell` integriert
- Sidecar gegenüber externem `whisper-cli`-Fallback priorisiert
- private STT-Tempdateien und geschützten nativen Modellpfad gehärtet
- Linux-x86_64-Sidecar im CI gebaut und per SHA-256 geprüft
- `AGENTS.md`, `TODO.md`, Entwicklerdokumentation und Repository-/Textintegritätsverträge eingeführt
- mergebedingte doppelte README-/TODO-/JSON-Strukturen bereinigt

## 0.4.0 – AUDIO NORMALISIERUNG, MODELLPFAD & LIVE-SEGMENT-STT

- 16-kHz-Mono-PCM16/WAV-Normalisierung
- 4-Sekunden-Live-STT-Segmente mit serieller Warteschlange
- 3-Sekunden-Audio-Recovery parallel erhalten
- 4-MiB-Modelltransfer, native SHA-256-Prüfung und atomare Modellaktivierung
- geschützten Modellpfad und WAV-Validierung eingeführt
- Rust/Tauri-Kompilierungsprüfung in CI ergänzt

## 0.3.0 – NATIVE WHISPER RUNTIME & DESKTOP BRIDGE

- Tauri-2-Desktop-Grundstruktur
- JavaScript↔Rust-Brücke für Fähigkeiten und Transkription
- kontrollierte `whisper-cli`-Erkennung und `NAQYA_WHISPER_CLI`
- Größenbegrenzung und Fehlerbehandlung für native Transkription

## 0.2.0 – AUDIO & OFFLINE-STT CORE

- persistente Audioaufnahme in 3-Sekunden-Segmenten
- Crash-/Unterbrechungs-Recovery
- lokaler STT-Providervertrag
- lokale Sprachmodellprofile und SHA-256-Modellimport
- vollständiges Backup von Metadaten und Binärdateien

## 0.1.0 – OFFLINE FUNDAMENT PRO

- erste lauffähige Offline-PWA
- responsive Oberfläche, IndexedDB-Datenkern und Dashboard
- Audio-Memo-Aufnahme, lokale Suche und PWA-Service-Worker
- Linux-/Windows-Starter und statische GitHub-Actions-Prüfung