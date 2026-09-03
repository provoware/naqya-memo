# Desktop-Uploadlimit – fail-safe Konfigurationsprüfung

## Befund

Der bestehende Datei-Upload liest `PROVOWARE_UPLOAD_MAX_BYTES` im Basisserver mit `int(...)`. Ein leerer oder nichtnumerischer Wert konnte deshalb erst beim tatsächlichen Dateiimport einen Fehler auslösen. Null und negative Werte waren ebenfalls keine sinnvolle Konfiguration.

## Release-Freeze-Optimierung

Der offizielle gehärtete Desktop-Entry-Point normalisiert den vorhandenen Upload-Grenzwert vor dem Import des Basisservers:

- fehlt der Wert: etablierter Default `536870912` Byte (512 MiB),
- leer oder nichtnumerisch: derselbe Default,
- null oder negativ: derselbe Default,
- gültige positive Ganzzahl: bleibt unverändert.

Damit wird keine neue Produktfunktion eingeführt und kein gültig konfiguriertes positives Uploadlimit still verändert.

## Automatische Regression

`tests/security/test_desktop_upload_config_parse.py` prüft sechs Verträge in getrennten Prozessen und bestätigt zusätzlich, dass der normalisierte Wert über die Umgebungsvariable beim Basis-Uploadhandler ankommt.

## Evidence-Grenze

Dieser Test beweist ausschließlich die robuste Verarbeitung der bestehenden Uploadlimit-Konfiguration im offiziellen Desktop-Produktionspfad. Er ersetzt weder einen realen großen Dateiimport noch Browser-, Datenträger-, Android- oder iPhone-Abnahmen. Der Release-Status bleibt deshalb unverändert NO-GO, solange die übrigen realen Gates offen sind.
