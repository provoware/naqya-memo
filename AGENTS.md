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
- `TODO.md` ist die operative Restarbeitenliste und muss denselben Fortschrittsstand führen.

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
Linux und Windows verwenden denselben Diagnosevertrag und denselben fachlichen Evidence-Fingerprint. Aktuell validierter Fingerprint:
`018452a4b7683cba40dbce2a2c221aa6b31e55c846470baef35e4baa13081aaf`

Der Fingerprint bindet gemeinsame Software-/Diagnoseinvarianten, nicht plattformspezifische Paket- oder Sidecar-Binärhashes. Eine fachliche Änderung am Diagnosevertrag, Fehlercodekatalog oder Fingerprint-Schema erfolgt nur als eigener versionierter Vertragswechsel mit neuen Tests und neuer Evidence.

## Hardware-Abnahmeregeln ab 0.5.1-E
- CI-Paketabnahme ist keine reale Hardwarefreigabe.
- Hardwarefreigaben müssen an einen validierten Evidence-Fingerprint gebunden sein.
- Plattform, OS-Version, Hardware, Mikrofon, Modell-SHA, Testdauer und Ergebnis müssen nachvollziehbar dokumentiert sein.
- 30-/60-Minuten-Aussagen zu Stabilität, CPU, RAM oder Echtzeitfaktor dürfen nur aus realen Messungen stammen.
- E3-Runtime-Metriken und E4-Ressourcenmetriken werden im Standardpfad über E5/E6 direkt und SHA-gebunden in den Hardware-Nachweis importiert; manuelles Abschreiben ist kein bevorzugter Freigabepfad.
- `AudioWorklet` wird erst gegen eine dokumentierte Baseline bewertet; die bestehende Aufnahmeimplementierung wird nicht gleichzeitig mit der Baseline-Erhebung umgebaut.

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
`TODO.md` ist die operative Restarbeitenliste. Erledigte Punkte werden nachvollziehbar in `Erledigt` verschoben. Fortschrittsangaben müssen mit README und `PROJEKTSTATUS.json` übereinstimmen. Diese Gleichheit wird automatisiert geprüft.

## Qualitätsgate
Je nach Änderungsumfang mindestens:
1. JSON-Struktur + Duplicate-Key-Erkennung
2. Text-/Merge-Integrität einschließlich README/TODO/Status-Gleichstand
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
**0.5.1-E6 – Runtime-Metriken direkt in Hardware-Evidence, 89 % / 8 von 9 Hauptpunkten**

Validiert:
- deterministisches Linux-DEB mit startbarem Sidecar
- Windows-NSIS mit startbarem gepacktem Sidecar
- Linux-/Windows-Release-Evidence und automatischer Paarvergleich
- zentraler Diagnosevertrag mit unveränderter plattformübergreifender Semantik
- Evidence-Fingerprint `018452a4b7683cba40dbce2a2c221aa6b31e55c846470baef35e4baa13081aaf`
- maschinenlesbarer Hardware-Abnahmevertrag und fail-closed Collector
- Runtime-Metrikexport mit Segmentbilanz und RTF
- Prozessfamilienmessung für CPU und Peak-RAM
- direkter SHA-gebundener Import von Runtime- und Ressourcenmetriken in Hardware-Evidence

Nicht als reale Hardwarefreigabe validiert:
- Mikrofon-/Endgerätebetrieb unter Linux und Windows
- 30-/60-Minuten-Langzeitverhalten
- CPU-/RAM-/Echtzeitfaktor-Baseline auf Referenzhardware
- AudioWorklet als Ersatz für ScriptProcessor

## Nächster Entwicklungsblock
**0.5.1-E7 – Reale Linux-Smoke-Hardwareabnahme**

Reihenfolge:
1. validiertes Linux-Paket auf realem Referenzgerät installieren und starten
2. Mikrofon, geschützten Modellpfad und gebündelten Sidecar real verwenden
3. E3/E4-Messdateien erzeugen und über E5/E6 in `HARDWARE_ACCEPTANCE.json` importieren
4. Hardware-Nachweis validieren; kein PASS ohne 0 Segmentverluste und alle realen Bestätigungen
5. danach Windows-Smoke, `long30`, `long60` und erst dann `AudioWorklet`.
