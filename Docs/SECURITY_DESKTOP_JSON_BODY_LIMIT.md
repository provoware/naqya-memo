# Desktop JSON Request Body Limit

Status: Release-Freeze-Härtung, keine neue Produktfunktion.

## Befund

Der Produktionshandler liest bei gewöhnlichen JSON-POSTs den durch `Content-Length` angekündigten Body vollständig in den Arbeitsspeicher. Für Datei-Uploads existiert bereits ein eigener Größen- und Streamingvertrag, für normale Memo-/Todo-/Kalender-/Einstellungs-Mutationen fehlte diese Grenze.

## Vertrag

Der offizielle Desktop-Entry-Point `app/secure_response_server.py` prüft normale POST-Anfragen vor Übergabe an den Produkthandler.

- Standardlimit: 1 MiB pro gewöhnlichem JSON-POST.
- Konfigurierbar über `PROVOWARE_JSON_POST_MAX_BYTES`.
- Harte Konfigurationsgrenzen: mindestens 4 KiB, höchstens 16 MiB.
- Überschreitung: HTTP 413 / `REQUEST_BODY_TOO_LARGE`.
- Ungültige oder negative `Content-Length`: HTTP 400 / `REQUEST_CONTENT_LENGTH_INVALID`.
- `/api/assets/upload` bleibt ausdrücklich ausgenommen und verwendet weiterhin den bestehenden separaten Upload-/Streamingvertrag.
- Ablehnungsantworten erben Cache-, Frame-, CSP-, Referrer- und `nosniff`-Schutz des gehärteten Response-Pfads.

## Regression / Evidence

`tests/security/test_desktop_json_body_limit.py` startet den echten Loopback-Produktionsserver und beweist:

1. authentifizierter Ausgangszustand ist erreichbar,
2. übergroße JSON-Mutation wird mit 413 abgewiesen,
3. die abgewiesene Anfrage erzeugt keine Memo-Mutation,
4. eine normale Anfrage unterhalb der Grenze funktioniert weiter,
5. der Server bleibt nach der 413-Antwort gesund und persistiert nur die gültige Mutation.

GitHub Actions führt diesen Test als `Desktop JSON request body limit` im bestehenden `quality / source-contracts`-Job aus.

## Release-Grenze

Dieser Vertrag ersetzt keine realen Browser-, Mikrofon-, Android- oder iPhone-Abnahmen und hebt kein Release-Gate auf GO. Der Release-Status bleibt NO-GO, bis die dafür vorgesehenen realen Gates Evidence besitzen.
