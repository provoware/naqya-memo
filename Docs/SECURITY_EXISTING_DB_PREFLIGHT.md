# Bestehende Projekt-DB – fail-closed Start-Preflight

Status: Release-Freeze-Härtung, kein neues Produktfeature.

## Befund

Der offizielle Desktop-Entry-Point importiert anschließend `secure_server` und den Basisserver. Diese unteren Module dürfen beim Erststart Schema und Bootstrap-Daten anlegen. Eine bereits vorhandene, aber beschädigte, unlesbare oder als falscher Pfadtyp vorliegende `daten/core.sqlite3` darf deshalb nicht still wie eine fehlende Datenbank behandelt werden.

Der erste gehärtete Preflight öffnete Bestandsdaten bereits read-only und verlangte ein lesbares `PRAGMA schema_version`. Das beweist jedoch nur, dass SQLite die Datei und zentrale Metadaten lesen kann. Strukturelle Schäden in B-Tree-/Indexreferenzen können dabei unentdeckt bleiben und erst nach Beginn der Produktlogik auffallen.

## Release-Freeze-Optimierung

`app/secure_response_server.py` prüft jetzt **vor dem Import** des mutierenden Serverpfads:

- fehlt `daten/core.sqlite3`, bleibt der normale Erststart erlaubt,
- existiert der Pfad, muss er eine regulär lesbare Datei sein,
- die Datei wird ausschließlich read-only mit `mode=ro` und `PRAGMA query_only=ON` geöffnet,
- `PRAGMA schema_version` muss lesbar sein,
- anschließend muss `PRAGMA quick_check` ausschließlich `ok` liefern,
- beschädigte/unlesbare SQLite-Datei -> `EXISTING_PROJECT_DB_PREFLIGHT_UNREADABLE`,
- strukturell inkonsistente SQLite-Datei -> `EXISTING_PROJECT_DB_PREFLIGHT_INTEGRITY_FAILED`,
- falscher Pfadtyp -> `EXISTING_PROJECT_DB_PREFLIGHT_UNSAFE`.

Der Preflight verändert die Bestandsdatei nicht. `quick_check` ist bewusst der leichtere SQLite-Integritätscheck für den Startpfad; er prüft wesentliche Seiten-/B-Tree-/Schema-Invarianten, ohne den deutlich teureren vollständigen `integrity_check` als dauerhafte Startlast einzuführen.

## Regression

`tests/security/test_existing_db_preflight_fail_closed.py` beweist neun Verträge:

1. eine komplett unlesbare vorhandene SQLite-Datei stoppt den offiziellen Produktionsstart vor dem Bootstrap,
2. ihre Bytes bleiben exakt unverändert,
3. nach dem Fehler entsteht keine Erststart-PIN-Datei,
4. ein Verzeichnis am erwarteten DB-Dateipfad wird fail-closed abgewiesen,
5. auch dieser falsche Pfadtyp löst keine Bootstrap-Credentialmutation aus,
6. eine speziell erzeugte strukturell beschädigte SQLite-Datei bleibt auf `schema_version`-Ebene lesbar,
7. `quick_check` erkennt diesen tieferen Schaden und stoppt mit `EXISTING_PROJECT_DB_PREFLIGHT_INTEGRITY_FAILED`,
8. auch diese Datei bleibt bytegenau unverändert,
9. auch der Integritätsfehler erzeugt keine Erststart-PIN-Datei.

Erwartete Zusammenfassung: `SUMMARY total=9 passed=9 failed=0`.

## Wirkung

Der Produktionsstart beweist jetzt nicht nur „SQLite lässt sich öffnen“, sondern auch einen grundlegenden konsistenten Datenbankzustand **vor jeder möglichen Produktmutation**. Damit sinkt das Risiko, dass versteckte Bestandskorruption erst während Bootstrap, Migration oder normalem Startschreiben sichtbar wird.

## Release-Grenze

Dieser Slice ersetzt weder Backup-/Recovery-Tests noch einen vollständigen Offline-`integrity_check`, Datenträgerausfall-, Disk-full-, Browser-, Mikrofon-, Android- oder iPhone-Abnahmen. HTTP Basic Auth und der fehlende explizit invalidierbare Lock-/Logout-Zustand bleiben ebenfalls offen. Release bleibt NO-GO.
