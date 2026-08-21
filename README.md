# PROVOWARE – NAQYA Memo Tool 2026

Offline-first Organizer für Termine, Fristen, Aufgaben, Dokumente, Fotos, Audio-Memos, Live-Diktat, Projekte, Kategorien, Tags und Chronologie.

## Stand

**0.4.0 – AUDIO NORMALISIERUNG, MODELLPFAD & LIVE-SEGMENT-STT**

NAQYA verarbeitet Sprache weiterhin ohne Cloudpflicht. Version 0.4.0 schließt die drei zentralen Desktop-Lücken der vorherigen Stufe: lokale Audio-Normalisierung auf 16 kHz Mono-WAV, kontrollierte Materialisierung importierter Sprachmodelle in einen geschützten NAQYA-Modellpfad und segmentierte native Live-Transkription über whisper.cpp.

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

## Neu in 0.4.0

- lokale Web-Audio-Normalisierung auf **16.000 Hz, Mono, PCM16/WAV**
- 4-Sekunden-PCM-Fenster für native Live-Transkription
- Originalaufnahme und 3-Sekunden-Recovery bleiben parallel erhalten
- echte lokale Live-STT-Warteschlange statt paralleler unkontrollierter Transkriptionsaufrufe
- Messung von Audiozeit, Transkriptionszeit und Echtzeitfaktor
- importierte `.bin`/`.gguf`-Modelle werden beim ersten nativen Diktat in den geschützten App-Datenpfad übertragen
- Modelltransfer speicherschonend in **4-MiB-Blöcken**
- native SHA-256-Prüfung des vollständigen Modells
- atomare Aktivierung erst nach erfolgreicher Integritätsprüfung
- Transkription akzeptiert nur Modelle aus dem kontrollierten NAQYA-Modellpfad
- abgebrochene Modelltransfers werden bereinigt
- PWA-Offline-Cache auf die 0.4-Dienste erweitert
- CI prüft JavaScript, statische Verträge sowie Rust/Tauri-Kompilierung

## Desktop-Spracherkennung

Die Desktop-Brücke erkennt `whisper-cli` entweder:

1. im lokalen `PATH`, oder
2. über die Umgebungsvariable `NAQYA_WHISPER_CLI`.

Ein importiertes Modell wird nicht direkt aus einem beliebigen Dateipfad an whisper.cpp übergeben. NAQYA überträgt es zuerst in den eigenen App-Datenbereich, prüft SHA-256 und verwendet anschließend ausschließlich diesen kontrollierten Pfad.

Der Live-Diktatpfad lautet:

```text
Mikrofon
  ↓
Originalaufnahme + 3-s-Recovery
  ↓
Web Audio PCM
  ↓
16 kHz / Mono / WAV
  ↓
4-s-Live-Segment
  ↓
whisper.cpp lokal
  ↓
Transkriptsegment
  ↓
persistenter Diktattext
```

## Bereits enthalten

- Tauri-2-Desktop-Grundstruktur
- JavaScript↔Rust-Brücke
- persistente Audioaufnahme in 3-Sekunden-Segmenten
- Crash-/Unterbrechungs-Recovery
- Browser-On-Device-STT, sofern tatsächlich lokal verfügbar
- vier Sprachprofile: Schnell, Ausgewogen, Genau, Maximum
- lokaler Import von `.bin`/`.gguf`-Sprachmodellen
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

## Datenschutz

Der Kern benötigt keinen Account, keine Cloud und keine Telemetrie. Diktat startet nur mit einer lokal verfügbaren STT-Engine. Es gibt keinen automatischen Online-Fallback.

## Technische Grenzen von 0.4.0

- whisper.cpp selbst wird weiterhin noch nicht als reproduzierbares Sidecar mit der Anwendung ausgeliefert.
- Die Live-PCM-Erfassung nutzt aktuell `ScriptProcessor` als breit kompatiblen Übergangsadapter. Eine spätere AudioWorklet-Umstellung ist vorgesehen.
- Reale Linux-/Windows-Abnahmen mit verschiedenen CPUs, Modellen, Mikrofonen und Langzeitaufnahmen stehen noch aus.
- Das Vollbackup verwendet weiterhin JSON/Base64 und ist bei sehr großen Datenbeständen speicherintensiv.
- Android- und iOS-Native-STT folgen später.

## Qualitätsprüfung

GitHub Actions prüft:

- JSON-Struktur
- JavaScript-Syntax
- Rust-Formatierung
- Rust/Tauri-Kompilierung
- statische Architekturverträge
- Shell-Syntax

## Roadmap

Nächster Hauptblock: **0.5.0 – DESKTOP SELF-SETUP, WHISPER SIDECAR & REAL-HARDWARE-ABNAHME**.

Ziele:

- reproduzierbare lokale whisper.cpp-Bereitstellung
- Self-Setup/Diagnose für Einsteiger
- erste echte Linux-Referenzabnahme
- Windows-Abnahme
- Latenz-, CPU-, RAM- und 30/60-Minuten-Diktattests
- AudioWorklet als moderner Live-PCM-Pfad
