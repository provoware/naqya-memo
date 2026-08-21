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

## Code- und Entwicklerdokumentationsregeln
- `CONTRIBUTING.md` ist der kurze GitHub-Einstieg; längere technische Erklärungen werden dort nicht dupliziert.
- `docs/ENTWICKLERDOKUMENTATION.md` ist die kanonische technische Übergabe für fremde Entwickler und muss Architekturkarte, Vertrauensgrenzen, lokale Prüfungen und den nächsten konkreten Arbeitsblock enthalten.
- Codekommentare bleiben sparsam. Kommentiert wird vor allem **warum** eine Sicherheitsgrenze, Reihenfolge, Migration oder Supply-Chain-Festlegung existiert; offensichtlicher Code wird nicht nacherzählt.
- Für schwer erkennbare Invarianten wird bevorzugt der Marker `ENTWICKLERHINWEIS` direkt an der betroffenen Stelle verwendet.
- Lange Begründungen gehören in die Entwickler- oder Fachdokumentation und werden nicht mehrfach in Quellcode, README und AGENTS kopiert.
- Bei neuen kritischen Modulen oder geänderten Architektur-/Build-/Releasepfaden werden Repository-Landkarte und Änderungsmatrix in der Entwicklerdokumentation geprüft.
- Produktversion und Datenbankschema sind getrennte Verträge. `DB_VERSION` wird ausschließlich bei IndexedDB-Migrationen verändert; eine Produktversion darf nicht automatisch die Datenbankversion erhöhen.
- Veraltete Versionskonstanten in Laufzeitcode, Backup-Metadaten oder UI gelten als Dokumentations-/Statusdrift und müssen behoben oder explizit im TODO geführt werden.

## Diagnose-, Logging- und Evidence-Regeln
- `diagnostics/DIAGNOSTICS_CONTRACT.json` ist der kanonische Maschinenvertrag für Ereignisschema, Fehlercodes, Privacy-Regeln, Deduplizierung und sichere Aktionen.
- Fehlercodes werden **niemals umgedeutet oder wiederverwendet**. Eine neue Bedeutung erhält einen neuen Code.
- Runtime-Diagnosen dürfen standardmäßig keine Audioinhalte, Transkripte, Dokument-/Notiztexte, Secrets, Tokens oder vollständige Benutzerpfade speichern.
- Der Puffer speichert nur bereits bereinigte Ereignisse und ist hart begrenzt; unbegrenztes Logging ist verboten.
- Wiederholungen dürfen nur über explizit freigegebene Safe Actions erfolgen; `retry-once` maximal einmal pro Ereignis. Keine automatischen Retry-Endlosschleifen.
- Diagnosefehler dürfen keine Produktfunktion zum Absturz bringen; der Loggingpfad arbeitet fail-safe.
- `RELEASE_EVIDENCE.json` bindet den exakten Diagnosevertrag über dessen SHA-256. Runtime-Diagnoseexporte müssen denselben Contract-SHA mitführen, damit Release → Runtime-Ereignis nachvollziehbar bleibt.
- Bei Änderungen an Diagnosecodes, Privacy-Regeln, Safe Actions oder Ereignisschema müssen mindestens `services/diagnostics.js`, `diagnostics/DIAGNOSTICS_CONTRACT.json`, `tests/validate_diagnostics.py`, `tests/diagnostics_runtime.test.js` und `docs/DIAGNOSE_LOGGING.md` gemeinsam geprüft werden.

## Pflichtdateien bei Änderungen
Bei jeder funktionalen, technischen, sicherheitsrelevanten, Build-, CI-, Release- oder Architekturänderung sind mindestens folgende Dateien auf Aktualisierungsbedarf zu prüfen:
- `AGENTS.md`
- `TODO.md`
- `README.md`
- `CONTRIBUTING.md`
- `docs/ENTWICKLERDOKUMENTATION.md`
- `CHANGELOG.md`
- `PROJEKTSTATUS.json`
- `VERSION.json`
- `LAIENANLEITUNG.md`, wenn sich Bedienung, Installation oder Voraussetzungen ändern
- relevante Dateien unter `docs/`
- relevante Tests unter `tests/`
- `.github/workflows/validate.yml`, falls sich Prüf- oder Buildverträge ändern

Wenn keine inhaltliche Änderung nötig ist, bleibt die Datei unverändert; die Prüfung selbst ist trotzdem Pflicht.

## TODO-Vertrag
`TODO.md` ist die operative Restarbeitenliste. Einträge enthalten nach Möglichkeit Priorität, Status, Komponente und klare Abnahmekriterien. Erledigte Punkte werden zunächst im Abschnitt `Erledigt` dokumentiert. Die Entwickler-Übergabecheckliste muss bei einer Übergabe oder einem größeren Meilenstein sichtbar abgearbeitet werden.

## Qualitätsgate
Vor Freigabe oder Merge sind je nach Änderungsumfang mindestens zu prüfen:
1. JSON-Strukturprüfung **mit Duplicate-Key-Erkennung**
2. Textintegrität und Merge-Konfliktmarker
3. JavaScript-Syntaxprüfung
4. Diagnose-Laufzeitregression und Diagnosevertrag, wenn Diagnose/Runtime betroffen sind
5. Rust-Formatprüfung
6. `cargo check`
7. statische Projektverträge
8. Shell-Syntaxprüfung
9. Sidecar-Build und Integritätsprüfung, wenn native Runtime betroffen ist
10. vollständiger Desktop-Bundle-Test, sobald Bundle-/Releasefähigkeit Bestandteil des Ziels ist
11. reale Plattform-/Hardwareabnahme, sobald sie Bestandteil des Freigabeziels ist

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
**0.5.1-B1 – Linux-Bundle, Release-Nachweis & deterministische DEB-Reproduzierbarkeit**

Bereits umgesetzt:
- deterministisches Desktop-Frontend-Staging über `dist/`
- reales Linux-DEB mit gebündeltem, startbarem whisper.cpp-Sidecar
- SHA-256-, Laufzeitabhängigkeits- und Paketkontextprüfung
- maschinenlesbarer und menschenlesbarer Release-Nachweis
- deterministisches DEB-Repacking mit festem `SOURCE_DATE_EPOCH`
- reproduzierbarer whisper.cpp-Runtimevertrag und geschützter Modellpfad
- Repository-, Textintegritäts- und Entwicklerübergabeverträge

## Nächster Entwicklungsblock
**0.5.1-C – Diagnose, Debugging, Logging & Evidence-Bindung**

Reihenfolge:
1. stabilen Diagnose-/Fehlercodevertrag und Privacy-Regeln festlegen
2. begrenztes, deduplizierendes Offline-Logging mit menschen- und maschinenlesbarem Export integrieren
3. laienverständlichen Auswahldialog mit ausschließlich sicheren Aktionen ergänzen
4. Native-Bridge- und Live-STT-Fehlerpfade instrumentieren
5. Diagnosevertrag per SHA-256 an `RELEASE_EVIDENCE.json` binden
6. Laufzeit- und statische Regressionstests vollständig grün abschließen
7. erst danach README-/TODO-Fortschritt von 56 % auf 78 % anheben
