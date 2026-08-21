# Entwicklerdokumentation – NAQYA Memo Tool 2026

> **Dokumentenstatus:** Kanonischer technischer Einstieg für den aktuell validierten 0.5.0-Stand. Vor jeder neuen Iteration zusätzlich den realen GitHub-`main`-, PR- und CI-Stand prüfen.

## Ziel dieser Dokumentation

Ein Entwickler ohne vorherige Projektkenntnis soll nach kurzer Lektüre sicher Änderungen umsetzen können, ohne Offline-, Datenintegritäts-, Audio-, Modell- oder Sidecar-Verträge versehentlich zu brechen.

Diese Datei erklärt den **Arbeitsweg und die Vertrauensgrenzen**. Die fachlichen Detailverträge bleiben in den spezialisierten Dateien unter `docs/`.

## Schnellübernahme

Arbeitsreihenfolge für einen neuen Entwickler:

1. `README.md` – aktueller Produkt- und Freigabestand.
2. `AGENTS.md` – verbindliche Entwicklungs-, Merge- und Freigaberegeln.
3. `TODO.md` – aktuelle Prioritäten und Abnahmekriterien.
4. diese Datei – technische Orientierung und lokale Befehle.
5. `docs/ARCHITEKTUR.md` – Systemebenen und Datenflüsse.
6. bei STT-/Sidecar-Arbeit zusätzlich `docs/WHISPER_SIDECAR.md`, `docs/DATENMODELL.md` und die historischen Audio-/STT-Verträge.

Vor der ersten Änderung:

```bash
git status
git branch --show-current
git rev-parse HEAD
```

Danach auf GitHub prüfen, ob der lokale Commit dem erwarteten `main` entspricht und ob offene Pull Requests oder fehlgeschlagene Prüfungen existieren.

## Aktueller technischer Stand

Produktversion: **0.5.0**

Validiert sind derzeit:

- statische Offline-PWA mit IndexedDB-Datenkern
- 3-Sekunden-Audiosegmente mit Recovery
- 16-kHz-Mono-PCM16/WAV-Normalisierung
- 4-Sekunden-Live-STT-Segmente
- blockweiser nativer Modelltransfer
- SHA-256-Prüfung und atomare Modellaktivierung
- Tauri-2-Desktop-Brücke
- bevorzugter whisper.cpp-Sidecar `naqya-whisper`
- reproduzierbarer Linux-x86_64-Sidecar-Build aus gepinntem whisper.cpp-Upstream
- Text-, Merge-, Rust-, JavaScript-, Shell- und Sidecar-Verträge im CI

Noch **nicht** als Release abgenommen sind ein vollständiges Linux-Endanwender-Bundle, das Windows-Bundle und reale Hardware-/Mikrofontests.

## Repository-Landkarte

| Pfad | Verantwortung | Typische Änderungsfolgen |
|---|---|---|
| `index.html` | statische UI-Struktur und Modulreihenfolge | UI, CSP, Service-Worker-Cache, statische Tests |
| `styles.css`, `styles-02.css` | Layout, Responsivität, Sichtbarkeit | UI-Abnahme |
| `app.js` | zentraler PWA-Controller, IndexedDB, Audio-Recovery, Backup, Rendering | Datenmodell, Backup, UI, Tests |
| `services/capabilities.js` | lokale Fähigkeitenerkennung | Diagnose, Providerwahl |
| `services/native-bridge.js` | JavaScript↔Tauri-IPC und Modelltransfer | Rust-Commands, Speicherverbrauch, Modellintegrität |
| `services/stt-core.js` | STT-Providervertrag und Modellprofile | Providerwahl, Modellvalidierung |
| `services/audio-normalizer.js` | Mono-/16-kHz-/WAV-Vertrag | Live-STT, AudioWorklet-Migration |
| `services/live-stt.js` | segmentierte native Live-Transkription | Reihenfolge, Persistenz, Echtzeitfaktor |
| `sw.js` | Offline-Cache | bei neuen/umbenannten Frontenddateien aktualisieren |
| `src-tauri/src/main.rs` | native Sicherheitsgrenzen, Modellablage, Temp-WAV, Sidecar/Fallback | Rust-, Sicherheits- und Runtime-Tests |
| `src-tauri/tauri.conf.json` | Tauri-App und Bundle-Konfiguration | Desktop-Build und Release |
| `src-tauri/sidecar/whisper-runtime.json` | Supply-Chain-/Zielplattformvertrag | Buildscript, Tests, Release-Nachweis |
| `tools/build_whisper_sidecar.sh` | reproduzierbarer whisper.cpp-Build | CI, Zielnamen, Hash-Nachweis |
| `.github/workflows/validate.yml` | kanonisches Qualitätsgate | lokale Prüfmatrix synchron halten |
| `tests/` | Architektur-, Text-, Sidecar- und Sicherheitsverträge | bei Vertragsänderungen mitändern |

## Laufzeitarchitektur

### PWA-Pfad

```text
index.html
  ↓
app.js
  ├─ IndexedDB: entries / projects / files / settings / audioSessions / audioSegments / models
  ├─ MediaRecorder: Originalaudio + Recovery
  └─ services/*: Fähigkeiten, STT, Normalisierung, Native Bridge
```

Das Frontend besitzt derzeit **keinen npm-/Bundler-Zwang**. Es besteht aus statischen Dateien und wird für die PWA über einen lokalen HTTP-Server ausgeliefert.

### Native STT-Pfad

```text
LivePcmCapture
  ↓ 16 kHz / Mono / PCM16-WAV
Live-STT-Warteschlange
  ↓
native-bridge.js
  ↓ Tauri invoke
src-tauri/src/main.rs
  ↓
geschützter Modellpfad + private Temp-WAV
  ↓
Tauri-Sidecar naqya-whisper
  ↓ nur wenn Sidecar nicht verfügbar
kontrollierter externer whisper-cli-Fallback
```

## Kritische Invarianten

Diese Punkte sind keine Implementierungsdetails, sondern Sicherheits-/Datenverträge:

1. **Offline-first:** Keine automatische Online-STT, Cloudpflicht oder Telemetrie einführen.
2. **Originalaudio und STT sind getrennt:** 3-Sekunden-Recoverysegmente und 4-Sekunden-STT-Segmente dürfen nicht zu einem gemeinsamen Lebenszyklus verschmolzen werden.
3. **STT-Segmente bleiben geordnet:** `services/live-stt.js` serialisiert Transkriptionen absichtlich über eine Promise-Kette. Parallelisierung kann Textreihenfolge und Messwerte verfälschen.
4. **Modelle werden nicht direkt aus beliebigen Benutzerpfaden ausgeführt:** Browser-Blob → 4-MiB-IPC-Blöcke → `.incoming` → SHA-256 → atomare Aktivierung → kanonisierter Pfad im NAQYA-Modellbereich.
5. **Native Modellpfade sind eine Vertrauensgrenze:** `trusted_model_path()` muss Pfade kanonisieren und auf den eigenen Modell-Root begrenzen.
6. **Sidecar vor PATH:** Der gebündelte Sidecar ist primär. Ein gestarteter Sidecar mit Laufzeitfehler darf nicht still durch einen externen CLI-Fallback ersetzt werden.
7. **Temp-Audio bleibt privat:** Tauri-App-Cache, exklusive Dateierzeugung, `sync_all()` vor Prozessübergabe, anschließende Bereinigung.
8. **Supply Chain ist gepinnt:** whisper.cpp-Tag **und** Commit müssen zum Runtimevertrag passen. Keine `latest`-Downloads.
9. **Produktversion ≠ Datenbankschema:** Produktversion und `DB_VERSION` dürfen nicht gekoppelt hochgezählt werden. `DB_VERSION` ändert sich nur bei IndexedDB-Migrationen.
10. **Releasebehauptungen brauchen Nachweis:** Erfolgreicher Sidecar-Build oder `cargo check` ist noch kein getestetes Endanwender-Bundle.

## Code-Kommentare

Kommentare werden bewusst sparsam eingesetzt. Ein Kommentar ist sinnvoll, wenn ein späterer Entwickler sonst eine scheinbar unnötige Einschränkung „optimieren“ könnte.

Regel:

- **kommentieren:** Sicherheitsgrenzen, Reihenfolgeabhängigkeiten, Migrationsregeln, ungewöhnliche Fallbackentscheidungen, Supply-Chain-Pins
- **nicht kommentieren:** offensichtliche Zuweisungen, normale Schleifen, selbstsprechende Funktionsnamen
- bevorzugtes Muster: `ENTWICKLERHINWEIS: <warum diese Invariante existiert>`

Lange Erklärungen gehören in diese Datei oder einen spezialisierten Vertrag unter `docs/`, nicht mehrfach in den Quellcode.

## Datenmodell und Migrationen

Aktuell gilt IndexedDB-Schema **V2**. Details stehen in `docs/DATENMODELL.md`.

Bei einer Schemaänderung:

1. `DB_VERSION` erhöhen.
2. Migration ausschließlich additiv oder explizit verlustfrei implementieren.
3. bestehende Stores nicht still löschen.
4. `docs/DATENMODELL.md` aktualisieren.
5. Backup-/Importpfad auf Kompatibilität prüfen.
6. statischen Vertrag ergänzen.

Produktversionsänderungen allein sind **kein** Grund, `DB_VERSION` zu erhöhen.

## Lokale PWA-Entwicklung

Schnellstart:

```bash
python3 -m http.server 8765 --bind 127.0.0.1
```

Dann `http://127.0.0.1:8765` öffnen.

Alternativ:

```bash
chmod +x START_NAQYA.sh
./START_NAQYA.sh
```

Für UI-/PWA-Arbeit sind keine npm-Abhängigkeiten erforderlich.

## Lokale Qualitätsprüfung

### Schnelle Prüfung nach kleinen Frontendänderungen

```bash
python3 tests/validate_text_integrity.py
node --check app.js
node --check sw.js
node --check services/capabilities.js
node --check services/native-bridge.js
node --check services/stt-core.js
node --check services/audio-normalizer.js
node --check services/live-stt.js
node --check services/release-04.js
python3 tests/validate_static.py
```

### Rust/Tauri-Prüfung

```bash
cargo fmt --manifest-path src-tauri/Cargo.toml -- --check
cargo check --manifest-path src-tauri/Cargo.toml
```

Unter Ubuntu/Kubuntu benötigt Tauri mindestens die im CI verwendeten Entwicklungsbibliotheken:

```bash
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
  libwebkit2gtk-4.1-dev libxdo-dev libssl-dev \
  libayatana-appindicator3-dev librsvg2-dev cmake build-essential
```

### Sidecar-Vertrag

Der echte Build greift ausschließlich auf den fest gepinnten Upstream zu:

```bash
bash tools/build_whisper_sidecar.sh
python3 tests/validate_sidecar.py
```

Danach unter Linux zusätzlich sinnvoll:

```bash
sha256sum src-tauri/binaries/naqya-whisper-x86_64-unknown-linux-gnu
ldd src-tauri/binaries/naqya-whisper-x86_64-unknown-linux-gnu
```

`ldd` ist für den nächsten Bundle-Schritt wichtig: Das bisherige CI beweist Build und Hash des kopierten Executables, aber noch nicht die vollständige Laufzeitabhängigkeits-Schließung eines Endanwenderpakets.

### Shell-Syntax

```bash
bash -n START_NAQYA.sh
bash -n tools/build_whisper_sidecar.sh
```

## Entwicklungs- und Mergeablauf

1. Realen `main`-, PR- und CI-Stand prüfen.
2. Fachlich kleinen Zweig vom aktuellen `main` erstellen.
3. Nur die für das Ziel notwendigen Dateien ändern.
4. Relevante lokale Prüfungen ausführen.
5. README, TODO, CHANGELOG, Entwicklerdokumentation und maschinenlesbare Statusdateien auf Aktualisierungsbedarf prüfen.
6. Pull Request zunächst als Entwurf öffnen.
7. Qualitätsgate für den **exakten Head-SHA** vollständig grün abwarten.
8. Erst danach Review-/Mergebereitschaft setzen.
9. Bevorzugt Squash-Merge mit erwarteter Head-SHA.
10. Den resultierenden `main` erneut lesen und zentrale Text-/Statusdateien gegenprüfen.

## Nächster Arbeitsblock 0.5.1

**Ziel:** Linux-Desktop-Bundle end-to-end erzeugen und nachweisen; anschließend Release-Nachweis und Windows-Sidecar.

### Aktueller Übergabepunkt

`src-tauri/tauri.conf.json` verwendet derzeit:

```json
"frontendDist": ".."
```

Das ist für eine reproduzierbare Release-Pipeline zu breit: Der Repository-Stamm ist kein deterministisch gestagtes Frontend-Artefakt.

### Empfohlene minimale Umsetzung

1. Ein deterministisches Desktop-Frontend-Staging einführen, das nur benötigte Runtime-Dateien in z. B. `dist/` kopiert.
2. `frontendDist` auf dieses Staging-Verzeichnis umstellen.
3. Staging selbst testen: keine `.git`, Tests, Dokumentation, Modelle oder Buildreste im Desktop-Frontend.
4. Linux-Sidecar wie bisher aus dem gepinnten Upstream bauen.
5. vollständiges Tauri-Linux-Bundle erzeugen.
6. Paketinhalt auf `naqya-whisper` und notwendige Laufzeitbibliotheken prüfen.
7. den Sidecar **aus dem erzeugten Paketkontext** starten.
8. maschinenlesbaren Release-Nachweis erzeugen: NAQYA-Version, Plattform, Architektur, whisper.cpp-Tag/Commit, Dateinamen, Größen, SHA-256, Compiler-/Rust-/Tauri-/CMake-Versionen und CI-Run.
9. erst nach erfolgreicher Prüfung `sidecar_release_bundle_validated` auf wahr setzen.

### Erwartete Touchpoints

So klein wie möglich halten:

- `src-tauri/tauri.conf.json`
- ein neues, kleines Frontend-Staging-Skript unter `tools/`
- `.gitignore` für erzeugtes `dist/`
- `.github/workflows/validate.yml`
- ein Bundle-/Release-Nachweistest unter `tests/`
- README/TODO/CHANGELOG/Statusdateien nur entsprechend real erreichtem Stand

Nicht gleichzeitig `app.js` refaktorieren oder `AudioWorklet` einführen. Beides ist fachlich ein separater Entwicklungsblock.

## Typische Fehlerbilder

### Native Bridge nicht verfügbar

Prüfen, ob `window.__TAURI__` vorhanden ist. Im normalen Browser ist die Native Bridge erwartungsgemäß nicht verfügbar.

### Sidecar nicht verfügbar

- `tools/build_whisper_sidecar.sh` ausführen.
- Zielname gegen `src-tauri/sidecar/whisper-runtime.json` prüfen.
- Tauri-`externalBin` prüfen.
- nicht durch eine generische PATH-Suche „reparieren“.

### Modell wird abgelehnt

Das Modell muss durch `materializeModel()` in den geschützten nativen Modellpfad übertragen worden sein. Ein beliebiger lokaler Dateipfad ist absichtlich ungültig.

### Live-Text ist verspätet

Echtzeitfaktor und Segmentzeiten prüfen. Nicht als erste Maßnahme mehrere Segmente parallel transkribieren; Reihenfolge und Zustandsupdates sind derzeit seriell ausgelegt.

### Textintegritätstest schlägt fehl

Zuerst auf Merge-Verklebung, doppelte H2-Abschnitte oder doppelte JSON-Schlüssel prüfen. Tests nicht lockern, solange der Vertrag fachlich korrekt ist.

## Dokumentationsmatrix

| Änderung | Mindestens prüfen |
|---|---|
| UI/Bedienung | README, LAIENANLEITUNG, Service-Worker, UI-Tests |
| IndexedDB/Backup | `docs/DATENMODELL.md`, `app.js`, Backup-Kompatibilität, Tests |
| Audio | Architektur, Audio-Dokumente, Recovery- und Live-STT-Verträge |
| STT/Modelle | STT-Core, Native Bridge, Rust, Sidecar-Doku, Sicherheitsprüfungen |
| Sidecar/Supply Chain | Runtime-Manifest, Buildscript, CI, Sidecar-Test, README |
| Tauri/Bundle | Tauri-Konfiguration, CI, Release-Nachweis, README/TODO/Status |
| Versionsstand | `VERSION.json`, `PROJEKTSTATUS.json`, Tauri-Version, `app.js`, Service-Worker, README/CHANGELOG |

## Definition of Done

Eine Iteration ist technisch fertig, wenn:

- Ziel und Abnahmekriterien erfüllt sind,
- keine unbeabsichtigte Architektur- oder Sicherheitsaufweichung erfolgt ist,
- relevante lokale Tests grün sind,
- CI für den exakten PR-Head grün ist,
- Dokumentation nur tatsächlich erreichten Stand behauptet,
- Merge nachvollziehbar erfolgt,
- resultierender `main` erneut geprüft ist.

Hardware- oder Releasefähigkeit darf nur behauptet werden, wenn die entsprechende reale Prüfung tatsächlich durchgeführt wurde.
