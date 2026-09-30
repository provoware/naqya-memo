# Desktop Auth Cache – Credential-Fingerprint

Status: Release-Freeze-Härtung, kein neues Produktfeature.

## Befund

Der Desktop-Auth-Cache war bereits an Profilrevision und Profil-Inkarnation (`created_at`) gebunden. Damit werden normale PIN-Änderungen und ersetzte Profile zuverlässig erkannt, sofern sich einer dieser Zustandswerte ändert.

Ein verbleibender Defense-in-Depth-Randfall bestand darin, dass ein extern reparierter oder ersetzter Profildatensatz theoretisch dieselbe Profil-ID, dieselbe Revision und denselben Zeitstempel weiterverwenden könnte, während sich nur das eigentliche Credential-Material (`pin_hash`) ändert. Ein alter Cacheeintrag darf in diesem Fall nicht weiter als vertrauenswürdig gelten.

## Vertrag

Der offizielle Produktions-Entry-Point `app/secure_response_server.py` liest den Auth-Sicherheitszustand weiterhin über eine kurze isolierte read-only SQLite-Verbindung. Der Cache-Epoch wird nun aus drei bereits vorhandenen Feldern gebildet:

- aktive Profil-`revision`
- Profil-`created_at`
- aktueller `pin_hash`

Die drei Werte werden in einem einzelnen SQLite-Snapshot gelesen und als SHA-256-basierter opaker Integer-Epoch an den bestehenden unteren Auth-Layer weitergegeben. Leere, fehlende oder nicht lesbare Werte bleiben fail-closed.

Damit wird ein Cacheeintrag auch dann sofort ungültig, wenn nur das Credential-Material wechselt und Profil-ID, Revision und `created_at` unverändert bleiben. Es wird weder ein neues Schemafeld noch ein neuer Session-, Logout- oder UI-Mechanismus eingeführt.

## Regression

`tests/security/test_desktop_auth_cache_credential_fingerprint.py` startet den echten gehärteten Loopback-Server und beweist fünf Punkte:

1. die Erststart-PIN authentifiziert und füllt den Auth-Cache,
2. der unveränderte Credential-Fingerprint erlaubt den normalen Cachetreffer,
3. die Test-Fixture ersetzt ausschließlich `pin_hash`, während Revision und `created_at` exakt gleich bleiben,
4. die zuvor gecachte alte PIN wird unmittelbar mit HTTP 401 abgewiesen,
5. die neue PIN authentifiziert unter dem neuen Cache-Epoch normal.

CI-Schritt: `Desktop auth cache credential fingerprint invalidation`.

Maschinenlesbare Evidence: `registry/evidence/security/DESKTOP_AUTH_CACHE_CREDENTIAL_FINGERPRINT_ACCEPTANCE.json`.

## Wirkung

Die Cache-Gültigkeit hängt nicht mehr nur von administrativen Zustandsmarkern ab, sondern zusätzlich vom tatsächlich aktiven Credential-Material. Das reduziert das Risiko einer Vertrauensvererbung nach manueller DB-Reparatur, Restore-Randfällen oder Profilersatz und macht die Auth-Invalidierung robuster gegen zukünftige Regressionsfehler in der Revisionspflege.

## Release-Grenze

HTTP Basic Auth bleibt unverändert bestehen. Es gibt weiterhin keinen expliziten serverseitigen Lock-/Logout-Zustand, der bereits authentifizierte Browserzustände garantiert invalidiert. Reale Browser-, Mikrofon-, Android- und iPhone-Gates bleiben offen; der Release-Status bleibt NO-GO.
