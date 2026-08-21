# Architektur – aktueller Stand 0.5.0

## Prinzipien

1. offline-first
2. lokale Datenhoheit
3. keine Cloudpflicht
4. UI, Domänenlogik und Plattformdienste getrennt
5. Feature-Erkennung statt versteckter Online-Fallbacks
6. Audio wird segmentiert und recovery-fähig gespeichert
7. Sprache-zu-Text arbeitet ausschließlich über lokale Provider
8. native Laufzeiten werden über stabile, prüfbare Verträge angebunden
9. Runtime- und Modellartefakte werden getrennt verifiziert
10. Releasefähigkeit wird erst nach reproduzierbarem Build, Integritätsnachweis und Plattformabnahme behauptet

## Ebenen

- UI: `index.html`, `styles.css`, `styles-02.css`
- Anwendungslogik: `app.js`
- Fähigkeiten-Erkennung: `services/capabilities.js`
- Native Bridge: `services/native-bridge.js`
- STT-Providervertrag: `services/stt-core.js`
- Audio-Normalisierung: `services/audio-normalizer.js`
- segmentiertes Live-STT: `services/live-stt.js`
- Persistenz: IndexedDB
- Dateispeicher: Blob-Store in IndexedDB
- Audio-Recovery: `audioSessions` + `audioSegments`
- Sprachmodelle: lokaler `models`-Store plus geschützter nativer Modellpfad
- Offline-Cache: `sw.js`
- Desktop-Frontend-Staging: `tools/stage_desktop_frontend.py` → `dist/`
- Desktop-Hülle: Tauri 2 unter `src-tauri/`
- native STT-Runtime: Tauri-Sidecar `naqya-whisper`
- Runtimevertrag: `src-tauri/sidecar/whisper-runtime.json`
- Sidecar-Build: `tools/build_whisper_sidecar.sh`

## Desktop-Frontend-Staging

Tauri verwendet nicht mehr den Repository-Stamm als Frontendquelle. Vor einem Desktop-Build erzeugt `tools/stage_desktop_frontend.py` ein frisches `dist/` aus einer expliziten Allowlist der benötigten Runtime-Dateien.

Das Staging:

- löscht ein vorhandenes generiertes `dist/` vor dem Neuaufbau
- lehnt Symlink-Quellen ab
- kopiert ausschließlich die festgelegten HTML-, CSS-, JavaScript-, Manifest- und Icon-Dateien
- erzeugt `NAQYA_FRONTEND_MANIFEST.json` mit Dateigröße und SHA-256 je Runtime-Datei
- verifiziert anschließend den exakten Dateisatz
- wird durch `tests/validate_frontend_staging.py` im CI geprüft

Damit gelangen Dokumentation, Tests, Repository-Metadaten, lokale Sprachmodelle, Sidecar-Buildreste und andere Entwicklerdateien nicht versehentlich in das Desktop-Frontend.

## Audio-Pipeline

```text
Mikrofon
  ├─ MediaRecorder
  │    ↓ alle 3000 ms
  │  audioSegments
  │    ↓ Stop / Recovery
  │  dauerhafte Originalaufnahme
  │
  └─ Web Audio PCM
       ↓ Mono / Resampling
     16 kHz PCM16/WAV
       ↓ alle 4000 ms
     Live-STT-Warteschlange
       ↓
     lokale native Runtime
       ↓
     Transkript
```

Originalaudio-Recovery und STT-Verarbeitung sind bewusst getrennte Pfade.

## Native STT-Runtime

Priorität:

```text
Tauri-Sidecar naqya-whisper
  ↓ falls nicht verfügbar
expliziter lokaler whisper-cli-Fallback
  ↓ falls nicht verfügbar
keine native STT
```

Der Sidecar wird aus einem fest gepinnten whisper.cpp-Upstream-Commit gebaut. Linux x86_64 wird im CI gebaut und per SHA-256 geprüft. Tauri ist über `bundle.externalBin` für das Einbetten des Sidecars konfiguriert.

Ein vollständiges Endanwender-Bundle ist damit noch nicht automatisch abgenommen. Dafür muss zusätzlich das erzeugte Paket selbst geprüft werden.

## Sprachmodell-Vertrauensgrenze

Importierte `.bin`-/`.gguf`-Modelle werden in 4-MiB-Blöcken in den nativen NAQYA-Modellbereich übertragen. Vor Aktivierung wird der vollständige SHA-256 geprüft. Native Transkription akzeptiert nur kanonisierte Modellpfade innerhalb dieses geschützten Bereichs.

## Temporäre STT-Dateien

Temporäre WAV-Dateien liegen im privaten Tauri-App-Cache. Dateinamen werden kollisionsgeschützt erzeugt; die Datei wird vor Übergabe an whisper.cpp synchronisiert und nach der Verarbeitung bereinigt.

## Offline-STT

Die Anwendung verwendet ausschließlich lokale Provider:

```text
SpracheZuTextDienst
  ├─ Browser On-Device SpeechRecognition, sofern wirklich lokal verfügbar
  └─ Native Tauri/whisper.cpp Runtime
```

Ist kein lokaler Provider vorhanden, wird keine Online-Transkription gestartet.

## Backup

Backup-Schema 2 ist selbstenthaltend und enthält Nutzdateien einschließlich Audio und Dokumenten. SHA-256 wird für Binärdateien verwendet. Große Sprachmodell-Binärdateien sind bewusst nicht Bestandteil des normalen Nutzbackups.

## Aktuelle technische Grenzen

- vollständiger Linux-Tauri-Bundle-Test steht noch aus
- Windows-Sidecar und Windows-Bundle stehen noch aus
- reale Hardware-/Mikrofonabnahme steht aus
- `app.js` führt noch eine veraltete Produktversionskonstante 0.2.0; das IndexedDB-Schema `DB_VERSION=2` ist davon unabhängig
- `ScriptProcessor` ist noch Übergangsadapter und soll später durch `AudioWorklet` ersetzt werden
- Vollbackup ist noch JSON/Base64 statt streamingfähigem Container
- native Mobiladapter stehen aus

## Nächste Zielarchitektur

- end-to-end geprüfte Linux-/Windows-Tauri-Bundles auf Basis des deterministischen Frontend-Stagings
- maschinenlesbare Release-Artefakt-Nachweise
- reale Messwerte für Latenz, Echtzeitfaktor, CPU und RAM
- AudioWorklet für den Live-PCM-Pfad
- langfristig gemeinsamer Persistenzvertrag für Browser- und native Speicheradapter
