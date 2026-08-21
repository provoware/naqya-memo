# Entwicklerdokumentation – NAQYA Memo Tool 2026

> **Dokumentenstatus:** Kanonischer technischer Einstieg für 0.5.1-D. Vor jeder Änderung realen GitHub-`main`-, PR- und CI-Stand prüfen.

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

Produktversion **0.5.0**, Entwicklungsstand **0.5.1-D**, Fortschritt **89 % / 8 von 9**.

Validiert sind Offline-PWA, Audio-Recovery, 16-kHz-Mono-WAV, segmentiertes Live-STT, geschützter Modellpfad, Tauri-Sidecar, deterministisches `dist/`, Linux-DEB, Windows-NSIS, Sidecar-Start aus beiden Paketkontexten, Release Evidence, Diagnosemodul, automatischer Linux-/Windows-Evidence-Vergleich und der plattformübergreifende Evidence-Fingerprint.

Tauri verwendet `frontendDist: "../dist"`.

Aktuell validierter Evidence-Fingerprint:

```text
018452a4b7683cba40dbce2a2c221aa6b31e55c846470baef35e4baa13081aaf
```

Noch offen sind reale Linux-/Windows-Hardware- und Mikrofonabnahme, 30-/60-Minuten-Langzeittests sowie anschließend der kontrollierte Ersatz von `ScriptProcessor` durch `AudioWorklet`.

## Repository-Landkarte

| Pfad | Verantwortung |
|---|---|
| `app.js` | PWA, IndexedDB, Backup, Audio-Recovery |
| `services/diagnostics.js` | Diagnosepuffer, Redaction, Export, Safe Actions |
| `diagnostics/DIAGNOSTICS_CONTRACT.json` | kanonische Fehlercodes und Diagnosevertrag |
| `services/native-bridge.js` | JavaScript↔Tauri und Modelltransfer |
| `services/live-stt.js` | segmentierte Live-Transkription |
| `services/audio-normalizer.js` | 16-kHz-/Mono-/WAV-Vertrag; derzeit `ScriptProcessor` |
| `src-tauri/src/main.rs` | native Sicherheits- und Runtimegrenzen |
| `src-tauri/tauri.conf.json` | Desktop-/Bundle-Konfiguration |
| `src-tauri/sidecar/whisper-runtime.json` | whisper.cpp-Supply-Chain-Vertrag |
| `tools/stage_desktop_frontend.py` | deterministisches Desktop-Frontend |
| `tools/generate_release_evidence.py` | plattformbezogene Release Evidence + gemeinsamer Fingerprint |
| `.github/workflows/validate.yml` | allgemeines Qualitätsgate |
| `.github/workflows/platform-bundle.yml` | gemeinsamer Linux-/Windows-Bundle- und Evidence-Paarlauf |
| `tests/compare_release_evidence.py` | Linux-/Windows-Evidence-Vergleich |
| `tests/validate_evidence_fingerprint.py` | plattformneutraler Fingerprint-Vertrag |
| `tests/validate_text_integrity.py` | Text-, Merge- und Statuskonsistenz |

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
10. Linux und Windows verwenden denselben Diagnosevertrag.
11. Plattformübergreifende Software-/Diagnosegleichheit wird über den Evidence-Fingerprint bestimmt; Paket- und Sidecar-Binärhashes dürfen plattformbedingt verschieden sein.
12. CI-Paketabnahme ist keine reale Hardwarefreigabe.

Aktuell validierter Diagnosevertrag:

```text
Schema: 1
Ereignisschema: 1
Format: NAQYA-DIAGNOSTICS
SHA-256: fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425
```

## Hardware-Abnahme 0.5.1-E

Vor einer Hardwarefreigabe wird ein maschinenlesbarer Abnahmevertrag eingeführt. Er bindet jede reale Messung an den Evidence-Fingerprint und dokumentiert mindestens Plattform, OS-Version, CPU/RAM, Mikrofon, Paketbezug, Modell-SHA, Testdauer, Segmentzahl, Echtzeitfaktor, relevante Fehlercodes und Ergebnis.

Wichtig: Die aktuelle `ScriptProcessor`-Implementierung bleibt zunächst als Baseline bestehen. Erst nachdem reale Linux-/Windows-Messwerte vorliegen, wird `AudioWorklet` implementiert und gegen dieselbe Messbasis verglichen. Damit werden zwei große Variablen nicht gleichzeitig verändert.

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
python3 tests/validate_platform_diagnostics.py
python3 tests/validate_evidence_fingerprint.py
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

**0.5.1-E – Reale Hardwareabnahme, AudioWorklet & Langzeithärtung**

Minimale Reihenfolge:

1. Hardware-Abnahmevertrag und Validator an den Evidence-Fingerprint binden.
2. reale Linux-/Windows-Baseline mit Paket, Mikrofon, Modell und Live-Diktat erfassen.
3. 30-/60-Minuten-Lastmessungen mit CPU, RAM, Segmentverlust und Echtzeitfaktor dokumentieren.
4. danach `AudioWorklet` implementieren.
5. neue Implementierung gegen dieselbe Baseline regressionsprüfen.

Nicht gleichzeitig größere UI-, Datenmodell- oder Runtime-Refactorings einführen.

## Definition of Done

Eine Iteration ist erst fertig, wenn Code, Dokumentation, Repository, PR und CI denselben Stand beschreiben; relevante Gates grün sind; Releaseänderungen Evidence besitzen; README/TODO/AGENTS/CHANGELOG/`PROJEKTSTATUS.json` geprüft sind und der resultierende `main` nach Merge erneut validiert wurde.