# Desktop-PIN-Gate – Release-Härtung

Status: **NO-GO bleibt bestehen**. Diese Iteration schließt ausschließlich den fehlenden Authentifizierungs-Gate im offiziellen Linux-Desktop-Startpfad.

## Befund

Der bisherige `app/server.py` wählt beim Start direkt das erste aktive Profil oder erzeugt `Standardprofil` mit PIN `0000`. Danach werden `PROFILE_ID` und alle API-Routen ohne vorherige PIN-Prüfung verwendet.

## Umsetzung

- Neuer Produktionswrapper `app/secure_server.py`.
- `STARTEN_LINUX.sh` und `STARTEN_OHNE_BROWSER.sh` starten ausschließlich diesen Wrapper.
- Vor UI-, Asset- und API-Zugriff ist HTTP-Basic-Authentifizierung erforderlich.
- Benutzername: `provoware`; Passwort: bestehende Profil-PIN.
- PIN-Prüfung nutzt `ProfileService.verify_access()` und damit den vorhandenen Hash-/Access-Log-Vertrag.
- Zur Entlastung bei CSS/JS/Asset-Requests wird nur ein SHA-256-Digest des Authorization-Headers kurzzeitig im RAM gecacht; PIN und Header werden nicht persistiert.
- Fehlende, ungültige oder falsche Zugangsdaten werden fail-closed mit HTTP 401 beantwortet.

## Automatische Evidence

`tests/security/test_desktop_pin_gate.py` beweist mit echtem Loopback-HTTP-Server:

1. UI ohne Authentifizierung → 401.
2. falsche PIN → 401.
3. korrekte Profil-PIN → 200.
4. authentifizierter `/api/state`-Zugriff → 200.
5. beide offiziellen Linux-Starter verwenden ausschließlich `app/secure_server.py`.

Der Test ist als Required-Source-Regression in `.github/workflows/quality.yml` aufgenommen.

## Verbleibende Risiken

- Ein neu erzeugtes Referenzprofil nutzt weiterhin den bekannten Erst-PIN `0000`; dessen sichere Erstinitialisierung ist ein eigener späterer Härtungspunkt.
- HTTP Basic Auth bietet keinen komfortablen expliziten Browser-Logout. Der Server bleibt ausschließlich an `127.0.0.1` gebunden; ein späterer Session-/Lock-UX-Vertrag kann darauf aufbauen.
- Diese Änderung erhöht keinen realen Plattform-Release-Gate-Zähler.

## Nächster logischer Schritt

Reminder-Scheduler oder Next-10 erst nach Abschluss der noch offenen sicherheitsrelevanten Release-Härtung. Priorisiert sollte als nächstes die sichere Erst-PIN-Initialisierung beziehungsweise ein expliziter Lock/Unlock-Vertrag geprüft werden.
