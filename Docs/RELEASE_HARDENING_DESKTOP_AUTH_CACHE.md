# Release-Härtung: Desktop-Auth-Cache

Stand: 2026-08-29
Status: umgesetzt, Release weiterhin NO-GO

## Befund

Der Desktop-PIN-Gate schützt den Zugriff, aber erfolgreiche UI- und API-Antworten waren nicht zentral gegen Browser- oder Proxy-Cache abgesichert. Bei Memo-, Profil- und Statusdaten ist das ein unnötiges Datenschutz- und Release-Risiko.

## Vertrag

`SecureHandler.end_headers()` setzt für jede Desktop-Antwort zentral:

- `Cache-Control: no-store, no-cache, must-revalidate, max-age=0`
- `Pragma: no-cache`
- `Expires: 0`
- `Vary: Authorization`

Damit gilt derselbe Schutz für 401, 429, statische UI-Dateien und authentifizierte API-Antworten.

## Regression

`tests/security/test_desktop_pin_gate.py` prüft den Vertrag im echten Loopback-Server für Auth-Challenge, Lockout, erfolgreiche UI und `/api/state`.

## Grenze

Diese Änderung implementiert bewusst keinen Logout. HTTP Basic Auth wird vom Browser automatisch erneut gesendet; ein belastbarer expliziter Logout benötigt einen separaten Session-/Lock-Vertrag und darf nicht als scheinbar funktionierende Cache-Löschung simuliert werden.
