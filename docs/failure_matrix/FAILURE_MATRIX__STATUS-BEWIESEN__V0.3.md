# FAILURE MATRIX — V0.3 ACCEPTANCE

| ID | Fehlerfall | Ergebnis |
|---|---|---|
| F01 | Kill vor BEGIN | 🟢 PASS |
| F02 | Kill nach BEGIN | 🟢 PASS |
| F03 | Kill nach Write/vor Commit | 🟢 PASS |
| F04 | Kill nach Commit | 🟢 PASS |
| F05 | Restore in frischen Projektordner | 🟢 PASS |
| F06 | DB locked | 🟢 PASS |
| F07 | Entity-Checksum manipuliert | 🟢 PASS |
| F08 | Backup beschädigt | 🟢 PASS |
| F09 | Read-only Preflight | 🟢 PASS |
| F10 | Permission denied Klassifikation | 🟢 PASS |
| F11 | Disk full Klassifikation | 🟢 PASS |
| F12 | Mutation Queue Reihenfolge | 🟢 PASS |
| F13 | zweite Projektinstanz/Lock | 🟢 PASS |
| F14 | Undo/Redo Semantik | 🟢 PASS |

## Einschränkung
Echte OS-native Disk-full/Permission/Read-only-Injektion bleibt Plattform-Gate. Die V0.3-Referenz beweist die Recovery-Semantik und Fehlerklassifikation.
