# PROVOWARE – NAQYA Memo Tool 2026

Offline-first Organizer für Termine, Fristen, Aufgaben, Dokumente, Fotos, Audio-Memos, Live-Diktat, Projekte, Kategorien, Tags und Chronologie.

## Stand

**0.3.0 – NATIVE WHISPER RUNTIME & DESKTOP BRIDGE**

NAQYA bleibt vollständig lokal nutzbar und erweitert den bisherigen PWA-Kern um eine Tauri-2-Desktop-Grundstruktur. Die neue Desktop-Brücke kann lokale whisper.cpp-CLI-Laufzeiten erkennen und über einen kontrollierten Rust-Befehl ansprechen. Ein Cloud-Fallback bleibt ausgeschlossen.

## Schnellstart PWA

### Linux

```bash
chmod +x START_NAQYA.sh
./START_NAQYA.sh
```

### Windows

Doppelklick auf `START_NAQYA.bat`.

### Manuell

```bash
python3 -m http.server 8765 --bind 127.0.0.1
```

Dann `http://127.0.0.1:8765` öffnen.

> Mikrofon, Service Worker und PWA-Installation benötigen einen sicheren Kontext. `localhost`/`127.0.0.1` gilt dafür als sicher.

## Neu in 0.3.0

- Tauri-2-Desktop-Grundstruktur in `src-tauri/`
- JavaScript↔Rust-Brücke `services/native-bridge.js`
- nativer Fähigkeiten-Check über `naqya_capabilities`
- lokale whisper.cpp-CLI-Erkennung über `PATH` oder `NAQYA_WHISPER_CLI`
- nativer Transkriptionsbefehl `naqya_transcribe`
- lokale WAV→Text-Verarbeitung mit frei wählbarem Modellpfad, Sprache und Threadzahl
- temporäre Audioarbeitsdateien werden nach der Transkription entfernt
- maximale Einzeltranskriptionsgröße 512 MiB
- STT-Providerkern erkennt Browser-On-Device und Tauri-Native getrennt
- Offline-Cache und Qualitätsprüfung auf die Native-Bridge erweitert

## Bereits enthalten

- persistente Audioaufnahme in 3-Sekunden-Segmenten
- Crash-/Unterbrechungs-Recovery
- direktes Abspielen gespeicherter Aufnahmen
- vier lokale Sprachprofile: Schnell, Ausgewogen, Genau, Maximum
- lokaler Import von `.bin`/`.gguf`-Sprachmodellen mit SHA-256
- vollständiges Binärbackup für Dokumente und Audio
- modernes responsives Kachel-Dashboard
- vier Themes und fünf Schrift-/Sichtbarkeitsprofile
- lokale IndexedDB-Datenbank
- Termine, Fristen, Aufgaben, Notizen und Textdokumente
- Projekte, Kategorien und Tags
- Dokument-/Fotoablage
- Kalender-Monatsansicht
- persistente Chronologie
- globale lokale Suche
- Diagnosebereich
- automatisierte Qualitätsprüfung via GitHub Actions

## Datenschutz

Der Kern benötigt keinen Account, keine Cloud und keine Telemetrie. Diktat startet nur mit einer lokal verfügbaren STT-Engine. Es gibt keinen automatischen Online-Fallback.

## Technische Grenzen von 0.3.0

- whisper.cpp selbst wird noch nicht als reproduzierbares Sidecar mitgeliefert. Die Desktop-Laufzeit erwartet `whisper-cli` im `PATH` oder über `NAQYA_WHISPER_CLI`.
- Der native Transkriptionsbefehl erwartet WAV. Browser-Aufnahmen liegen je nach Browser als WebM/Opus vor und benötigen noch einen lokalen Normalisierungsadapter.
- In IndexedDB importierte Sprachmodelle müssen für die native Desktop-Laufzeit noch in einen kontrollierten Dateipfad materialisiert werden.
- Reale Linux-/Windows-Latenz-, CPU-, RAM- und Langzeittests stehen noch aus.

Siehe `docs/NATIVE_WHISPER_DESKTOP.md`.

## Roadmap

Nächster Hauptblock: **0.4.0 – AUDIO NORMALISIERUNG, MODELLPFAD & LIVE-SEGMENT-STT**. Ziel ist die automatische lokale WebM/Opus→PCM/WAV-Normalisierung, sichere Modellmaterialisierung, segmentweise native Transkription und messbare Live-Latenz.
