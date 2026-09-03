# Bestehende Projekt-DB – fail-closed Start-Preflight

Status: Release-Freeze-Härtung, kein neues Produktfeature.

## Befund

Der offizielle Desktop-Entry-Point importiert anschließend `secure_server` und den Basisserver. Diese unteren Module dürfen beim Erststart Schema und Bootstrap-Daten anlegen. Eine bereits vorhandene, aber beschädigte, unlesbare oder als falscher Pfadtyp vorliegende `daten/core.sqlite3` darf deshalb nicht still wie eine fehlende Datenbank behandelt werden.

Der gehärtete Preflight prüfte bereits read-only `PRAGMA schema_version` und `PRAGMA quick_check`. Damit wird SQLite-Dateiintegrität deutlich besser belegt. Ein noch offener Klassifikationsfehler blieb jedoch: Eine technisch vollkommen gesunde SQLite-Datei kann zu einer anderen Anwendung gehören oder nur ein unvollständiges `profiles`-Schema enthalten. Der untere Server interpretiert fehlende aktive Profildaten als Bootstrap-Situation und könnte eine solche Bestandsdatei anschließend verändern.

## Release-Freeze-Optimierung

`app/secure_response_server.py` prüft jetzt **vor dem Import** des mutierenden Serverpfads:

- fehlt `daten/core.sqlite3`, bleibt der normale Erststart erlaubt,
- existiert der Pfad, muss er eine regulär lesbare Datei sein,
- die Datei wird ausschließlich read-only mit `mode=ro` und `PRAGMA query_only=ON` geöffnet,
- `PRAGMA schema_version` muss lesbar sein,
- `PRAGMA quick_check` muss ausschließlich `ok` liefern,
- anschließend muss die bestehende Datei als PROVOWARE-Core-DB erkennbar sein,
- dafür muss die Tabelle `profiles` existieren und mindestens die bereits produktiv benötigten Spalten `id`, `display_name`, `pin_hash`, `created_at`, `updated_at`, `revision` und `status` besitzen,
- fremde oder unvollständige, aber technisch gesunde SQLite-Dateien -> `EXISTING_PROJECT_DB_PREFLIGHT_CONTRACT_MISMATCH`,
- beschädigte/unlesbare SQLite-Datei -> `EXISTING_PROJECT_DB_PREFLIGHT_UNREADABLE`,
- strukturell inkonsistente SQLite-Datei -> `EXISTING_PROJECT_DB_PREFLIGHT_INTEGRITY_FAILED`,
- falscher Pfadtyp -> `EXISTING_PROJECT_DB_PREFLIGHT_UNSAFE`.

Die Prüfung erzeugt kein Schema, führt keine Migration aus und schreibt keine Daten. Sie dient nur dazu, eine vorhandene Datei vor dem mutierenden Produktimport eindeutig als bekannten Projektvertrag zu klassifizieren.

## Regression

`tests/security/test_existing_db_preflight_fail_closed.py` beweist vierzehn Verträge:

1. eine komplett unlesbare vorhandene SQLite-Datei stoppt den offiziellen Produktionsstart vor dem Bootstrap,
2. ihre Bytes bleiben exakt unverändert,
3. nach dem Fehler entsteht keine Erststart-PIN-Datei,
4. ein Verzeichnis am erwarteten DB-Dateipfad wird fail-closed abgewiesen,
5. auch dieser falsche Pfadtyp löst keine Bootstrap-Credentialmutation aus,
6. eine speziell erzeugte strukturell beschädigte SQLite-Datei bleibt auf `schema_version`-Ebene lesbar,
7. `quick_check` erkennt diesen tieferen Schaden und stoppt mit `EXISTING_PROJECT_DB_PREFLIGHT_INTEGRITY_FAILED`,
8. auch diese Datei bleibt bytegenau unverändert,
9. auch der Integritätsfehler erzeugt keine Erststart-PIN-Datei,
10. eine technisch gesunde fremde SQLite-Datei wird als Nicht-PROVOWARE-Vertrag erkannt,
11. auch diese fremde Datei bleibt bytegenau unverändert,
12. auch der Vertragsfehler erzeugt keine Erststart-PIN-Datei,
13. eine vorhandene `profiles`-Tabelle mit unvollständigem produktiv benötigtem Spaltensatz wird fail-closed abgewiesen,
14. auch dieser Teilvertrag löst keine Bootstrap-Credentialmutation aus.

Erwartete Zusammenfassung: `SUMMARY total=14 passed=14 failed=0`.

## Wirkung

Der Produktionsstart beweist jetzt drei getrennte Eigenschaften, bevor Bestandsdaten in einen potenziell mutierenden Pfad gelangen: **lesbar**, **strukturell konsistent** und **als PROVOWARE-Projektvertrag erkennbar**. Damit kann eine fremde, leere oder nur teilweise passende SQLite-Datei nicht mehr allein aufgrund technischer SQLite-Gesundheit als legitime Bootstrap-Basis behandelt werden.

## Release-Grenze

Der Check ersetzt keine vollständige Schema-Migrationsprüfung und keinen vollständigen Offline-`integrity_check`. Falls künftig ältere unterstützte Datenbankverträge automatisch migriert werden sollen, muss dafür ein expliziter versionsgebundener Migrationsvertrag vor diesem Gate definiert werden. Backup-/Recovery-, Datenträgerausfall-, Disk-full-, Browser-, Mikrofon-, Android- und iPhone-Abnahmen bleiben offen. HTTP Basic Auth und der fehlende explizit invalidierbare Lock-/Logout-Zustand bleiben ebenfalls offen. Release bleibt NO-GO.
