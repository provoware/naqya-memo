# PROVOWARE – NAQYA Memo Tool 2026

Offline-first Organizer für Termine, Fristen, Aufgaben, Dokumente, Fotos, Audio-Memos, Live-Diktat, Projekte, Kategorien, Tags und Chronologie.

## Stand

**0.3.0 – NATIVE WHISPER RUNTIME & DESKTOP BRIDGE**

NAQYA besitzt weiterhin die vollständig offlinefähige PWA und ergänzt sie jetzt um eine native Tauri-Desktop-Schicht für Linux und Windows. Die Desktop-App enthält eine lokale `whisper.cpp`-Runtime über `whisper-rs 0.16.0`. Mikrofon-Audio wird zusätzlich zur persistenten Originalaufnahme als Mono-PCM verarbeitet, auf 16 kHz gebracht und in kurzen Blöcken lokal transkribiert.

**Kein Cloud-Fallback:** Ist keine lokale STT-Engine verfügbar, bleibt Audioaufnahme nutzbar, aber NAQYA sendet nichts automatisch an einen Online-Dienst.

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

## Native Desktop-Entwicklung

Voraussetzungen:

- Rust stable
- Tauri-2-Systembibliotheken
- C/C++-Compiler, CMake und Clang
- optional ein mehrsprachiges Whisper-Modell

Aus Repository-Wurzel:

```bash
python3 -m http.server 8765 --bind 127.0.0.1 &
cargo run --manifest-path src-tauri/Cargo.toml
```

Ausführliche Anweisungen: `docs/NATIVE_DESKTOP.md`.

## Neu in 0.3.0

- echte lokale `whisper.cpp`-Runtime über `whisper-rs 0.16.0`
- Tauri-2-Desktop-Brücke
- nativer Status- und Diagnosebefehl
- lokales PCM-Live-Diktat mit 16 kHz Mono
- AudioWorklet mit kompatiblem Fallback
- fortlaufende 3-Sekunden-Transkriptionsblöcke
- Originalaudio bleibt unabhängig vom STT-Pfad persistent erhalten
- Kontextcache: Sprachmodell wird nicht für jeden Block neu geladen
- Segmentzeitstempel
- Messung von Verarbeitungszeit und Echtzeitfaktor (RTF)
- blockweiser Modellimport statt riesiger IPC-Nachrichten
- SHA-256-Prüfung des nativen Modells
- Modellprofile Schnell / Ausgewogen / Genau / Maximum
- native Modellsuche im persistenten App-Datenordner und in Release-Ressourcen
- Linux-CI kompiliert Tauri + whisper.cpp mit `cargo check`

## Bereits enthalten

- modernes responsives Kachel-Dashboard
- vier Themes: Klar & Hell, Dunkel Kontrast, Barrierefrei Kontrast, Elegant Violett
- fünf Schrift-/Sichtbarkeitsprofile
- lokale IndexedDB-Datenbank
- Termine, Fristen, Aufgaben, Notizen und Textdokumente
- Projekte, Kategorien und Tags
- Dokument-/Fotoablage
- Audioaufnahme mit persistenten 3-Sekunden-Segmenten
- Crash-/Unterbrechungs-Recovery
- Kalender-Monatsansicht
- persistente Chronologie
- globale lokale Suche
- vollständiges Binärbackup mit SHA-256
- PWA-Service-Worker
- Diagnosebereich

## Sprachmodelle

Für deutsche Diktate mehrsprachige Whisper-Modelle verwenden. Empfohlene Zuordnung:

| Profil | Modell | Richtgröße |
|---|---|---:|
| Schnell | tiny | ~75 MiB |
| Ausgewogen | base | ~142 MiB |
| Genau | small | ~466 MiB |
| Maximum | medium | ~1536 MiB |

Die Modelldatei kann in der Desktop-App blockweise importiert werden. Große Modelldateien werden nicht in Git eingecheckt.

## Datenschutz

- kein Account erforderlich
- keine Cloudpflicht
- keine Telemetrie im Kern
- lokale Audioaufnahme
- lokale Desktop-Transkription
- PWA-STT nur bei echter On-Device-Erkennung
- kein versteckter Online-Fallback

## Bekannte Grenzen

- Linux- und Windows-Releasepakete müssen noch auf realen Zielsystemen abgenommen werden.
- 3-Sekunden-Fenster sind zunächst zeitbasiert; adaptive VAD-Fenster folgen.
- auf langsamen Rechnern kann die Transkriptionswarteschlange wachsen.
- das Vollbackup nutzt für Binärdaten noch Base64/JSON und ist bei sehr großen Beständen RAM-intensiv.
- native Android-/iOS-STT-Brücken folgen später.

## Nächster Meilenstein

**0.3.1 – DESKTOP HARDENING & RELEASE PACKAGING**

Schwerpunkte: reale Linux-/Windows-Abnahme, adaptive Lastregelung, VAD, native Modellpflege, reproduzierbare Benchmarks und belastbare Desktop-Pakete.
