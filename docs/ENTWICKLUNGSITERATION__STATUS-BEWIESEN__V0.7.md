# ENTWICKLUNGSITERATION V0.7

**Ziel:** die V0.6-Shell kontrolliert an vorhandene Services anbinden.

## Patchbereiche
- lokaler Application-API-Server
- sichere Linux-Startskripte
- Memo-/Todo-/Kalender-UI
- Header-Schnelleingabe
- nächste 10 Live-Daten
- Undo/Redo/Papierkorb
- Reminder/Share/Standardeditor-Adapter
- API-E2E und UI-Contract-Tests

## Wirkung
Erstmals bedienbare Fachfunktionen, ohne die Architekturgrenze UI → Service → Domain → Persistence zu verletzen.

## Acceptance
- 51/51 automatisierte Tests grün.
- Loopback-API-E2E grün.
- Headless-Chromium-Screenshot in dieser Containerumgebung durch DBus/Browser-Timeout blockiert; bewusst nicht als PASS gewertet.
