# AGENTS.md – NAQYA Entwicklungsvertrag

## Zweck
Diese Datei ist die verbindliche Arbeitsanweisung für alle künftigen Entwicklungsänderungen an NAQYA. Sie wird bei jeder relevanten Änderung geprüft und nur dann geändert, wenn sich der Vertrag tatsächlich ändert.

## Grundregeln
- Nutzerseitige Benennungen, Statusangaben, Berichte und Dokumentation grundsätzlich auf Deutsch halten.
- Änderungen klein, nachvollziehbar, rückrollbar und testbar umsetzen.
- Kein Merge nach `main`, solange der exakte PR-Head nicht vollständig durch sein Qualitätsgate gelaufen ist.
- Keine stillen Fallbacks, keine ungeprüften Runtime-Downloads, keine ungebundenen Releasebehauptungen.
- Reproduzierbarkeit, SHA-256-Nachweis, Offline-Fähigkeit und Plattformbindung haben Vorrang vor Komfort-Abkürzungen.

## Repository- und Merge-Pflicht je Iteration
Vor Beginn und nach Abschluss jeder Iteration werden real geprüft:
- aktueller `main`-Commit
- Arbeitszweig und Head-SHA
- Pull Request: offen/geschlossen, Draft/Ready, mergefähig
- CI für den **exakten Head-SHA**
- offene Review-Threads
- veraltete Parallel-PRs oder widersprüchliche Branches
- nach Merge der tatsächlich resultierende `main`

Wenn Repository, PR, CI oder Dokumentation nicht synchron sind, wird zuerst dieser Zustand bereinigt.

## Merge-Konflikt- und Textintegritätsregeln
- Konflikte niemals durch bloßes Aneinanderhängen beider Varianten lösen.
- Doppelte JSON-Schlüssel sind verboten.
- README-, TODO- und Statusaussagen dürfen nicht konkurrierend doppelt vorkommen.
- Merge-Marker `<<<<<<<`, `=======`, `>>>>>>>` dürfen nicht verbleiben.
- `README.md` ist die kanonische menschenlesbare Gesamtübersicht.
- `PROJEKTSTATUS.json` ist die kanonische maschinenlesbare Statusübersicht.

## Code- und Entwicklerdokumentationsregeln
- `CONTRIBUTING.md` ist der kurze Einstieg.
- `docs/ENTWICKLERDOKUMENTATION.md` ist die kanonische technische Übergabe.
- `docs/DIAGNOSE_LOGGING.md` ist der fachliche Diagnose-/Privacy-/Evidence-Vertrag.
- Codekommentare bleiben sparsam und erklären vor allem **warum** eine Invariante existiert.
- Für schwer erkennbare Grenzen wird `ENTWICKLERHINWEIS` direkt an der betroffenen Stelle verwendet.
- Produktversion und IndexedDB-Schema sind getrennte Verträge: **Produktversion ≠ Datenbankschema**.

## Diagnose-, Logging- und Evidence-Regeln
- `diagnostics/DIAGNOSTICS_CONTRACT.json` ist der kanonische Maschinenvertrag.
- Aktuell validierte Identität:
  - Schema: `1`
  - Ereignisschema: `1`
  - Format: `NAQYA-DIAGNOSTICS`
  - SHA-256: `fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425`
- Fehlercodes werden niemals umgedeutet oder wiederverwendet.
- Ein Code wie `NAQYA-STT-4002` hat auf Linux und Windows dieselbe Bedeutung.
- Runtime-Diagnosen speichern standardmäßig keine Audioinhalte, Transkripte, Dokument-/Notiztexte, Secrets, Tokens oder vollständigen Benutzerpfade.
- Der Puffer ist hart begrenzt; Wiederholungen werden dedupliziert.
- `retry-once` darf pro Ereignis höchstens einmal als explizite Safe Action ausgeführt werden.
- Logging arbeitet fail-safe und darf Produktfunktionen nicht zum Absturz bringen.
- `RELEASE_EVIDENCE.json` bindet den exakten Diagnosevertrag über SHA-256.

### Plattforminvariante ab 0.5.1-D
Der in 0.5.1-C validierte Diagnosevertrag wird für den Windows-Nachweis **unverändert wiederverwendet**. Der Windows-Build muss den SHA-256
`fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425`
hart prüfen. Eine Abweichung ist ein Vertragsbruch und muss CI abbrechen.

Wenn eine fachliche Änderung am Diagnosevertrag wirklich nötig wird, erfolgt sie als eigener versionierter Diagnoseblock mit neuen Tests und neuer Evidence – niemals still als Nebenwirkung eines Plattformbuilds.

## Pflichtdateien bei Änderungen
Bei funktionalen, technischen, sicherheitsrelevanten, Build-, CI-, Release- oder Architekturänderungen sind mindestens zu prüfen:
- `AGENTS.md`
- `TODO.md`
- `README.md`
- `CONTRIBUTING.md`
- `docs/ENTWICKLERDOKUMENTATION.md`
- `CHANGELOG.md`
- `PROJEKTSTATUS.json`
- `VERSION.json`
- `LAIENANLEITUNG.md`, wenn Bedienung oder Voraussetzungen betroffen sind
- relevante `docs/`, `tests/` und Workflows

Unveränderte Dateien bleiben unverändert, wenn keine inhaltliche Änderung nötig ist.

## TODO-Vertrag
`TODO.md` ist die operative Restarbeitenliste. Erledigte Punkte werden nachvollziehbar in `Erledigt` verschoben. Fortschrittsangaben müssen mit README und `PROJEKTSTATUS.json` übereinstimmen.

## Qualitätsgate
Je nach Änderungsumfang mindestens:
1. JSON-Struktur + Duplicate-Key-Erkennung
2. Text-/Merge-Integrität
3. JavaScript-Syntax
4. Diagnose-Laufzeitregression und Diagnosevertrag
5. deterministisches Desktop-Staging
6. Rust-Formatierung + `cargo check`
7. Sidecar-Build + SHA-256
8. statische Projektverträge
9. Shell-Syntax
10. vollständiger Plattform-Bundle-Test bei Releaseänderungen
11. reale Hardwareabnahme, sobald sie Freigabeziel ist

## Sidecar- und Runtime-Regeln
- whisper.cpp nur aus festgelegtem Upstream/Commit bauen.
- Tauri-Sidecar vor PATH-Fallback.
- Fallback darf einen gestarteten Sidecar mit Laufzeitfehler nicht still ersetzen.
- Runtimequelle muss diagnostizierbar sein.
- Linux und Windows sind getrennte Paket-/Hardware-Abnahmeziele, teilen aber denselben Diagnosecodevertrag.
- Release-Artefakte benötigen Paket-/Sidecar-SHA-256 und Buildumgebungszuordnung.

## Versions- und Freigaberegeln
- `main` enthält nur validierte Stände.
- größere Schritte über eigenen Branch + Draft-PR.
- Merge bevorzugt Squash + `expected_head_sha`.
- nach jedem Merge resultierenden `main` erneut prüfen.
- eine Iteration ist erst abgeschlossen, wenn Repository, PR, CI und Dokumentation übereinstimmen.

## Aktueller validierter Stand
**0.5.1-C – Diagnose, Logging & Evidence-Bindung**

Validiert:
- deterministisches Linux-DEB mit startbarem Sidecar
- deterministisches DEB-Repacking
- Release Evidence
- zentraler Diagnosevertrag
- Ringpuffer, Deduplizierung, Privacy-Redaktion, Safe Actions und `retry-once`
- SHA-256-Bindung Diagnosevertrag ↔ Release Evidence
- Qualitätsprüfung #268 und Linux-Bundle-Nachweis #14 auf Quellcommit `0388cda77c6696017c5b00cb795f5758af2d5e22`

## Nächster Entwicklungsblock
**0.5.1-D – Windows-x86_64-Bundle & plattformübergreifender Evidence-Nachweis**

Reihenfolge:
1. C-Contract-SHA unverändert als Windows-Invariante prüfen.
2. whisper.cpp für `x86_64-pc-windows-msvc` aus demselben Upstream-Commit bauen.
3. Windows-Tauri-Bundle erzeugen und Sidecar aus Paketkontext starten.
4. Windows-Paket-/Sidecar-SHA und Toolchain in Evidence aufnehmen.
5. Linux/Windows auf identische Diagnosecodebedeutung prüfen.
6. danach reale Hardwareabnahme und AudioWorklet-/Langzeithärtung.
