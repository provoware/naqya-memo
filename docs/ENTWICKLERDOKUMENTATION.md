# Entwicklerdokumentation – NAQYA Memo Tool 2026

> **Dokumentenstatus:** Kanonischer technischer Einstieg für den aktuellen 0.5.0-/0.5.1-Entwicklungsstand. Vor jeder Iteration realen `main`-, PR- und CI-Stand prüfen.

## Ziel dieser Dokumentation

Ein fremder Entwickler soll ohne Vorwissen sicher weiterarbeiten können, ohne Offline-, Datenintegritäts-, Audio-, Modell-, Sidecar- oder Releaseverträge zu brechen. Detailverträge bleiben in den spezialisierten Dateien unter `docs/`.

## Schnellübernahme

In dieser Reihenfolge lesen:

1. `README.md` – Produkt- und Freigabestand.
2. `AGENTS.md` – verbindliche Entwicklungs-, Merge- und Freigaberegeln.
3. `TODO.md` – priorisierte Restarbeiten und Abnahmekriterien.
4. diese Datei – technische Orientierung und lokale Prüfungen.
5. `docs/ARCHITEKTUR.md` – Systemebenen und Datenflüsse.
6. bei Runtime-/STT-Arbeit zusätzlich `docs/WHISPER_SIDECAR.md` und `docs/DATENMODELL.md`.

Vor Änderungen:

```bash
git status
git branch --show-current
git rev-parse HEAD
```

Danach auf GitHub offenen PR-, CI- und Mergezustand gegenprüfen.

## Aktueller technischer Stand

Produktversion: **0.5.0**. Validiert sind PWA/IndexedDB, Audio-Recovery, lokale 16-kHz-WAV-Normalisierung, segmentiertes Live-STT, geschützter Modelltransfer, Tauri-Bridge, gepinnter whisper.cpp-Sidecar-Build sowie Text-, JavaScript-, Rust-, Shell-, Sidecar- und Frontend-Staging-Verträge.

Für 0.5.1 ist das Desktop-Frontend-Staging umgesetzt: `tools/stage_desktop_frontend.py` erzeugt ein frisches `dist/` aus exakt 14 erlaubten Runtime-Dateien und schreibt `NAQYA_FRONTEND_MANIFEST.json` mit Größe und SHA-256 je Datei. Ein vollständiges Endanwender-Linux-Bundle ist damit **noch nicht** abgenommen.

Bekannte Restinkonsistenz: `app.js` führt noch Produktversion 0.2.0. Das ist getrennt von `DB_VERSION=2`, dem korrekten IndexedDB-Schema.

## Repository-Landkarte

| Pfad | Verantwortung |
|---|---|
| `index.html`, `styles*.css` | UI-Struktur, Lesbarkeit, Modulreihenfolge |
| `app.js` | PWA-Controller, IndexedDB, Audio-Recovery, Backup, Rendering |
| `services/capabilities.js` | lokale Fähigkeitenerkennung |
| `services/native-bridge.js` | JavaScript↔Tauri-IPC und Modelltransfer |
| `services/stt-core.js` | STT-Providervertrag und Modellprofile |
| `services/audio-normalizer.js` | 16-kHz-Mono-/WAV-Vertrag |
| `services/live-stt.js` | geordnete segmentierte Live-Transkription |
| `sw.js` | Offline-Cache; bei Runtime-Dateiänderungen synchron halten |
| `tools/stage_desktop_frontend.py` | Desktop-Runtime-Allowlist, `dist/`, Frontend-Manifest |
| `tests/validate_frontend_staging.py` | Dateisatz-, Hash- und Tauri-Staging-Vertrag |
| `src-tauri/src/main.rs` | native Vertrauensgrenzen, Modellpfad, Temp-WAV, Sidecar/Fallback |
| `src-tauri/tauri.conf.json` | Tauri-Build und Bundle-Konfiguration |
| `src-tauri/sidecar/whisper-runtime.json` | Sidecar-Supply-Chain-/Zielplattformvertrag |
| `tools/build_whisper_sidecar.sh` | reproduzierbarer whisper.cpp-Build |
| `.github/workflows/validate.yml` | kanonisches Qualitätsgate |

## Laufzeit- und Buildpfade

PWA:

```text
index.html → app.js/services/* → IndexedDB / MediaRecorder / lokale STT
```

Desktop:

```text
Runtime-Allowlist
  ↓ tools/stage_desktop_frontend.py
 dist/ + NAQYA_FRONTEND_MANIFEST.json
  ↓ Tauri beforeBuildCommand / frontendDist
 Desktop-Paket
```

Tauri verwendet bewusst:

```json
"frontendDist": "../dist"
```

Der Repository-Stamm darf nicht wieder als Frontendquelle dienen. `dist/` ist generiert, steht in `.gitignore` und wird nie manuell gepflegt.

Native STT:

```text
LivePcmCapture → 16 kHz Mono WAV → Live-STT-Warteschlange
→ native-bridge.js → Tauri invoke → geschützter Modellpfad
→ naqya-whisper Sidecar → nur bei Nichtverfügbarkeit kontrollierter whisper-cli-Fallback
```

## Kritische Invarianten

1. **Offline-first:** keine automatische Online-STT, Cloudpflicht oder Telemetrie.
2. **Originalaudio ≠ STT-Segmente:** 3-Sekunden-Recovery und 4-Sekunden-STT getrennt halten.
3. **STT-Reihenfolge:** Promise-Kette in `live-stt.js` nicht leichtfertig parallelisieren.
4. **Modell-Vertrauensgrenze:** Blob → 4-MiB-Blöcke → `.incoming` → SHA-256 → atomare Aktivierung → kanonisierter NAQYA-Modellpfad.
5. **Sidecar vor PATH:** gestarteten Sidecar mit Laufzeitfehler nicht still durch externen CLI ersetzen.
6. **Temp-Audio privat:** Tauri-App-Cache, exklusive Erzeugung, `sync_all()`, danach Bereinigung.
7. **Supply Chain gepinnt:** whisper.cpp-Tag und Commit müssen übereinstimmen; keine `latest`-Downloads.
8. **Desktop-Frontend ist Allowlist:** neue Runtime-Dateien bewusst in Staging, Service Worker und Test aufnehmen.
9. **Produktversion ≠ Datenbankschema:** `DB_VERSION` nur bei IndexedDB-Migrationen ändern.
10. **Releasebehauptung nur mit Nachweis:** Sidecar-Build, Staging und `cargo check` sind noch kein getestetes Endanwender-Bundle.

## Code-Kommentare

Kommentare bleiben sparsam. Direkt im Code nur nicht offensichtliche Sicherheits-, Reihenfolge-, Migrations- oder Supply-Chain-Invarianten erklären. Bevorzugtes Muster:

```text
ENTWICKLERHINWEIS: <warum diese Einschränkung existiert>
```

Normale Kontrollflüsse und selbsterklärende Zuweisungen nicht kommentieren; längere Begründungen gehören in `docs/`.

## Datenmodell und Migrationen

Aktuell gilt IndexedDB-Schema **V2**. Bei Schemaänderungen `DB_VERSION` erhöhen, verlustfreie Migration implementieren, `docs/DATENMODELL.md` nachziehen und Backup/Import prüfen. Produktversionsänderungen allein sind kein Migrationsgrund.

## Lokale Entwicklung

PWA:

```bash
python3 -m http.server 8765 --bind 127.0.0.1
```

oder:

```bash
chmod +x START_NAQYA.sh
./START_NAQYA.sh
```

Kein npm-/Bundler-Zwang für die statische PWA.

## Lokale Qualitätsprüfung

Kleine Frontend-/Dokumentationsänderung:

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
python3 tests/validate_frontend_staging.py
python3 tests/validate_static.py
```

Desktop-Staging gezielt:

```bash
python3 tools/stage_desktop_frontend.py
python3 tests/validate_frontend_staging.py
```

Erwartung: exakt 14 Runtime-Dateien plus `NAQYA_FRONTEND_MANIFEST.json`.

Rust/Tauri:

```bash
cargo fmt --manifest-path src-tauri/Cargo.toml -- --check
cargo check --manifest-path src-tauri/Cargo.toml
```

Sidecar:

```bash
bash tools/build_whisper_sidecar.sh
python3 tests/validate_sidecar.py
sha256sum src-tauri/binaries/naqya-whisper-x86_64-unknown-linux-gnu
ldd src-tauri/binaries/naqya-whisper-x86_64-unknown-linux-gnu
```

Shell:

```bash
bash -n START_NAQYA.sh
bash -n tools/build_whisper_sidecar.sh
```

## Entwicklungs- und Mergeablauf

1. realen `main`-, PR- und CI-Stand prüfen.
2. kleinen Fachzweig vom aktuellen `main` erstellen.
3. nur notwendige Dateien ändern.
4. relevante lokale Prüfungen ausführen.
5. README, TODO, CHANGELOG, Entwicklerdoku und Statusdateien auf Drift prüfen.
6. PR zunächst als Entwurf öffnen.
7. Qualitätsgate für den exakten Head-SHA vollständig grün abwarten.
8. Reviewbereitschaft erst danach setzen.
9. bevorzugt Squash-Merge mit erwarteter Head-SHA.
10. resultierenden `main` erneut validieren.

## Nächster Arbeitsblock 0.5.1

**Ziel:** Linux-Desktop-Bundle end-to-end erzeugen und nachweisen; danach Release-Nachweis und Windows-Sidecar.

Aktueller Übergabepunkt: Das deterministische `dist/`-Staging ist umgesetzt. Nächste Schritte:

1. separate PWA-Produktversionsdrift `app.js` 0.2.0 → 0.5.0 schließen, `DB_VERSION=2` unverändert lassen.
2. vollständiges Tauri-Linux-Bundle aus dem deterministischen `dist/` erzeugen.
3. Paketinhalt auf Frontend-Manifest, `naqya-whisper` und Laufzeitbibliotheken prüfen.
4. Sidecar aus dem Paketkontext tatsächlich starten.
5. maschinenlesbaren Release-Nachweis mit Plattform, Architektur, whisper.cpp-Tag/Commit, Dateinamen, Größen, SHA-256 sowie Toolchain-/CI-Zuordnung erzeugen.
6. erst nach End-to-End-Nachweis `sidecar_release_bundle_validated` auf wahr setzen.

## Definition of Done

Eine Änderung ist erst fertig, wenn Code und Dokumentation denselben realen Stand beschreiben, die betroffenen lokalen Prüfungen bestanden sind, das GitHub-Qualitätsgate für den **exakten PR-Head** vollständig grün ist und nach einem Merge der resultierende `main` erneut geprüft wurde. Build-, Bundle- oder Releasefähigkeit darf nur behauptet werden, wenn genau diese Stufe praktisch nachgewiesen wurde.
