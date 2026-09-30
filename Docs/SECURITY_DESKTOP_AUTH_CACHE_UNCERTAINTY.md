# Desktop Auth Cache – Unsicherheits-Eviction

Status: Release-Freeze-Härtung, kein neues Produktfeature.

## Befund

Der Desktop-Auth-Cache war bereits an Profilrevision und Profil-Inkarnation gebunden. Wenn der Sicherheitszustand kurzfristig nicht gelesen werden konnte, wurde die konkrete Anfrage zwar fail-closed abgewiesen. Die bereits im Speicher liegenden Cacheeinträge blieben jedoch erhalten. Sobald derselbe Security-Epoch später wieder lesbar war, konnten diese alten Cacheeinträge erneut als gültig erscheinen.

Dieses Verhalten widerspricht einem strikten Fail-Closed-Vertrag: Ein unbekannter globaler Sicherheitszustand darf keinen zuvor vertrauenswürdigen Auth-Zustand konservieren.

## Release-Freeze-Optimierung

`app/secure_server.py` verwirft jetzt bei einem nicht beweisbaren Profil-Sicherheitszustand (`_profile_revision() is None`) den vollständigen Auth-Cache unter dem bestehenden Auth-Lock.

Damit gilt:

- unbekannter Security-State -> aktuelle Anfrage wird abgewiesen,
- gleichzeitig werden sämtliche zuvor gecachten Authorization-Digests entfernt,
- eine spätere Erholung derselben DB-/Profil-Epoche belebt keine alten Cacheeinträge wieder,
- erneutes Caching ist erst nach einer neuen erfolgreichen Authentifizierung möglich.

PIN-Verifikation, Rate-Limit, Datenmodell, UI und Produktfunktionen bleiben unverändert.

## Regression

`tests/security/test_desktop_auth_cache_uncertainty_eviction.py` beweist sechs Verträge:

1. mehrere Zugangsdaten können bei bewiesenem Security-State normal gecacht werden,
2. beide Digests liegen tatsächlich im Cache,
3. unbekannter Security-State schlägt fail-closed fehl,
4. die Unsicherheit leert den gesamten Auth-Cache,
5. nach Wiederkehr desselben Epochs lebt kein alter Cacheeintrag wieder auf,
6. erneutes Caching funktioniert erst nach einem expliziten neuen erfolgreichen Remember-Schritt.

CI-Schritt: `Desktop auth cache uncertainty eviction`.

## Release-Grenze

Dieser Slice ersetzt HTTP Basic Auth nicht und führt keinen Lock-/Logout-Workflow ein. Reale Browser-, Mikrofon-, Android- und iPhone-Gates bleiben offen. Der Release-Status bleibt NO-GO.
