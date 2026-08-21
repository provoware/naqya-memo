# TODO – NAQYA

Stand: 2026-08-21
Aktueller Entwicklungsstand: `0.5.0 – Desktop Sidecar Integration & Hardening`
Aktueller Pflegezweig: `pflege/0.5.0-status-konsistenz`

## P0 – Freigabekritisch

### [in Arbeit] Repository- und Merge-Stand je Iteration prüfen
Komponente: Repository / Freigabe / CI

Abnahmekriterien:
- vor jeder Iteration aktuellen `main`-Commit prüfen
- Arbeitszweig, Head-SHA, PR-Status und Mergefähigkeit prüfen
- prüfen, ob der letzte freigegebene Stand tatsächlich nach `main` gemergt wurde
- CI für den exakten aktuellen Head-SHA prüfen
- nach jeder Iteration denselben Abgleich erneut durchführen
- nach Merge neuen `main`-Commit dokumentieren
- bei Abweichungen zuerst Repository-/PR-/CI-Synchronität herstellen

Aktueller Stand:
- PR #8 ist erfolgreich nach `main` gemergt
- Merge-Commit: `29a07f918d32ab1cf3be9df299d213121849d3b3`
- letzter geprüfter PR-Head: `1279b4bde3623ab86d1475975fb6e88c9f875473`
- Qualitätsprüfung Run #144 für diesen Head: erfolgreich
- veralteter Parallel-PR #3 wurde als überholt geschlossen

### [in Arbeit] 0.5.0-Metadaten und Projektstatus konsistent nachziehen
Komponente: Versionierung / Dokumentation / Offline-Cache

Abnahmekriterien:
- `VERSION.json`, `PROJEKTSTATUS.json`, Tauri-Version und Cargo-Version auf `0.5.0`
- Sidecar-Status entspricht dem realen gemergten Code
- Service-Worker-Cache auf `naqya-0.5.0`
- statische Verträge prüfen die neuen 0.5-Invarianten
- CI für exakten Pflegezweig-Head vollständig grün

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
- Plattform, Upstream-Commit, Dateiname und Dateigröße
- SHA-256
- Buildnachweis
- eindeutige Zuordnung zum NAQYA-Release

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

### [offen] CHANGELOG für 0.5.0 konsolidieren
Komponente: Dokumentation

Abnahmekriterien:
- Runtimevertrag, Tauri-Sidecar-Integration und Sicherheitsänderungen zusammenführen
- bekannte Einschränkungen klar benennen
- tatsächliche Freigabegates dokumentieren

### [offen] Veraltete Release-04-Bezeichnungen prüfen
Komponente: Wartbarkeit

Abnahmekriterien:
- feststellen, ob `services/release-04.js` nur historischer Modulname oder fachlich überholt ist
- keine reine Umbenennung ohne Nutzen
- bei Änderung alle Offline-Cache-, HTML- und Testreferenzen atomar anpassen

## Erledigt

### [erledigt] Reproduzierbaren whisper.cpp-Runtimevertrag festlegen
- Upstream und Commit fest gepinnt
- CPU-Releaseprofil mit `GGML_NATIVE=OFF`
- Linux-/Windows-Zielnamen definiert
- SHA-256-Erzeugung vorgesehen
- Laufzeit-Downloads ausgeschlossen

### [erledigt] Native Runtime-Sicherheit härten
- generische `main`-PATH-Erkennung entfernt
- expliziter `NAQYA_WHISPER_CLI`-Pfad kanonisiert
- private Tauri-App-Cache-Tempdateien
- kollisionsgeschützte Dateierzeugung
- `sync_all()` vor Übergabe an whisper.cpp

### [erledigt] Linux-Tauri-Sidecar integrieren und CI-validieren
- `tauri-plugin-shell` und `externalBin`
- reproduzierbarer Linux-x86_64-Sidecar-Build
- SHA-256-Artefaktprüfung
- Sidecar vor externem CLI-Fallback
- Runtimequelle diagnostizierbar
- PR #8 erfolgreich gemergt

### [erledigt] Überholten Parallel-PR #3 bereinigen
- Branch war gegenüber `main` 31 Commits voraus und 36 Commits zurück
- Inhalt inzwischen durch validierte PRs #4 bis #8 ersetzt
- PR nachvollziehbar als überholt geschlossen

## Pflegevertrag
Diese Datei wird bei jeder relevanten funktionalen, technischen, sicherheitsrelevanten, Build-, CI-, Release- oder Architekturänderung geprüft und aktualisiert. Zusätzlich wird vor und nach jeder Iteration der reale Repository-, PR-, Merge- und CI-Stand geprüft. Erledigte Punkte zunächst in `Erledigt` verschieben; neue Risiken oder Folgearbeiten sofort aufnehmen.
