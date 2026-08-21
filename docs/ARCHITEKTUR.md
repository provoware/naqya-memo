# Architektur 0.3.0

## Prinzipien

1. offline-first
2. lokale Datenhoheit
3. keine Cloudpflicht
4. UI, Domänenlogik und Plattformdienste getrennt
5. Fähigkeiten-Erkennung statt versteckter Online-Fallbacks
6. Originalaudio wird recovery-fähig gespeichert, unabhängig von der Transkription
7. Sprache-zu-Text arbeitet ausschließlich über lokale Provider
8. native Laufzeit wird über klar begrenzte Tauri-Befehle angebunden
9. große Modelle werden blockweise statt als riesige IPC-Nachricht übertragen
10. Performance wird mit messbaren Kennzahlen statt subjektiv bewertet

## Ebenen

```text
UI / Wizard / Kacheln
        │
        ├─ PWA-Pfad
        │    ├─ IndexedDB
        │    ├─ MediaRecorder
        │    └─ Browser On-Device STT
        │
        └─ Desktop-Pfad
             ├─ services/native-bridge.js
             ├─ Tauri IPC
             └─ Rust / whisper-rs / whisper.cpp
```

### Oberfläche

- `index.html`
- `styles.css`
- `styles-02.css`
- `styles-03.css`
- `app.js` – bestehender 0.2-Kern
- `app-03.js` – 0.3-Native-Integrationsschicht

`app-03.js` ist bewusst eine Übergangsschicht. Eine spätere Strukturstufe soll die JavaScript-Monolithen in TypeScript-Module zerlegen, ohne die Datenverträge zu ändern.

### Fähigkeiten und STT

- `services/capabilities.js`
- `services/stt-core.js`
- `services/native-bridge.js`
- `services/pcm-worklet.js`

### Native Desktop-Schicht

- `src-tauri/src/lib.rs`
- `src-tauri/src/main.rs`
- `src-tauri/Cargo.toml`
- `src-tauri/tauri.conf.json`

Die Rust-Schicht besitzt nur die für NAQYA notwendigen Befehle. Freie Dateipfade werden nicht ungeprüft vom Frontend transkribiert.

## Audio-Pipeline

### Persistente Originalaufnahme

```text
Mikrofon
  ↓
MediaRecorder
  ↓ alle 3000 ms
audioSegments
  ↓
audioSessions
  ↓ Stop / Recovery
zusammenhängender Blob
  ↓
files + entries + Chronologie
```

### Native Live-Transkription

```text
Mikrofonstream
  ↓
AudioWorklet
  ↓
PCM Fenster
  ↓
Resampling 16 kHz Mono
  ↓
Tauri IPC
  ↓
whisper-rs / whisper.cpp
  ↓
Text + Segmentzeiten + RTF
  ↓
Live-UI + transcriptDraft
```

Beide Pfade laufen parallel. Ein STT-Ausfall darf die Originalaufnahme nicht beschädigen.

## Whisper-Kontextverwaltung

`WhisperContext` wird pro Modellpfad in `RuntimeState` gecacht. Für einen neuen Transkriptionsblock wird ein neuer `WhisperState` erzeugt.

Nutzen:

- keine Modell-Neuladung alle 3 Sekunden
- wesentlich geringere Latenz
- kontrollierte Speichernutzung
- Thread-sicherer Zugriff auf bekannte Modellkontexte

## Providerreihenfolge

```text
1. Native Desktop whisper.cpp + Modell
2. Browser On-Device SpeechRecognition
3. nur Audioaufnahme
```

Es existiert kein automatischer Cloud-STT-Pfad.

## Modellverwaltung

Modelle werden gesucht in:

1. persistentem App-Datenordner `models/`
2. optionalen gebündelten Release-Ressourcen

Der native Import schreibt zunächst `.part`-Dateien und aktiviert ein Modell erst nach vollständiger Größen- und SHA-256-Prüfung.

## Persistenz

### PWA / aktuelle gemeinsame Oberfläche

- IndexedDB
- `entries`
- `projects`
- `files`
- `settings`
- `audioSessions`
- `audioSegments`
- `models`

### Native Zielarchitektur

SQLite ist weiterhin für eine spätere native Persistenzstufe vorgesehen. 0.3.0 ändert bewusst noch nicht gleichzeitig STT-Laufzeit **und** Hauptdatenbank, damit Fehlerursachen isolierbar bleiben.

## Backup

Backup-Schema 2 enthält Nutzdateien einschließlich Audio und Dokumenten. SHA-256 schützt Binärdateien beim Import.

Whisper-Modellbinärdateien werden nicht in jedes Benutzerbackup kopiert; gespeichert werden nur Modellmetadaten. Das allgemeine Backup wird später auf ein streamingfähiges Containerformat umgestellt.

## Qualitätsgates

- JSON-Verträge
- JavaScript-Syntax
- statische Strukturprüfung
- Shell-Syntax
- Linux `cargo check` für Tauri + whisper.cpp
- anschließend reale Linux-/Windows-Abnahmen

## Nächste Zielarchitektur 0.3.1+

- adaptive VAD-Fenster statt rein zeitbasierter Blöcke
- begrenzte Transkriptionswarteschlange und Lastregelung
- nativer Modellwechsel und sicheres Entfernen
- reproduzierbare Desktop-Pakete
- Release-Modellmanifest mit bekannten SHA-256-Werten
- native Benchmarkreports
- streamingfähiges Backup
- spätere TypeScript-Modularisierung
- danach native Mobiladapter
