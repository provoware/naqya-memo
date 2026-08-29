# FAILURE MATRIX — V0.2 PLAN / V0.3 EXECUTION

| ID | Fehlerpunkt | Erwartung |
|---|---|---|
| F01 | vor Transaktion | keine Änderung |
| F02 | nach BEGIN | automatischer Rollback |
| F03 | während Entity-Write | keine Teilrevision |
| F04 | vor COMMIT | Rollback |
| F05 | unmittelbar nach COMMIT | Daten beim Neustart konsistent |
| F06 | während Temp-Asset-Write | Temp isoliert, kein Final-Asset |
| F07 | vor Asset-Rename | alter Zustand gültig |
| F08 | Disk full | verständlicher Fehler, kein Datenverlust |
| F09 | Read-only | keine Mutation |
| F10 | Permission denied | keine Mutation |
| F11 | DB locked | Retry/Queue, kein Doppelwrite |
| F12 | Prozess-Kill | Recovery erkennt letzten Zustand |
| F13 | beschädigter Entity-Checksum | Quarantäne/Fehler, nicht still lesen |
| F14 | beschädigtes Backup | Generation nicht VERIFIED |
| F15 | Revision conflict | kein Überschreiben |
| F16 | Systemzeit springt | Dauer via monotonic stabil |
