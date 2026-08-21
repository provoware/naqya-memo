# Entwicklerdokumentation – NAQYA Memo Tool 2026

> **Dokumentenstatus:** Kanonischer technischer Einstieg für 0.5.1-C. Vor jeder Änderung realen GitHub-`main`-, PR- und CI-Stand prüfen.

## Ziel

Ein fremder Entwickler soll ohne Vorwissen sicher weiterarbeiten können, ohne Offline-, Daten-, Audio-, Sidecar-, Diagnose- oder Release-Verträge zu brechen.

## Schnellübernahme

1. `README.md` – aktueller Status und Fortschritt.
2. `AGENTS.md` – verbindliche Entwicklungs- und Mergeverträge.
3. `TODO.md` – Restarbeiten und Abnahmekriterien.
4. `docs/ARCHITEKTUR.md` – Systemübersicht.
5. `docs/WHISPER_SIDECAR.md` – Sidecar-/Supply-Chain-Vertrag.
6. `docs/DIAGNOSE_LOGGING.md` – Diagnose-/Evidence-Vertrag.

Vor Änderungen:

```bash
git status
git branch --show-current
git rev-parse HEAD
```

## Aktueller technischer Stand

Produktversion **0.5.0**, Entwicklungsstand **0.5.1-C**, Fortschritt **78 % / 7 von 9**.

Validiert sind Offline-PWA, Audio-Recovery, 16-kHz-Mono-WAV, segmentiertes Live-STT, geschützter Modellpfad, Tauri-Sidecar, deterministisches `dist/`, Linux-DEB, deterministisches DEB-Repacking, Release Evidence und das professionelle Diagnosemodul mit SHA-256-Bindung an Release Evidence.

Tauri verwendet `frontendDist: "../dist"`.

Noch offen sind Windows-Paketnachweis, reale Linux-/Windows-Hardwareabnahme, AudioWorklet und Langzeittests.

## Repository-Landkarte

| Pfad | Verantwortung |
|---|---|
| `app.js` | PWA, IndexedDB, Backup, Audio-Recovery |
| `services/diagnostics.js` | Diagnosepuffer, Redaction, Export, Safe Actions |
| `diagnostics/DIAGNOSTICS_CONTRACT.json` | kanonische Fehlercodes und Diagnosevertrag |
| `services/native-bridge.js` | JavaScript↔Tauri und Modelltransfer |
| `services/live-stt.js` | segmentierte Live-Transkription |
| `services/audio-normalizer.js` | 16-kHz-/Mono-/WAV-Vertrag |
| `src-tauri/src/main.rs` | native Sicherheits- und Runtimegrenzen |
| `src-tauri/tauri.conf.json` | Desktop-/Bundle-Konfiguration |
| `src-tauri/sidecar/whisper-runtime.json` | whisper.cpp-Supply-Chain-Vertrag |
| `tools/stage_desktop_frontend.py` | deterministisches Desktop-Frontend |
| `tools/generate_release_evidence.py` | Release Evidence |
| `.github/workflows/validate.yml` | allgemeines Qualitätsgate |
| `.github/workflows/bundle-linux.yml` | Linux-Paketnachweis |
| `tests/diagnostics_runtime.test.js` | Diagnose-Laufzeitregression |
| `tests/validate_diagnostics.py` | Diagnose-/Evidence-Statikvertrag |

## Kritische Invarianten

1. Offline-first: keine automatische Cloud-STT oder Telemetrie.
2. 3-s-Audio-Recovery und 4-s-STT-Segmente bleiben getrennt.
3. STT-Segmente bleiben seriell geordnet.
4. Modelle nur über geschützte Materialisierung und SHA-256 aktivieren.
5. Sidecar vor PATH-Fallback; kein stiller Ersatz eines gestarteten, fehlernden Sidecars.
6. whisper.cpp-Tag und Commit bleiben gepinnt.
7. **Produktversion ≠ Datenbankschema**; `DB_VERSION` nur bei IndexedDB-Migrationen ändern.
8. Releasebehauptungen benötigen Paket-Evidence.
9. Diagnosecodes werden nicht umgedeutet.
10. Linux und Windows verwenden in 0.5.1-D denselben Diagnosevertrag.

Aktuell validierter Diagnosevertrag:

```text
Schema: 1
Ereignisschema: 1
Format: NAQYA-DIAGNOSTICS
SHA-256: fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425
```

## Code-Kommentare

Kommentare bleiben sparsam. `ENTWICKLERHINWEIS` erklärt nur nicht offensichtliche Sicherheits-, Reihenfolge-, Migrations- oder Supply-Chain-Gründe.

## Lokale Qualitätsprüfung

```bash
python3 tests/validate_text_integrity.py
node --check app.js
node --check sw.js
node --check services/diagnostics.js
node --check services/native-bridge.js
node --check services/live-stt.js
node tests/diagnostics_runtime.test.js
python3 tests/validate_diagnostics.py
python3 tools/stage_desktop_frontend.py
python3 tests/validate_dist.py
python3 tests/validate_static.py
cargo fmt --manifest-path src-tauri/Cargo.toml -- --check
cargo check --manifest-path src-tauri/Cargo.toml
bash -n START_NAQYA.sh
bash -n tools/build_whisper_sidecar.sh
bash -n tools/repack_deb_deterministic.sh
```

## Entwicklungs- und Mergeablauf

1. realen `main`-, PR- und CI-Stand prüfen.
2. kleinen Branch vom aktuellen `main` erstellen.
3. nur notwendige Dateien ändern.
4. lokale Prüfungen ausführen.
5. README, TODO, AGENTS, CHANGELOG und Statusdateien prüfen.
6. Draft-PR öffnen.
7. exakten Head vollständig grün abwarten.
8. Ready setzen und mit `expected_head_sha` squash-mergen.
9. resultierenden `main` erneut prüfen.

## Nächster Arbeitsblock 0.5.1

**0.5.1-D – Windows-x86_64-Bundle & plattformübergreifender Evidence-Nachweis**

Nicht verhandelbare Plattforminvariante: `diagnostics/DIAGNOSTICS_CONTRACT.json` bleibt unverändert. Das Windows-Gate prüft SHA-256 `fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425`. Damit bedeutet beispielsweise `NAQYA-STT-4002` auf Linux und Windows dasselbe.

Minimale Umsetzung:

1. Windows-Build für `x86_64-pc-windows-msvc`.
2. Contract-SHA vor Build hart prüfen.
3. whisper.cpp aus demselben Tag/Commit bauen.
4. Tauri-Windows-Paket erzeugen.
5. Sidecar aus Paketkontext starten.
6. Paket-/Sidecar-SHA und Toolchain in Windows Evidence aufnehmen.
7. Linux-/Windows-Evidence auf identische Diagnosebindung vergleichen.

Nicht gleichzeitig AudioWorklet oder größere UI-Refactorings einführen.

## Definition of Done

Eine Iteration ist erst fertig, wenn Code, Dokumentation, Repository, PR und CI denselben Stand beschreiben; relevante Gates grün sind; Releaseänderungen Evidence besitzen; README/TODO/AGENTS/CHANGELOG/`PROJEKTSTATUS.json` geprüft sind und der resultierende `main` nach Merge erneut validiert wurde.
