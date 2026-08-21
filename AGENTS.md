# AGENTS.md – NAQYA Entwicklungsvertrag

## Zweck
Diese Datei ist die verbindliche Arbeitsanweisung für alle künftigen Entwicklungsänderungen an NAQYA. Sie wird bei jeder relevanten Änderung mitgeprüft und bei Bedarf aktualisiert.

## Grundregeln
- Nutzerseitige Benennungen, Statusangaben, Berichte und Dokumentation grundsätzlich auf Deutsch halten.
- Änderungen klein, nachvollziehbar und rückrollbar umsetzen.
- Kein Merge nach `main`, solange der exakte PR-Head nicht vollständig durch das Qualitätsgate gelaufen ist.
- Bei sicherheits-, Runtime-, Build- oder Releaseänderungen zuerst bestehende Verträge lesen und danach gezielt härten.
- Keine stillen Fallbacks. Fallbacks müssen diagnostizierbar, dokumentiert und testbar sein.
- Keine ungeprüften Laufzeit-Downloads für kritische Binärartefakte oder Sprachmodelle.
- Reproduzierbarkeit, SHA-256-Nachweis und Plattformbindung haben Vorrang vor Komfort-Abkürzungen.
- Build-, Ziel-, Cache-, Modell- und temporäre Laufzeitartefakte gehören nicht ins Repository und sind über `.gitignore` abzusichern.

## Repository- und Merge-Pflicht je Iteration
Vor Beginn **und** nach Abschluss jeder Entwicklungsiteration wird der reale GitHub-Stand geprüft. Annahmen aus vorherigen Chatnachrichten ersetzen diese Prüfung nicht.

Mindestens zu prüfen:
- aktueller `main`-Commit
- aktueller Arbeitszweig und Head-SHA
- zugehöriger Pull Request: offen/geschlossen, Entwurf/Review, mergefähig/nicht mergefähig
- ob der letzte freigegebene Stand tatsächlich nach `main` gemergt wurde
- ob der Arbeitszweig auf dem aktuellen `main` basiert oder hinter `main` zurückliegt
- CI-/Qualitätsgate für den **exakten aktuellen Head-SHA**
- offene Review-Threads oder blockierende Prüfungen
- veraltete offene PRs oder widersprüchliche Parallelstände
- nach einem Merge: resultierenden `main`-Commit erneut prüfen und dokumentieren

Wenn Repository, PR, CI oder Dokumentation nicht synchron sind, wird zuerst dieser Zustand bereinigt. Neue Funktionsarbeit beginnt erst danach.

## Merge-Konflikt- und Textintegritätsregeln
- Konflikte niemals durch bloßes Aneinanderhängen beider Varianten auflösen.
- Für jede widersprüchliche Aussage wird genau eine kanonische Fassung gewählt.
- Doppelte JSON-Schlüssel sind verboten, auch wenn Standardparser sie akzeptieren.
- README-Abschnitte, TODO-Blöcke und Statusfelder dürfen nicht mehrfach mit konkurrierendem Inhalt vorkommen.
- Merge-Konfliktmarker wie `<<<<<<<`, `=======` und `>>>>>>>` dürfen in produktiven Text-/Quell-Dateien nicht verbleiben.
- Nach jedem Merge muss der **resultierende `main`-Stand** erneut geprüft werden; ein grüner PR-Head allein reicht bei manueller Konfliktauflösung nicht als Nachweis.
- `README.md` ist die kanonische menschenlesbare Gesamtübersicht und muss den realen Code-, CI- und Freigabestand korrekt wiedergeben.

## Repository-Hygiene
- Veraltete oder durch neuere Architekturpfade ersetzte PRs nicht offen liegen lassen; nachvollziehbar als überholt schließen.
- Keine alten Parallelzweige in neue Arbeit hineinmergen, wenn ihre Inhalte bereits durch neuere, validierte Iterationen ersetzt wurden.
- Dokumentations-, Versions- und Projektstatusangaben dürfen dem realen `main` nicht hinterherlaufen.
- Aufräumarbeiten getrennt von größeren Funktionsänderungen halten, damit Review und Rückrollback eindeutig bleiben.

## Pflichtdateien bei Änderungen
Bei jeder funktionalen, technischen, sicherheitsrelevanten, Build-, CI-, Release- oder Architekturänderung sind mindestens folgende Dateien auf Aktualisierungsbedarf zu prüfen:
- `AGENTS.md`
- `TODO.md`
- `README.md`
- `CHANGELOG.md`
- `PROJEKTSTATUS.json`
- `VERSION.json`
- `LAIENANLEITUNG.md`, wenn sich Bedienung, Installation oder Voraussetzungen ändern
- relevante Dateien unter `docs/`
- relevante Tests unter `tests/`
- `.github/workflows/validate.yml`, falls sich Prüf- oder Buildverträge ändern

Wenn keine inhaltliche Änderung nötig ist, bleibt die Datei unverändert; die Prüfung selbst ist trotzdem Pflicht.

## TODO-Vertrag
`TODO.md` ist die operative Restarbeitenliste. Einträge enthalten nach Möglichkeit Priorität, Status, Komponente und klare Abnahmekriterien. Erledigte Punkte werden zunächst im Abschnitt `Erledigt` dokumentiert.

## Qualitätsgate
Vor Freigabe oder Merge sind je nach Änderungsumfang mindestens zu prüfen:
1. JSON-Strukturprüfung **mit Duplicate-Key-Erkennung**
2. Textintegrität und Merge-Konfliktmarker
3. JavaScript-Syntaxprüfung
4. Rust-Formatprüfung
5. `cargo check`
6. statische Projektverträge
7. Shell-Syntaxprüfung
8. Sidecar-Build und Integritätsprüfung, wenn native Runtime betroffen ist
9. vollständiger Desktop-Bundle-Test, sobald Bundle-/Releasefähigkeit Bestandteil des Ziels ist
10. reale Plattform-/Hardwareabnahme, sobald sie Bestandteil des Freigabeziels ist

Fehlgeschlagene Gates werden ursachenbezogen korrigiert. Keine fachfremden Änderungen in denselben Fix mischen.

## Sidecar- und Runtime-Regeln
- `whisper.cpp` wird nur aus dem festgelegten Upstream und Commit gebaut.
- Tauri ist über `externalBin` für den Sidecar konfiguriert.
- Der Sidecar ist gegenüber PATH-basierten Fallbacks zu bevorzugen.
- Fallbacks dürfen den Sidecar nicht still überstimmen.
- Die tatsächlich verwendete Runtimequelle muss diagnostizierbar sein.
- CI-Build eines Sidecars darf nicht mit einer vollständigen Endanwender-Bundle-Abnahme verwechselt werden.
- Release-Artefakte benötigen SHA-256-Nachweis und Zuordnung zur Buildumgebung.
- Linux und Windows werden als getrennte Abnahmeziele behandelt.

## Versions- und Freigaberegeln
- `main` enthält nur validierte Stände.
- Größere Funktionsschritte über eigenen Zweig und Pull Request entwickeln.
- PR zunächst als Entwurf führen, solange die Qualitätsprüfung noch nicht vollständig grün ist.
- Merge bevorzugt als Squash und mit erwarteter Head-SHA absichern, sofern kein technischer Grund dagegen spricht.
- Bei manuell aufgelösten Mergekonflikten muss der resultierende Merge-Commit erneut vollständig validiert werden.
- Nach Merge den resultierenden `main`-Commit dokumentieren.
- Version, Projektstatus, Tauri-Version, Offline-Cache und Dokumentation müssen denselben realen Entwicklungsstand beschreiben.
- Eine Iteration gilt erst als abgeschlossen, wenn Repository-, PR-, CI- und Dokumentationsstand übereinstimmen.

## Dokumentationspflicht
`TODO.md`, `PROJEKTSTATUS.json`, README, CHANGELOG und PR-Beschreibung dürfen keinen bereits erledigten oder noch nicht umgesetzten Stand behaupten. Historische Entwicklungsdokumente müssen klar als historisch gekennzeichnet sein, wenn darin Aussagen enthalten sind, die heute überholt sind.

## Aktueller validierter Stand
**0.5.0 – Tauri-Sidecar-Integration & Repository-Konsolidierung**

Bereits umgesetzt:
- reproduzierbarer whisper.cpp-Runtimevertrag
- Tauri-Sidecar-Konfiguration über `externalBin`
- Linux-x86_64-Sidecar-Build und SHA-256-Prüfung im CI
- Sidecar vor externem CLI-Fallback
- diagnostizierbare Runtimequelle
- geschützter Modellpfad und segmentiertes Offline-Live-STT
- Repository- und Textintegritätsverträge

## Nächster Entwicklungsblock
**0.5.1 – Linux-Bundle-Abnahme, Release-Nachweis & Windows-Sidecar**

Reihenfolge:
1. vollständiges Linux-Tauri-Bundle end-to-end bauen und Sidecar-Inhalt/Start nachweisen
2. maschinenlesbaren Release-Nachweis erzeugen
3. Windows-x86_64-Sidecar und Windows-Bundle reproduzierbar bauen
4. reale Linux-/Windows-Hardware- und Mikrofonabnahme
5. danach AudioWorklet- und Langzeithärtung
