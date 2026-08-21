# TODO – NAQYA

Stand: 2026-08-21
Aktueller Entwicklungsstrang: `0.5.x – Repository-Konsolidierung`
Aktueller PR: wird für die Konsolidierungsiteration neu erstellt

## P0 – Freigabekritisch

### [in Arbeit] Repository- und Merge-Stand je Iteration prüfen
Komponente: Repository / Freigabe / CI

Abnahmekriterien:
- vor jeder Iteration aktuellen `main`-Commit prüfen
- Arbeitszweig, Head-SHA, PR-Status und Mergefähigkeit prüfen
- veraltete offene PRs und widersprüchliche Parallelstände identifizieren
- CI für den exakten aktuellen Head-SHA prüfen
- nach jeder Iteration denselben Abgleich erneut durchführen
- nach Merge neuen `main`-Commit dokumentieren

Aktueller Stand:
- PR #8 ist gemergt
- `main` nach PR #8: `29a07f918d32ab1cf3be9df299d213121849d3b3`
- veralteter PR #3 wurde als überholt geschlossen
- Konsolidierungszweig basiert auf aktuellem `main`

### [in Arbeit] 0.5.0-Metadaten vollständig konsolidieren
Komponente: Versionierung / Dokumentation / Offline-Cache

Abnahmekriterien:
- `VERSION.json`, `PROJEKTSTATUS.json`, `src-tauri/Cargo.toml` und `src-tauri/tauri.conf.json` = 0.5.0
- Service-Worker-Cache = `naqya-0.5.0`
- README und CHANGELOG beschreiben den realen Sidecar-Stand
- statische Verträge erzwingen diese Konsistenz
- vollständiger CI-Erfolg für den exakten Konsolidierungs-Head

### [in Arbeit] Repository-Hygiene absichern
Komponente: Git / Build / Runtime

Abnahmekriterien:
- `.gitignore` vorhanden
- `.sidecar-build/`, `src-tauri/binaries/`, Tauri-Targets und temporäre Dateien ignoriert
- lokale `.gguf`-/`.bin`-Modelle werden nicht versehentlich versioniert
- statischer Vertrag prüft zentrale Ignore-Regeln

## P1 – Hohe Priorität

### [offen] Windows-x86_64-Sidecar reproduzierbar bauen
Komponente: whisper.cpp / Windows

Abnahmekriterien:
- Build aus identischem fest gepinnten Upstream-Commit
- Tauri-konformer Binärname
- SHA-256-Nachweis
- Windows-Bundle startet den Sidecar tatsächlich

### [offen] Release-Manifest für konkrete Sidecar-Artefakte ergänzen
Komponente: Release / Integrität

Abnahmekriterien:
- Plattform, Upstream-Commit, Dateiname, Dateigröße und SHA-256
- Buildnachweis
- eindeutige Zuordnung zum NAQYA-Release

### [offen] Reale Linux-Desktop-Abnahme durchführen
Komponente: Linux / Mikrofon / STT

Abnahmekriterien:
- Desktop-Bundle startet
- gebündelter Sidecar wird bevorzugt erkannt
- echtes Modell aus geschütztem NAQYA-Modellpfad funktioniert
- Mikrofonaufnahme und segmentiertes Live-Diktat funktionieren
- temporäre WAV-Dateien werden bereinigt
- Providerdiagnose zeigt `whisper.cpp-sidecar`

### [offen] Reale Windows-Desktop-Abnahme durchführen
Komponente: Windows / Mikrofon / STT

Abnahmekriterien analog zur Linux-Abnahme, zusätzlich `.exe`-Sidecar und Windows-Bundle.

## P2 – Qualitätsausbau

### [offen] `ScriptProcessor` durch `AudioWorklet` ersetzen
Komponente: Web Audio / Live-STT

Abnahmekriterien:
- gleiche oder bessere 16-kHz-Mono-Normalisierung
- stabile Segmentbildung
- keine Regression bei Live-Diktat und Recovery
- Firefox- und Chrome-Kompatibilität geprüft

### [offen] Langzeit- und Lasttests für Live-STT durchführen
Komponente: Performance / Stabilität

Abnahmekriterien:
- längere Diktatsitzungen ohne Speicherwachstum oder Segmentverlust
- CPU-/RAM-Verhalten und Echtzeitfaktor dokumentiert
- kontrolliertes Verhalten bei langsamer Transkription

### [offen] Runtime-Diagnose in der Oberfläche deutlicher darstellen
Komponente: UI / Diagnose

Abnahmekriterien:
- Sidecar / externer Fallback / nicht verfügbar klar unterscheidbar
- verwendeter Provider nach Transkription sichtbar
- laienverständliche Fehlermeldung mit konkretem nächsten Schritt

## P3 – Wartbarkeit

### [offen] Alte bereits gemergte Entwicklungszweige auf GitHub löschen
Komponente: Repository-Hygiene

Hinweis: Die aktuell verfügbare GitHub-Schnittstelle unterstützt das sichere Löschen von Branch-Refs nicht. Die Zweige können nach bestätigtem Merge-Stand manuell entfernt werden. Keine Zweige löschen, deren Inhalt nicht nachweislich in `main` enthalten oder bewusst verworfen ist.

## Erledigt

### [erledigt] PR #8 – Tauri-Sidecar-Integration
Ergebnis:
- PR #8 ist nach `main` gemergt
- Linux-Sidecar-Build, SHA-256-Prüfung, Rust-Format, `cargo check`, statische Verträge und Shell-Syntax waren im Qualitätsgate erfolgreich

### [erledigt] Veralteten PR #3 schließen
Ergebnis:
- früherer 0.3.0-Parallelversuch als fachlich ersetzt dokumentiert und geschlossen

### [erledigt] Reproduzierbaren whisper.cpp-Runtimevertrag festlegen
Ergebnis:
- Upstream/Commit fest gepinnt
- CPU-Releaseprofil mit `GGML_NATIVE=OFF`
- Linux-/Windows-Zielnamen definiert
- SHA-256 und keine ungeprüften Laufzeit-Downloads

### [erledigt] Native Runtime-Sicherheit härten
Ergebnis:
- generische `main`-PATH-Erkennung entfernt
- `NAQYA_WHISPER_CLI` kanonisiert
- STT-Tempdateien in privaten Tauri-App-Cache verschoben
- kollisionsgeschützte Dateierzeugung und `sync_all()`

## Pflegevertrag
Diese Datei wird bei jeder relevanten funktionalen, technischen, sicherheitsrelevanten, Build-, CI-, Release- oder Architekturänderung geprüft und aktualisiert. Zusätzlich wird vor und nach jeder Iteration der reale Repository-, PR-, Merge- und CI-Stand geprüft.
