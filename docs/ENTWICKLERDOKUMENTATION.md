# Entwicklerdokumentation – NAQYA Memo Tool 2026

> **Dokumentenstatus:** Kanonischer technischer Einstieg für den CI-validierten Stand 0.5.1-C. Produktversion bleibt 0.5.0.

## Ziel dieser Dokumentation

Ein fremder Entwickler soll NAQYA übernehmen können, ohne Offline-, Datenintegritäts-, Audio-, Modell-, Sidecar-, Diagnose- oder Release-Evidence-Verträge unbeabsichtigt zu brechen.

## Schnellübernahme

In dieser Reihenfolge lesen:

1. `README.md`
2. `AGENTS.md`
3. `TODO.md`
4. diese Datei
5. `docs/ARCHITEKTUR.md`
6. `docs/WHISPER_SIDECAR.md`
7. `docs/DIAGNOSE_LOGGING.md`
8. `PROJEKTSTATUS.json`

Vor Änderungen immer real prüfen:

```bash
git status
git branch --show-current
git rev-parse HEAD
```

Danach PR-, CI- und `main`-Stand auf GitHub abgleichen.

## Aktueller technischer Stand

Produktversion: **0.5.0**  
Entwicklungsstand: **0.5.1-C – Diagnose, Logging & Evidence-Bindung**  
Fortschritt 0.5.1: **78 % – 7/9 Hauptpunkte**

Validiert:
- deterministisches Desktop-`dist/`; `frontendDist` zeigt auf `../dist`
- Linux-x86_64-Sidecar aus gepinntem whisper.cpp
- Linux-DEB, Paketkontext-Start und Laufzeitabhängigkeiten
- deterministisches DEB-Repacking
- Release Evidence
- fail-safe Diagnosemodul
- stabiler Fehlercode-/Ereignisvertrag
- Privacy-Redaction, Ringpuffer, Deduplizierung und Safe Actions
- Diagnoseexport JSON/TXT
- Diagnosevertrag per SHA-256 an Release Evidence gebunden

Noch nicht als Hardware-Release abgenommen:
- Windows-Bundle
- reale Linux-/Windows-Mikrofon- und Hardwaretests
- 30-/60-Minuten-Langzeittests
- AudioWorklet-Migration

## Repository-Landkarte

| Pfad | Verantwortung | Wichtige Folgeprüfung |
|---|---|---|
| `app.js` | PWA-Controller, IndexedDB, Audio-Recovery, Backup | Daten-/Backup-Vertrag |
| `services/diagnostics.js` | fail-safe Runtime-Diagnose | Diagnose-Laufzeittests |
| `diagnostics/DIAGNOSTICS_CONTRACT.json` | kanonischer Diagnosevertrag | Contract-SHA und Schema |
| `services/native-bridge.js` | JS↔Tauri-IPC, Modelltransfer | Rust/Runtime/Diagnose |
| `services/live-stt.js` | segmentierte Live-STT-Warteschlange | Reihenfolge, Diagnosecodes |
| `src-tauri/src/main.rs` | native Sicherheits- und Runtimegrenzen | Rust, Sidecar, Tempdateien |
| `src-tauri/tauri.conf.json` | Desktop-Bundle | Bundle-Test |
| `src-tauri/sidecar/whisper-runtime.json` | Supply-Chain-/Plattformvertrag | Sidecar-Build |
| `release/RELEASE_EVIDENCE.schema.json` | Release-Nachweisschema | Evidence-Validator |
| `tools/stage_desktop_frontend.py` | deterministisches Runtime-Staging | `validate_dist.py` |
| `tools/build_whisper_sidecar.sh` | Linux-Sidecar-Build | Sidecar-SHA |
| `tests/validate_platform_diagnostics.py` | Plattform-Semantiksperre | bei Plattformarbeit zwingend |
| `.github/workflows/validate.yml` | kanonisches Qualitätsgate | bei Teständerungen synchron halten |

## Laufzeitarchitektur

```text
Mikrofon
  ↓
Originalaudio + 3-s-Recovery
  ↓
16 kHz / Mono / PCM16-WAV
  ↓
4-s-Live-STT-Warteschlange
  ↓
native-bridge.js
  ↓
Tauri / geschützter Modellpfad
  ↓
naqya-whisper Sidecar
  ↓
Transkript + bereinigte Diagnoseereignisse
```

## Kritische Invarianten

1. **Offline-first:** Keine automatische Cloud-STT oder Telemetrie einführen.
2. **Originalaudio ≠ STT-Segment:** 3-s-Recovery und 4-s-STT bleiben getrennte Lebenszyklen.
3. **Reihenfolge:** Live-STT bleibt seriell geordnet, solange keine explizit validierte Parallelstrategie existiert.
4. **Modellpfad:** Modelle werden nur nach Transfer, SHA-256 und atomarer Aktivierung aus dem eigenen App-Bereich genutzt.
5. **Sidecar vor PATH:** Ein gestarteter Sidecar mit Laufzeitfehler wird nicht still durch externen CLI-Fallback ersetzt.
6. **Supply Chain:** whisper.cpp bleibt auf `v1.9.2`, Commit `306c88f4d1286aec1bf96e544632897886af5501` gepinnt.
7. **Produktversion ≠ Datenbankschema:** `DB_VERSION` ändert sich nur bei IndexedDB-Migrationen.
8. **Releasebehauptung braucht Evidence:** Build-Erfolg ist keine Hardwareabnahme.
9. **Diagnosevertrag ist plattformübergreifend:** Linux und Windows verwenden bytegenau denselben Vertrag.
10. **Contract-SHA 0.5.1-C/D:** `fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425`.
11. **Fehlercodes sind semantisch stabil:** `NAQYA-STT-4002` bedeutet auf jeder Plattform „Live-STT-Segment konnte nicht transkribiert werden“.

## Code-Kommentare

Kommentare erklären nur nicht offensichtliche Architektur-, Sicherheits-, Reihenfolge- oder Supply-Chain-Gründe. Bevorzugter Marker:

```text
ENTWICKLERHINWEIS: <warum diese Invariante existiert>
```

Offensichtlicher Code wird nicht kommentierend nacherzählt.

## Datenmodell und Migrationen

IndexedDB-Schema bleibt **V2**. Produktversion **0.5.0** und Datenbankschema sind getrennt. Bei echten Schemaänderungen Migration verlustfrei planen, `DB_VERSION` erhöhen, `docs/DATENMODELL.md` und Backup-/Importvertrag gemeinsam prüfen.

## Lokale Qualitätsprüfung

Schnelle Vertragsprüfung:

```bash
python3 tests/validate_text_integrity.py
python3 tests/validate_diagnostics.py
python3 tests/validate_platform_diagnostics.py
node tests/diagnostics_runtime.test.js
python3 tools/stage_desktop_frontend.py
python3 tests/validate_dist.py
python3 tests/validate_release_evidence.py --schema-only
python3 tests/validate_static.py
python3 tests/validate_sidecar.py
```

JavaScript:

```bash
node --check app.js
node --check sw.js
node --check services/diagnostics.js
node --check services/native-bridge.js
node --check services/live-stt.js
```

Rust/Tauri:

```bash
cargo fmt --manifest-path src-tauri/Cargo.toml -- --check
cargo check --manifest-path src-tauri/Cargo.toml
```

## Entwicklungs- und Mergeablauf

1. realen `main`-, PR- und CI-Stand prüfen
2. kleinen Fachzweig vom aktuellen `main` erstellen
3. nur notwendige Dateien ändern
4. relevante lokale Prüfungen ausführen
5. README, TODO, AGENTS, CHANGELOG, Entwicklerdokumentation und `PROJEKTSTATUS.json` prüfen
6. PR zunächst als Draft öffnen
7. exakten Head-SHA vollständig validieren
8. erst dann Review-/Mergebereitschaft
9. bevorzugt Squash-Merge mit erwarteter Head-SHA
10. resultierenden `main` erneut prüfen

## Nächster Arbeitsblock 0.5.1

**0.5.1-D – Windows-Bundle mit identischem Diagnosevertrag**

Ziel ist nicht nur ein startbares Windows-Paket, sondern ein nachweislich vergleichbarer Plattformport.

Minimaler Umfang:
1. Windows-x86_64-Sidecar aus demselben whisper.cpp-Tag und Commit bauen.
2. Tauri-konformen `.exe`-Sidecar bundeln.
3. Paket- und Sidecar-SHA-256 erzeugen.
4. Sidecar aus dem erzeugten Paketkontext starten.
5. Windows Release Evidence erzeugen.
6. Diagnosevertrag vor und nach dem Windows-Build gegen SHA `fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425` prüfen.
7. Ereignisschema `1`, Format `NAQYA-DIAGNOSTICS` und Fehlercode-Semantik unverändert halten.
8. keine AudioWorklet-, UI- oder Datenmodellrefaktorisierung in denselben Block mischen.

## Typische Fehlerbilder

### Native Bridge nicht verfügbar
Im Browser erwartbar; in Tauri `window.__TAURI__` und Capability-Diagnose prüfen.

### Sidecar nicht verfügbar
Zielname, `externalBin`, Buildartefakt und Runtimequelle prüfen. Nicht durch generische PATH-Suche kaschieren.

### Diagnosevertrag driftet
`python3 tests/validate_platform_diagnostics.py` ausführen. Bei Plattformarbeit niemals den erwarteten SHA einfach aktualisieren; zuerst klären, warum der Vertrag verändert wurde.

### Textintegrität schlägt fehl
Merge-Verklebung, doppelte Überschriften, doppelte JSON-Schlüssel oder Statusdrift korrigieren; Test nicht lockern, solange der Vertrag fachlich stimmt.

## Definition of Done

Eine Iteration ist erst fertig, wenn:
- Code/Vertrag umgesetzt ist
- relevante Tests grün sind
- CI für den exakten Head grün ist
- README/TODO/AGENTS/Projektstatus nicht hinterherlaufen
- Release-/Bundle-Behauptungen durch Evidence belegt sind
- nach Merge der resultierende `main` erneut geprüft wurde
