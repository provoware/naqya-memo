# Desktop Response Security Headers

Status: **P0 Release-Härtung – implementiert, Release bleibt NO-GO**

## Befund

Der Desktoppfad besaß bereits PIN-Gate, Fehlversuchsbegrenzung, No-Store und Loopback-/Origin-Prüfung. Ein zentraler Browser-Antwortvertrag gegen Einbettung/Clickjacking und Referrer-Leaks fehlte jedoch.

## Umsetzung

Der offizielle Linux-Startpfad läuft über `app/secure_response_server.py`. Diese schmale Schicht übernimmt sämtliche vorhandenen Schutzregeln aus `secure_server.py` und ergänzt für jede Antwort:

- `X-Frame-Options: DENY`
- `Content-Security-Policy: frame-ancestors 'none'; base-uri 'none'; object-src 'none'`
- `Referrer-Policy: no-referrer`
- `X-Content-Type-Options: nosniff`

Der bestehende Cache-Vertrag (`no-store`) bleibt unverändert aktiv.

Die CSP ist absichtlich eng auf browserseitige Container-/Navigationsrisiken begrenzt und verändert weder Script-, Style-, Media- noch API-Ladequellen. Dadurch wird das Risiko einer UI-Regression im Release-Freeze minimiert.

## Regression / Evidence

`tests/security/test_desktop_response_headers.py` startet den echten Loopback-Server und beweist:

1. 401-Auth-Challenge enthält den vollständigen Headervertrag.
2. Authentifizierte API-Antwort enthält den vollständigen Headervertrag.
3. Authentifizierte UI-Antwort enthält den vollständigen Headervertrag.
4. Beide offiziellen Linux-Starter verwenden ausschließlich den gehärteten Entry-Point.

Der Test ist Bestandteil von `.github/workflows/quality.yml`.

## Release-Grenze

Diese Änderung schließt nur den Response-Header-Vertrag. Sie ersetzt ausdrücklich keine realen Browser-, Mikrofon-, Android- oder iPhone-Gates und führt zu keiner Release-Gate-Promotion.
