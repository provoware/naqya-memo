# Desktop-Auth-Konfiguration – fail-safe Parsing

## Befund

Der offizielle Desktop-Startpfad hatte bereits robustes Parsing für JSON-Größe und Request-I/O-Timeout. Vier vorhandene Authentifizierungsgrenzen wurden im darunterliegenden Auth-Modul jedoch noch direkt mit `int(...)` aus Umgebungsvariablen gelesen. Ein leerer oder nichtnumerischer Wert konnte deshalb den Desktopstart vor der Oberfläche abbrechen.

## Release-Freeze-Optimierung

`app/secure_response_server.py` normalisiert die vier bereits vorhandenen Auth-Werte jetzt vor dem Import von `secure_server`:

- `PROVOWARE_AUTH_CACHE_TTL`: Default 300 s, erlaubt 5–3600 s
- `PROVOWARE_AUTH_MAX_FAILURES`: Default 5, erlaubt 3–20
- `PROVOWARE_AUTH_FAILURE_WINDOW`: Default 120 s, erlaubt 5–3600 s
- `PROVOWARE_AUTH_LOCKOUT_SECONDS`: Default 30 s, erlaubt 1–3600 s

Fehlende, leere oder nichtnumerische Werte verwenden den dokumentierten Default. Numerische Werte außerhalb des Sicherheitsbereichs werden auf die jeweilige Grenze begrenzt. Gültige Werte innerhalb des Bereichs bleiben unverändert.

## Warum vor dem Import?

`secure_server.py` liest diese Werte beim Modulimport. Der offizielle Produktions-Entry-Point normalisiert deshalb zuerst die Umgebung und importiert erst danach die Auth-Schicht. So bleibt die Änderung klein und beeinflusst weder Auth-Logik noch UI oder Datenmodell.

## Regression

`tests/security/test_desktop_auth_config_parse.py` prüft sechs Verträge in isolierten temporären Projektordnern:

1. fehlende Werte → sichere Defaults,
2. nichtnumerische Werte → sichere Defaults statt Startabbruch,
3. leere Werte → sichere Defaults,
4. zu kleine Zahlen → untere Sicherheitsgrenze,
5. zu große Zahlen → obere Sicherheitsgrenze,
6. gültige Werte → unverändert.

Der Test ist als eigener Schritt `Desktop auth security config parsing` in der Quality-CI registriert.

## Release-Grenze

Diese Änderung führt keine Produktfunktion ein und ersetzt nicht die geplante Session-/Lock-Architektur. Reale Browser-, Mikrofon-, Android- und iPhone-Abnahmen bleiben unverändert offen. Der Release-Status wird durch diesen Source-/Runtime-Vertrag nicht automatisch auf GO gesetzt.
