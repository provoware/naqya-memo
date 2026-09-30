# Desktop Auth Cache – Profil-Inkarnation

Status: Release-Freeze-Härtung, kein neues Produktfeature.

## Befund

Der Desktop-Auth-Cache war bereits an die Profil-`revision` gebunden. Das invalidiert alte Zugangsdaten bei normalen PIN-/Profiländerungen. Ein seltener, aber sicherheitsrelevanter Restfall blieb jedoch offen: Wird ein Profil ersetzt und dabei dieselbe Profil-ID sowie dieselbe Revisionsnummer wiederverwendet, kann die Revision allein die alte und die neue Profil-Inkarnation nicht unterscheiden.

Das Profilschema besitzt bereits `created_at`. Dieser bestehende Wert kann zusammen mit `revision` als Inkarnationsmerkmal genutzt werden, ohne das Datenmodell zu ändern.

## Vertrag

Der offizielle Produktions-Entry-Point `app/secure_response_server.py` liest den Auth-Sicherheitszustand weiterhin über die isolierte read-only SQLite-Verbindung. Für die Cache-Gültigkeit wird nun ein opaker SHA-256-basierter Integer-Epoch aus:

- aktiver Profil-`revision`
- Profil-`created_at`

erzeugt.

Der untere Auth-Layer behält seinen bestehenden Integer-/Equality-Vertrag. Ändert sich Revision **oder** Profil-Inkarnation, ist ein vorhandener Cacheeintrag ungültig. Leere, fehlende oder nicht konvertierbare Security-State-Werte verhalten sich fail-closed.

## Regression

`tests/security/test_desktop_auth_cache_profile_incarnation.py` beweist fünf Punkte:

1. die ursprüngliche PIN authentifiziert und füllt den Cache,
2. derselbe Cache gilt bei unveränderter Profil-Inkarnation,
3. eine Ersatzprofil-Fixture kann ID und Revision beibehalten, während `created_at` und PIN wechseln,
4. die gecachte Vorgänger-PIN wird danach sofort mit HTTP 401 abgewiesen,
5. die PIN der neuen Profil-Inkarnation authentifiziert unmittelbar.

CI-Schritt: `Desktop auth cache profile incarnation invalidation`.

## Release-Grenze

Dieser Slice ersetzt HTTP Basic Auth nicht und führt keinen Logout-/Lock-Mechanismus ein. Reale Browser-, Mikrofon-, Android- und iPhone-Gates bleiben unverändert offen. Der Release-Status bleibt NO-GO, bis die entsprechenden Release-Gates separat bewiesen sind.
