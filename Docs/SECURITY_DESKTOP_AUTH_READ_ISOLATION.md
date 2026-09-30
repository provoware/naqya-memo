# Desktop Auth Security Read Isolation

Status: Release-Freeze-Härtung, kein neues Produktfeature.

## Befund

Der Desktop-Produktserver verwendet eine gemeinsame SQLite-Verbindung mit `check_same_thread=False`. Der PIN-/Auth-Pfad las die aktive Profilrevision bislang über genau diese mutable Produktverbindung. Da der HTTP-Server Requests parallel in Threads verarbeitet, koppelte die Sicherheitsvorprüfung damit Authentifizierung und Produktmutationen unnötig an dieselbe Connection.

## Vertrag

Der offizielle Produktions-Entry-Point `app/secure_response_server.py` ersetzt ausschließlich den Read-Pfad für die Profilrevision durch eine kurze unabhängige SQLite-Verbindung mit:

- `mode=ro`
- `PRAGMA query_only=ON`
- 2 Sekunden SQLite-Timeout
- Abfrage nur des aktiven `PROFILE_ID` und seiner `revision`
- fail-closed (`None`) bei Datenbank-, I/O- oder Konvertierungsfehlern

Die bestehende PIN-Prüfung, Rate-Limits, Cache-TTLs, UI und Produktdatenmodelle bleiben unverändert.

## Regression

`tests/security/test_desktop_auth_read_connection.py` beweist fünf Punkte:

1. committed Profilrevision ist lesbar,
2. der Auth-Read funktioniert auch dann, wenn die gemeinsame Produktverbindung absichtlich unbenutzbar gemacht wird,
3. ein inaktives Profil wird fail-closed abgewiesen,
4. eine reaktivierte committed Profilrevision wird unmittelbar sichtbar,
5. fehlende/unlesbare Security-State-DB liefert fail-closed `None`.

CI-Schritt: `Desktop auth security read isolation`.

## Release-Grenze

Dieser Slice ersetzt HTTP Basic Auth nicht und führt keinen Logout-/Lock-Mechanismus ein. Reale Browser-, Mikrofon-, Android- und iPhone-Gates bleiben unverändert offen. Der Release-Status wird durch diese isolierte Härtung nicht auf GO gesetzt.
