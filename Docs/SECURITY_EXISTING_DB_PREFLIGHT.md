# Bestehende Projekt-DB – fail-closed Start-Preflight

Status: Release-Freeze-Härtung, kein neues Produktfeature.

## Befund

Der offizielle Desktop-Entry-Point importiert anschließend `secure_server` und den Basisserver. Diese unteren Module dürfen beim Erststart Schema und Bootstrap-Daten anlegen. Eine bereits vorhandene, aber beschädigte, unlesbare oder als falscher Pfadtyp vorliegende `daten/core.sqlite3` durfte deshalb nicht still wie eine fehlende Datenbank behandelt werden.

Der bisherige untere Vorcheck gab bei SQLite-/I/O-Fehlern lediglich `False` zurück. Damit bestand das Risiko, dass ein beschädigter Bestandszustand in den Erststartpfad fällt, statt vor jeder möglichen Produktmutation zu stoppen.

## Release-Freeze-Optimierung

`app/secure_response_server.py` prüft jetzt **vor dem Import** des mutierenden Serverpfads:

- fehlt `daten/core.sqlite3`, bleibt der normale Erststart erlaubt,
- existiert der Pfad, muss er eine regulär lesbare Datei sein,
- die Datei wird ausschließlich read-only mit `mode=ro` und `PRAGMA query_only=ON` geöffnet,
- `PRAGMA schema_version` muss lesbar sein,
- beschädigte/unlesbare SQLite-Datei -> `EXISTING_PROJECT_DB_PREFLIGHT_UNREADABLE`,
- falscher Pfadtyp -> `EXISTING_PROJECT_DB_PREFLIGHT_UNSAFE`.

Der Preflight verändert die Bestandsdatei nicht. Gültige leere oder ältere SQLite-Dateien werden nicht pauschal blockiert; bestehende Bootstrap-/Migrationslogik bleibt damit erhalten.

## Regression

`tests/security/test_existing_db_preflight_fail_closed.py` beweist fünf Verträge:

1. eine vorhandene beschädigte SQLite-Datei stoppt den offiziellen Produktionsstart vor dem Bootstrap,
2. ihre Bytes bleiben exakt unverändert,
3. nach dem Fehler entsteht keine Erststart-PIN-Datei,
4. ein Verzeichnis am erwarteten DB-Dateipfad wird fail-closed abgewiesen,
5. auch dieser falsche Pfadtyp löst keine Bootstrap-Credentialmutation aus.

Erwartete Zusammenfassung: `SUMMARY total=5 passed=5 failed=0`.

## Wirkung

Ein beschädigtes bestehendes Projekt wird nicht mehr versehentlich als neues Projekt interpretiert. Das reduziert das Risiko von Folgemutationen in einem bereits fehlerhaften Datenzustand und macht den Produktionsstart konsequenter nach dem Prinzip **Vorprüfung -> erst dann Mutation**.

## Release-Grenze

Dieser Slice repariert ausschließlich die vorhandene DB-Vorprüfung. Er ersetzt weder Backup-/Recovery-Tests noch reale Datenträgerausfall-, Browser-, Mikrofon-, Android- oder iPhone-Abnahmen. HTTP Basic Auth und der fehlende explizit invalidierbare Lock-/Logout-Zustand bleiben ebenfalls offen. Release bleibt NO-GO.
