# Desktop Security Configuration Parsing

## Befund

Die vorhandenen Desktop-Härtungsparameter `PROVOWARE_JSON_POST_MAX_BYTES` und `PROVOWARE_REQUEST_IO_TIMEOUT_SECONDS` wurden beim Modulimport direkt mit `int(...)` ausgewertet. Ein leerer, falsch formatierter oder nichtnumerischer Umgebungswert konnte dadurch den offiziellen Desktop-Start vollständig abbrechen, bevor die Oberfläche erreichbar war.

## Release-Freeze-Optimierung

`app/secure_response_server.py` verwendet nun genau eine kleine Hilfsfunktion für sicherheitsrelevante Ganzzahl-Konfigurationen:

- fehlender Wert -> dokumentierter sicherer Standardwert
- leerer/Whitespace-Wert -> sicherer Standardwert
- nichtnumerischer Wert -> sicherer Standardwert
- numerischer Wert unter Minimum -> auf Minimum begrenzt
- numerischer Wert über Maximum -> auf Maximum begrenzt
- gültiger Wert innerhalb des Bereichs -> unverändert übernommen

Bestehende Sicherheitsgrenzen bleiben unverändert:

- JSON-POST-Limit: Standard 1 MiB, zulässig 4 KiB bis 16 MiB
- Request-I/O-Timeout: Standard 30 s, zulässig 1 bis 120 s

Es wurden keine Produktfunktionen, Datenmodelle, Authentifizierungsabläufe oder Release-Gates erweitert.

## Regression

`tests/security/test_desktop_security_config_parse.py` prüft sechs Verträge in frischen temporären Projekten:

1. fehlende Werte verwenden die Standards,
2. nichtnumerische Werte verhindern den Start nicht,
3. leere Werte verwenden die Standards,
4. zu kleine numerische Werte werden nach oben begrenzt,
5. zu große numerische Werte werden nach unten begrenzt,
6. gültige Werte bleiben erhalten.

Der Test ist als eigener Schritt in `.github/workflows/quality.yml` verankert.

## Release-Grenze

Diese Evidence belegt ausschließlich robustes Parsing der bestehenden Desktop-Sicherheitskonfiguration. Sie ersetzt keine reale Browser-, Mikrofon-, Android- oder iPhone-Abnahme. Der Release-Status wird dadurch nicht automatisch hochgestuft.
