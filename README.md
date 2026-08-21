# PROVOWARE – NAQYA Memo Tool 2026

Offline-first Organizer für Termine, Fristen, Aufgaben, Dokumente, Fotos, Audio-Memos, Live-Diktat, Projekte, Kategorien, Tags und Chronologie.

## Stand

**0.2.0 – AUDIO & OFFLINE-STT CORE**

NAQYA ist eine lauffähige, installierbare PWA ohne externe Laufzeit-Abhängigkeiten. Die Version 0.2.0 härtet Audio und Offline-Spracheingabe: Aufnahmen werden alle 3 Sekunden persistent segmentiert, nach Unterbrechungen automatisch wiederhergestellt und erst beim Abschluss zu einer Audiodatei finalisiert. Für Sprache-zu-Text existiert ein Providervertrag für lokale Browser-Erkennung und die kommende native whisper.cpp-Brücke. Ein Cloud-Fallback ist ausdrücklich ausgeschlossen.

## Schnellstart

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

## Neu in 0.2.0

- Audioaufnahme mit persistenten 3-Sekunden-Segmenten
- Recovery unterbrochener Audio- und Diktataufnahmen beim nächsten Start
- gespeicherte Aufnahmen direkt abspielbar
- lokaler Fähigkeiten-Check für Mikrofon, MediaRecorder, IndexedDB, Service Worker, WebCrypto und STT-Provider
- Offline-STT-Providervertrag: Browser On-Device + native whisper.cpp-Brücke
- vier Sprachprofile: Schnell, Ausgewogen, Genau, Maximum
- lokaler Import von `.bin`/`.gguf`-Sprachmodellen mit SHA-256
- vollständiges Binärbackup für Dokumente und Audio als selbstenthaltendes NAQYA-Paket
- SHA-256-Prüfung beim Backup-Import
- Abwärtsimport des alten 0.1-Metadatenbackups
- persistenter Speicher wird, sofern unterstützt, beim Start angefordert

## Bereits enthalten

- modernes responsives Kachel-Dashboard
- vier Themes: Klar & Hell, Dunkel Kontrast, Barrierefrei Kontrast, Elegant Violett
- fünf Schrift-/Sichtbarkeitsprofile
- lokale IndexedDB-Datenbank
- Termine, Fristen, Aufgaben, Notizen und Textdokumente
- Projekte, Kategorien und Tags
- Dokument-/Fotoablage in IndexedDB
- Kalender-Monatsansicht
- persistente Chronologie
- globale lokale Suche
- PWA-Service-Worker
- Linux-/Windows-Starter
- Diagnosebereich
- automatisierte Qualitätsprüfung via GitHub Actions

## Datenschutz

Der Kern benötigt keinen Account, keine Cloud und keine Telemetrie. Diktat startet nur, wenn eine lokale STT-Engine erkannt wird. Es gibt keinen automatischen Online-Fallback.

## Technische Grenze von 0.2.0

Die native whisper.cpp-Laufzeit selbst ist noch nicht Bestandteil der PWA. 0.2.0 liefert dafür den Providervertrag, Modellmanager und Diagnosepfad. Ein lokal importiertes Modell wird gespeichert, aktiviert aber ohne native/WASM-Laufzeit noch keine Transkription.

Das Vollbackup enthält Binärdaten derzeit Base64-kodiert in einem JSON-Paket. Das ist robust und dependency-frei, aber für sehr große Backups speicherintensiver als ein späteres streamingfähiges ZIP-Containerformat.

## Roadmap

Nächster Hauptblock: **0.3.0 – NATIVE WHISPER RUNTIME & DESKTOP BRIDGE** mit Tauri/native Bridge, realer whisper.cpp-Transkription, Modellpfad-Übergabe, Latenzmessung und langzeitstabiler Desktop-Abnahme.
