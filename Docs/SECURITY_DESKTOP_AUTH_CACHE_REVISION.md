# Desktop-Auth-Cache an Profilrevision binden

## Befund
Der Desktop-PIN-Gate cacht bereits erfolgreich geprüfte HTTP-Basic-Zugangsdaten standardmäßig bis zu 300 Sekunden. Bisher war dieser Cacheeintrag nur an den Authorization-Digest und die Ablaufzeit gebunden. Wenn sich die Profil-PIN in dieser Zeit änderte, konnte der alte bereits gecachte Authorization-Wert bis zum TTL-Ablauf weiter akzeptiert werden.

## Release-Freeze-Optimierung
Der Cacheeintrag enthält jetzt zusätzlich die aktuelle `profiles.revision` des aktiven Profils.

Vor jeder Cache-Nutzung wird die aktuelle Profilrevision gelesen. Ein Cachetreffer gilt nur noch, wenn:

1. die TTL noch nicht abgelaufen ist und
2. die gespeicherte Profilrevision exakt der aktuellen Revision entspricht.

Bei Datenbank-/Revisionsfehlern wird fail-closed kein Cachetreffer akzeptiert. Bei einer neuen erfolgreichen PIN-Prüfung wird außerdem geprüft, dass sich die Profilrevision während der Authentifizierung nicht verändert hat, bevor der Credential-Digest erneut gecacht wird.

## Sicherheitswirkung
Eine PIN-Änderung erhöht bereits im bestehenden Core die Profilrevision. Damit verliert ein zuvor gecachter alter PIN-Zugang unmittelbar seine Gültigkeit und wartet nicht mehr auf das Ende der Auth-Cache-TTL.

## Regression
`tests/security/test_desktop_auth_cache_revision.py` startet den echten gehärteten Loopback-Server und beweist sechs Verträge:

1. Erst-PIN authentifiziert und füllt den Cache.
2. Unveränderte Revision erlaubt den erwarteten Cachetreffer.
3. PIN-Ersetzung erhöht die Profilrevision.
4. Die alte gecachte PIN wird unmittelbar danach mit HTTP 401 abgewiesen.
5. Die neue PIN funktioniert unmittelbar.
6. Die neue PIN kann unter der neuen Revision wieder sicher gecacht werden.

## Bewusste Grenze
Diese Änderung führt keinen neuen Logout-/Lock-Mechanismus und keine neue Session-Architektur ein. HTTP Basic Auth bleibt der größere offene Architekturpunkt. Reale Browser-, Mikrofon-, Android- und iPhone-Abnahmen bleiben unverändert offen; der Release-Status wird durch diesen Source-/Loopback-Vertrag nicht hochgestuft.
