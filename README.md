# PROVOWARE – NAQYA Memo Tool 2026

Offline-first Organizer für Termine, Fristen, Aufgaben, Dokumente, Fotos, Audio-Memos, Live-Diktat, Projekte, Kategorien, Tags und Chronologie.

## Stand

**0.5.0 – DESKTOP SIDECAR INTEGRATION & HARDENING**

NAQYA verarbeitet Sprache weiterhin ohne Cloudpflicht. Der 0.5.0-Stand baut auf der 0.4-Audio-/Modellpfad-Härtung auf und integriert zusätzlich einen reproduzierbar gebauten whisper.cpp-Sidecar in die Tauri-Desktop-Runtime. Der gebündelte Sidecar wird bevorzugt; ein explizit verfügbares externes `whisper-cli` bleibt nur als diagnostizierbarer Fallback erhalten.

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

## Neu in 0.5.0

- fest gepinnter whisper.cpp-Upstream und Commit als reproduzierbarer Runtimevertrag
- Linux-x86_64-Sidecar-Build im Qualitätsgate
- SHA-256-Prüfung des erzeugten Sidecar-Artefakts
- Tauri `externalBin` für `binaries/naqya-whisper`
- Sidecar-Ausführung über `tauri-plugin-shell`
- gebündelter Sidecar wird vor externem CLI-Fallback verwendet
- Capabilities prüfen die Runtimequelle real und diagnostizierbar
- Provider unterscheiden `whisper.cpp-sidecar` und `whisper.cpp-fallback`
- sichere temporäre STT-Dateien im privaten Tauri-App-Cache
- keine generische `main`-PATH-Auflösung für whisper.cpp
- 0.4-Funktionen bleiben erhalten: 16-kHz-Mono-WAV, geschützter Modellpfad, SHA-256-Modellprüfung, atomare Modellaktivierung und segmentiertes Live-STT

## Desktop-Spracherkennung

Die bevorzugte Desktop-Runtime ist der gebündelte `naqya-whisper`-Sidecar. Nur wenn dieser nicht verfügbar ist, darf ein explizit ermitteltes externes `whisper-cli` als Fallback verwendet werden. Die verwendete Runtimequelle bleibt diagnostizierbar.

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
gebündelter whisper.cpp-Sidecar
  ↓
optional expliziter externer CLI-Fallback
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

## Technische Grenzen von 0.5.0

- Der Linux-x86_64-Sidecar ist reproduzierbar gebaut und integriert; die vollständige Windows-Bundle-Abnahme steht noch aus.
- Die Live-PCM-Erfassung nutzt aktuell `ScriptProcessor` als breit kompatiblen Übergangsadapter. Eine AudioWorklet-Umstellung ist vorgesehen.
- Reale Linux-/Windows-Abnahmen mit verschiedenen CPUs, Modellen, Mikrofonen und Langzeitaufnahmen stehen noch aus.
- Das Vollbackup verwendet weiterhin JSON/Base64 und ist bei sehr großen Datenbeständen speicherintensiv.
- Android- und iOS-Native-STT folgen später.

## Qualitätsprüfung

GitHub Actions prüft:

- JSON-Struktur
- JavaScript-Syntax
- reproduzierbaren Linux-Sidecar-Build
- Sidecar-Integrität per SHA-256
- Rust-Formatierung
- Rust/Tauri-Kompilierung
- statische Architektur- und Sicherheitsverträge
- Shell-Syntax

## Roadmap

Nächster Hauptblock: **0.5.1 – WINDOWS SIDECAR, RELEASE-MANIFEST & REAL-HARDWARE-ABNAHME**.

Ziele:

- reproduzierbarer Windows-x86_64-Sidecar
- Release-Manifest mit Plattform, Upstream-Commit, Dateigröße und SHA-256
- echte Linux-Referenzabnahme mit Mikrofon und Modell
- Windows-Bundle-Abnahme
- Latenz-, CPU-, RAM- und 30/60-Minuten-Diktattests
- danach AudioWorklet als moderner Live-PCM-Pfad
