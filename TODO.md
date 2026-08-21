# TODO – NAQYA

Stand: 2026-08-21
Aktueller Entwicklungsstrang: `0.5.0-B – Tauri-Sidecar-Integration`
Aktueller PR: `#8`

## P0 – Freigabekritisch

### [in Arbeit] Repository- und Merge-Stand je Iteration prüfen
Komponente: Repository / Freigabe / CI

Abnahmekriterien:
- vor jeder Iteration aktuellen `main`-Commit prüfen
- aktuellen Arbeitszweig und Head-SHA prüfen
- zugehörigen PR-Status und Mergefähigkeit prüfen
- prüfen, ob der letzte freigegebene Stand tatsächlich nach `main` gemergt wurde
- CI für den exakten aktuellen Head-SHA prüfen
- nach jeder Iteration denselben Abgleich erneut durchführen
- nach Merge neuen `main`-Commit dokumentieren
- bei Abweichungen zuerst Repository-/PR-/CI-Synchronität herstellen

### [in Arbeit] Linux-Tauri-Sidecar vollständig validieren
Komponente: Tauri / whisper.cpp / Linux x86_64

Abnahmekriterien:
- reproduzierbarer Build aus dem fest gepinnten whisper.cpp-Commit erfolgreich
- erzeugtes Sidecar-Artefakt per SHA-256 geprüft
- `cargo fmt --check` erfolgreich
- `cargo check` mit `tauri-plugin-shell` und `externalBin` erfolgreich
- statische Verträge erfolgreich
- Shell-Syntaxprüfung erfolgreich
- exakter PR-Head vollständig grün

Aktueller Stand:
- realer Linux-Sidecar-Build: erfolgreich
- SHA-256-Artefaktprüfung: erfolgreich
- Rust-Formatprüfung: erfolgreich
- `cargo check`: erfolgreich im vorherigen vollständig geprüften Kandidaten
- nach Dokumentations-/Vertragsänderungen muss CI für den neuen exakten Head erneut vollständig grün sein

### [offen] PR #8 erst nach vollständigem Qualitätsgate promoten
Komponente: Freigabe

Abnahmekriterien:
- vollständiger CI-Erfolg für den aktuellen PR-Head
- PR aus Entwurfsstatus nehmen
- Squash-Merge mit erwarteter Head-SHA
- resultierenden `main`-Commit dokumentieren
- anschließend Repository- und Merge-Stand erneut prüfen

## P1 – Hohe Priorität

### [offen] Windows-x86_64-Sidecar reproduzierbar bauen
Komponente: whisper.cpp / Windows

Abnahmekriterien:
- Build aus identischem fest gepinnten Upstream-Commit
- zielkonformer Tauri-Binärname
- SHA-256-Nachweis
- Windows-Bundle kann den Sidecar tatsächlich starten

### [offen] Release-Manifest für konkrete Sidecar-Artefakte ergänzen
Komponente: Release / Integrität

Abnahmekriterien:
- Plattform
- Upstream-Commit
- Dateiname
- Dateigröße
- SHA-256
- Buildzeitpunkt bzw. Buildnachweis
- nachvollziehbare Zuordnung zum NAQYA-Release

### [offen] Reale Linux-Desktop-Abnahme durchführen
Komponente: Linux / Mikrofon / STT

Abnahmekriterien:
- Anwendung startet als Desktop-Bundle
- gebündelter Sidecar wird als bevorzugte Runtime erkannt
- echtes Sprachmodell aus geschütztem NAQYA-Modellpfad wird akzeptiert
- Mikrofonaufnahme und segmentiertes Live-Diktat funktionieren
- temporäre WAV-Dateien werden zuverlässig bereinigt
- Providerdiagnose zeigt `whisper.cpp-sidecar`

### [offen] Reale Windows-Desktop-Abnahme durchführen
Komponente: Windows / Mikrofon / STT

Abnahmekriterien analog zur Linux-Abnahme, zusätzlich Prüfung des `.exe`-Sidecars und des Windows-Bundles.

## P2 – Qualitätsausbau

### [offen] `ScriptProcessor` durch `AudioWorklet` ersetzen
Komponente: Web Audio / Live-STT

Abnahmekriterien:
- gleiche oder bessere 16-kHz-Mono-Normalisierung
- stabile Segmentbildung
- keine Regression bei Live-Diktat und Aufnahmewiederherstellung
- Firefox- und Chrome-Kompatibilität geprüft

### [offen] Langzeit- und Lasttests für Live-STT durchführen
Komponente: Performance / Stabilität

Abnahmekriterien:
- längere Diktatsitzungen ohne Speicherwachstum oder Segmentverlust
- CPU- und RAM-Verhalten dokumentiert
- Echtzeitfaktor für typische Modelle dokumentiert
- kontrolliertes Verhalten bei sehr langsamer Transkription

### [offen] Runtime-Diagnose in der Oberfläche deutlicher darstellen
Komponente: UI / Diagnose

Abnahmekriterien:
- gebündelter Sidecar / externer Fallback / nicht verfügbar klar unterscheidbar
- verwendeter Provider nach Transkription sichtbar
- laienverständliche Fehlermeldung mit konkretem nächsten Schritt

## P3 – Wartbarkeit und Dokumentation

### [offen] Versionsangaben für 0.5.x konsistent anheben
Komponente: Versionierung

Abnahmekriterien:
- `VERSION.json`
- `PROJEKTSTATUS.json`
- `src-tauri/Cargo.toml`
- `src-tauri/tauri.conf.json`
- Service-Worker-Cachebezeichner
- README und relevante Dokumentation

Hinweis: erst durchführen, wenn der genaue Freigabeumfang von 0.5.x feststeht.

### [offen] CHANGELOG für Sidecar-Entwicklungsstrang ergänzen
Komponente: Dokumentation

Abnahmekriterien:
- 0.5.0-Vertrag
- 0.5.0-B Tauri-Integration
- bekannte Einschränkungen
- tatsächliche Freigabegates

## Erledigt

### [erledigt] Reproduzierbaren whisper.cpp-Runtimevertrag festlegen
Ergebnis:
- Upstream auf `ggml-org/whisper.cpp` festgelegt
- Version/Commit fest gepinnt
- CPU-Releaseprofil mit `GGML_NATIVE=OFF`
- Linux-/Windows-Zielnamen definiert
- SHA-256-Erzeugung vorgesehen
- Laufzeit-Downloads und ungeprüfte Aktivierung ausgeschlossen

### [erledigt] Native Runtime-Sicherheit härten
Ergebnis:
- generische `main`-PATH-Erkennung entfernt
- expliziter `NAQYA_WHISPER_CLI`-Pfad kanonisiert
- temporäre STT-Dateien in privaten Tauri-App-Cache verschoben
- kollisionsgeschützte Dateierzeugung mit `create_new(true)`
- `sync_all()` vor Übergabe an whisper.cpp

## Pflegevertrag
Diese Datei wird bei jeder relevanten funktionalen, technischen, sicherheitsrelevanten, Build-, CI-, Release- oder Architekturänderung geprüft und aktualisiert. Zusätzlich wird vor und nach jeder Iteration der reale Repository-, PR-, Merge- und CI-Stand geprüft. Erledigte Punkte zunächst in `Erledigt` verschieben; neue Risiken oder Folgearbeiten sofort aufnehmen.
