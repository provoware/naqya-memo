# Architektur 0.2.0

## Prinzipien

1. offline-first
2. lokale Datenhoheit
3. keine Cloudpflicht
4. UI, Domänenlogik und Plattformdienste getrennt
5. Feature-Erkennung statt versteckter Online-Fallbacks
6. Audio wird segmentiert und recovery-fähig gespeichert
7. Sprache-zu-Text arbeitet ausschließlich über lokale Provider
8. native Laufzeiten werden über stabile Verträge angebunden

## Ebenen

- UI: `index.html`, `styles.css`, `styles-02.css`
- Anwendungslogik: `app.js`
- Fähigkeiten-Erkennung: `services/capabilities.js`
- STT-Providervertrag: `services/stt-core.js`
- Persistenz: IndexedDB-Adapter
- Dateispeicher: Blob-Store in IndexedDB für die PWA
- Audio-Recovery: `audioSessions` + `audioSegments`
- Sprachmodelle: lokaler `models`-Store
- Offline-Cache: `sw.js`
- Plattformstart: `START_NAQYA.sh`, `START_NAQYA.bat`

## Audio-Pipeline

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

## Offline-STT

Die Anwendung fragt ausschließlich lokale Provider ab:

```text
SpracheZuTextDienst
  ├─ Browser On-Device SpeechRecognition
  └─ Native whisper.cpp Bridge
```

Ist kein lokaler Provider vorhanden, wird keine Online-Transkription gestartet.

## Backup

Backup-Schema 2 ist selbstenthaltend und enthält Nutzdateien einschließlich Audio und Dokumenten. SHA-256 wird verwendet, wenn WebCrypto verfügbar ist.

Große Sprachmodell-Binärdateien werden bewusst nicht in normale Nutzbackups aufgenommen; nur ihre Metadaten werden dokumentiert.

## Nächste Zielarchitektur

- Tauri-Desktop-Hülle
- echte native whisper.cpp-Laufzeit
- sichere Übergabe lokaler Modellpfade
- SQLite für native Desktop-/Mobil-Pakete
- gemeinsame Service-Verträge zwischen IndexedDB und SQLite
- streamingfähiges Backupcontainerformat statt Base64-Gesamtpaket
- messbare STT-Latenz, Echtzeitfaktor und RAM-Werte
