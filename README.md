# PROVOWARE – NAQYA Memo Tool 2026

Offline-first Organizer für Termine, Fristen, Aufgaben, Dokumente, Fotos, Audio-Memos, Live-Diktat, Projekte, Kategorien, Tags und Chronologie.

## Stand

**0.1.0 – OFFLINE FUNDAMENT PRO**

Dieser Stand ist eine lauffähige, installierbare PWA ohne externe Laufzeit-Abhängigkeiten. Kernfunktionen speichern lokal in IndexedDB. Audioaufnahme funktioniert offline. Offline-Live-Diktat wird ausschließlich dann aktiviert, wenn der Browser eine lokale On-Device-Spracherkennung anbietet; es gibt bewusst keinen Cloud-Fallback. Die universelle whisper.cpp-Brücke für Desktop/iOS/Android ist als nächster Entwicklungsblock vorgesehen.

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

## Enthalten

- modernes responsives Kachel-Dashboard
- vier Themes: Klar & Hell, Dunkel Kontrast, Barrierefrei Kontrast, Elegant Violett
- fünf Schrift-/Sichtbarkeitsprofile
- lokale IndexedDB-Datenbank
- Termine, Fristen, Aufgaben, Notizen, Textdokumente
- Projekte, Kategorien, Tags
- Dokument-/Fotoablage in IndexedDB
- Audio-Memos mit MediaRecorder
- Offline-Diktat ohne Cloud-Fallback, falls On-Device SpeechRecognition verfügbar ist
- Kalender-Monatsansicht
- persistente Chronologie
- globale Suche
- JSON-Backup und Wiederherstellung
- Papierkorb-Prinzip für Einträge
- PWA-Service-Worker
- Diagnosebereich
- automatisierte statische Qualitätsprüfung via GitHub Actions

## Datenschutz

Der Kern benötigt keinen Account, keine Cloud und keine Telemetrie. Netzwerkzugriffe sind für die Kernfunktionen nicht vorgesehen.

## Roadmap

Nächster Hauptblock: **0.2.0 – AUDIO & WHISPER OFFLINE CORE** mit nativer whisper.cpp-Abstraktion, segmentiertem Audio-Recovery, Modellmanager und messbarer Diktat-Latenz.
