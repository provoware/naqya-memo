# Mitentwickeln an NAQYA

Diese Datei ist der kurze GitHub-Einstieg. Die ausführliche technische Übergabe steht in `docs/ENTWICKLERDOKUMENTATION.md`.

## In 10 Minuten arbeitsfähig

1. `README.md` lesen: realer Produkt- und Freigabestand.
2. `docs/ENTWICKLERDOKUMENTATION.md` lesen: Architektur, lokale Befehle, Vertrauensgrenzen und aktueller Übergabepunkt.
3. `AGENTS.md` lesen: verbindlicher Entwicklungs-, Merge- und Freigabevertrag.
4. `TODO.md` lesen: priorisierte Restarbeiten und Entwickler-Übergabecheckliste.
5. Aktuellen `main`-Commit und CI-Stand auf GitHub prüfen; Chat- oder Dokumentationsangaben ersetzen diese Prüfung nicht.

## Arbeitsweise

- Nicht direkt auf `main` entwickeln. Kleine, fachlich geschlossene Zweige und Pull Requests verwenden.
- PR zunächst als Entwurf führen und erst nach vollständig grünem Qualitätsgate freigeben.
- Keine Cloudpflicht, Telemetrie oder ungeprüften Laufzeit-Downloads in den Offline-Kern einführen.
- Sicherheits- und Runtime-Fallbacks niemals still ändern. Sidecar, Modellpfad und Integritätsprüfungen sind Vertrauensgrenzen.
- Kommentare im Code sparsam halten. Kommentiert wird vor allem **warum** eine Invariante existiert; offensichtlicher Code wird nicht nacherzählt.
- Nutzerseitige Texte und Projektdokumentation bleiben deutsch. Technische API-/Bibliotheksnamen bleiben unverändert.

## Lokale Mindestprüfung

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
cargo fmt --manifest-path src-tauri/Cargo.toml -- --check
cargo check --manifest-path src-tauri/Cargo.toml
python3 tests/validate_static.py
python3 tests/validate_sidecar.py
bash -n START_NAQYA.sh
bash -n tools/build_whisper_sidecar.sh
```

Der reale Sidecar-Build benötigt zusätzlich die in `docs/ENTWICKLERDOKUMENTATION.md` beschriebenen Build-Abhängigkeiten und Netzwerkzugriff auf den **fest gepinnten** whisper.cpp-Upstream.

## Definition „fertig“

Eine Änderung ist erst fertig, wenn Code, Tests, README, TODO, Entwicklerdokumentation und maschinenlesbarer Projektstatus denselben realen Stand beschreiben und der resultierende `main` nach dem Merge erneut geprüft wurde.
