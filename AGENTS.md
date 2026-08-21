# AGENTS.md – NAQYA Entwicklungsvertrag

## Zweck
Diese Datei ist die verbindliche Arbeitsanweisung für alle künftigen Entwicklungsänderungen an NAQYA. Sie muss bei jeder relevanten Änderung mitgeprüft und bei Bedarf aktualisiert werden.

## Grundregeln
- Nutzerseitige Benennungen, Statusangaben, Berichte und Dokumentation grundsätzlich auf Deutsch halten.
- Änderungen klein, nachvollziehbar und rückrollbar umsetzen.
- Kein Merge nach `main`, solange der exakte PR-Head nicht vollständig durch das Qualitätsgate gelaufen ist.
- Bei sicherheits-, runtime-, build- oder releasekritischen Änderungen immer zuerst bestehende Verträge lesen und danach gezielt härten.
- Keine stillen Fallbacks einführen. Fallbacks müssen diagnostizierbar, dokumentiert und testbar sein.
- Keine ungeprüften Laufzeit-Downloads für kritische Binärartefakte oder Sprachmodelle.
- Reproduzierbarkeit, SHA-256-Nachweis und Plattformbindung haben Vorrang vor Komfort-Abkürzungen.

## Repository- und Merge-Pflicht je Iteration
Vor Beginn **und** nach Abschluss jeder Entwicklungsiteration muss der reale GitHub-Stand geprüft werden. Diese Prüfung ist verpflichtend und darf nicht durch Annahmen aus vorherigen Chatnachrichten ersetzt werden.

Mindestens zu prüfen und im Status zu berücksichtigen:
- aktueller `main`-Commit
- aktueller Arbeitszweig und dessen Head-SHA
- zugehöriger Pull Request: offen/geschlossen, Entwurf/Review, mergefähig/nicht mergefähig
- ob der letzte freigegebene Stand tatsächlich nach `main` gemergt wurde
- ob der Arbeitszweig auf dem aktuellen `main` basiert oder hinter `main` zurückliegt
- CI-/Qualitätsgate für den **exakten aktuellen Head-SHA**
- offene Review-Threads oder blockierende Prüfungen
- nach einem Merge: resultierenden `main`-Commit erneut prüfen und dokumentieren

Wenn Repository, PR, CI oder Dokumentation nicht synchron sind, wird zuerst dieser Zustand bereinigt. Neue Funktionsarbeit beginnt erst danach.

## Pflichtdateien bei Änderungen
Bei jeder funktionalen, technischen, sicherheitsrelevanten, Build-, CI-, Release- oder Architekturänderung sind mindestens folgende Dateien auf Aktualisierungsbedarf zu prüfen:

- `AGENTS.md`
- `TODO.md`
- `README.md`
- `PROJEKTSTATUS.json`
- `VERSION.json`
- relevante Dateien unter `docs/`
- relevante Tests unter `tests/`
- `.github/workflows/validate.yml`, falls sich Prüf- oder Buildverträge ändern

Wenn keine inhaltliche Änderung nötig ist, bleibt die Datei unverändert; die Prüfung selbst ist trotzdem Pflicht.

## TODO-Vertrag
`TODO.md` ist die operative Restarbeitenliste und muss bei jeder relevanten Projektänderung geprüft werden.

Ein TODO-Eintrag muss nach Möglichkeit enthalten:
- Priorität: `P0`, `P1`, `P2` oder `P3`
- Status: `offen`, `in Arbeit`, `blockiert`, `erledigt`
- betroffene Plattform oder Komponente
- klare Abnahmekriterien
- bekannte Abhängigkeiten oder Risiken

Erledigte Punkte werden nicht kommentarlos gelöscht, sondern zunächst in den Abschnitt `Erledigt` verschoben. Größere abgeschlossene Blöcke können später in CHANGELOG oder Release-Dokumentation überführt werden.

## Qualitätsgate
Vor Freigabe oder Merge sind je nach Änderungsumfang mindestens zu prüfen:

1. JSON-Strukturprüfung
2. JavaScript-Syntaxprüfung
3. Rust-Formatprüfung
4. `cargo check`
5. statische Projektverträge
6. Shell-Syntaxprüfung
7. Sidecar-Build und Integritätsprüfung, wenn native Runtime betroffen ist
8. reale Plattform-/Hardwareabnahme, sobald sie Bestandteil des Freigabeziels ist

Ein fehlgeschlagenes Gate wird ursachenbezogen korrigiert. Keine kosmetischen oder fachfremden Änderungen in denselben Fix mischen.

## Sidecar- und Runtime-Regeln
- `whisper.cpp` wird nur aus dem festgelegten Upstream und dem festgelegten Commit gebaut.
- Der gebündelte Tauri-Sidecar ist gegenüber PATH-basierten Fallbacks zu bevorzugen.
- Fallbacks dürfen den gebündelten Sidecar nicht still überstimmen.
- Die tatsächlich verwendete Runtimequelle muss diagnostizierbar sein.
- Release-Artefakte benötigen SHA-256-Nachweis.
- Linux und Windows werden als getrennte Abnahmeziele behandelt.

## Versions- und Freigaberegeln
- `main` enthält nur validierte Stände.
- Größere Funktionsschritte über eigenen Zweig und Pull Request entwickeln.
- PR zunächst als Entwurf führen, solange die Qualitätsprüfung noch nicht vollständig grün ist.
- Merge bevorzugt als Squash mit erwarteter Head-SHA absichern.
- Nach Merge den resultierenden `main`-Commit dokumentieren.
- Eine Iteration gilt erst als abgeschlossen, wenn Repository-, PR-, CI- und Dokumentationsstand miteinander übereinstimmen.

## Dokumentationspflicht
Bei jeder relevanten Änderung müssen Status und Restarbeiten mit dem realen Codezustand übereinstimmen. Insbesondere dürfen `TODO.md`, `PROJEKTSTATUS.json`, README und PR-Beschreibung keinen bereits erledigten oder noch nicht umgesetzten Stand behaupten.

## Aktueller Schwerpunkt
Aktueller Entwicklungsstrang: `0.5.0-B – Tauri-Sidecar-Integration`.

Ziel dieses Strangs:
- gebündelten whisper.cpp-Sidecar über Tauri `externalBin` integrieren,
- Linux-x86_64 reproduzierbar bauen und per SHA-256 prüfen,
- gebündelten Sidecar vor externem CLI-Fallback verwenden,
- Runtimequelle diagnostizierbar machen,
- Integration durch CI und statische Verträge absichern.

Nicht Teil dieser Iteration sind derzeit die vollständige Windows-Bundle-Abnahme und reale Mikrofon-/Hardwaretests.
