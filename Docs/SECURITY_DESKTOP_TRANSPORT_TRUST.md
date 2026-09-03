# Desktop Transport Trust – Release-Härtung

## Befund
Der lokale Desktop-HTTP-Dienst war bereits durch PIN, Rate-Limit und No-Store geschützt. Vor der Authentifizierung fehlte jedoch eine explizite Prüfung, ob der Browser wirklich den erwarteten Loopback-Host und eine lokale Same-Origin-Anfrage verwendet. Dadurch blieb eine unnötige Angriffsfläche für DNS-Rebinding und fremde Cross-Site-Anfragen.

## Sicherheitsvertrag
Der gehärtete `SecureHandler` akzeptiert ausschließlich `127.0.0.1:<aktueller Port>` und `localhost:<aktueller Port>` als `Host`. Ein vorhandener `Origin` muss zu genau einem dieser lokalen HTTP-Ursprünge gehören. `Sec-Fetch-Site: cross-site` wird fail-closed abgewiesen. Die Prüfung erfolgt vor PIN-/Rate-Limit-Verarbeitung.

## Fehlerverhalten
- fremder `Host` → HTTP 421 / `LOCAL_HOST_BLOCKED`
- fremder `Origin` → HTTP 403 / `CROSS_SITE_ORIGIN_BLOCKED`
- `Sec-Fetch-Site: cross-site` → HTTP 403 / `CROSS_SITE_REQUEST_BLOCKED`
- Direktnavigation ohne `Origin` bleibt erlaubt und fällt anschließend normal in das PIN-Gate
- lokale Same-Origin-Anfragen bleiben kompatibel

Alle Blockantworten übernehmen den zentralen No-Store-Vertrag.

## Regression / Evidence
`tests/security/test_desktop_transport_trust.py` beweist fünf Laufzeitverträge auf einem echten Loopback-Port. GitHub Actions führt den Test im `quality/source-contracts`-Job aus. Maschinenlesbare Evidence: `registry/evidence/security/DESKTOP_TRANSPORT_TRUST_ACCEPTANCE.json`.

## Release-Grenze
Diese Härtung ist keine neue Produktfunktion und stuft kein reales Release-Gate hoch. Browser-/Mikrofon-/Android-/iPhone-Evidence bleibt separat. Der Release bleibt NO-GO.
