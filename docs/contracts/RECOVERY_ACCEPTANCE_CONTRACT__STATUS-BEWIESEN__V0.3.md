# RECOVERY ACCEPTANCE CONTRACT — V0.3

## Grüne Bedingungen
- Kill vor BEGIN → keine Änderung.
- Kill nach BEGIN → Rollback.
- Kill nach Write/vor COMMIT → Rollback.
- Kill nach COMMIT → Änderung bleibt konsistent.
- frischer Restore → Hash + Dateninhalt + SQLite-Integrity identisch.
- DB locked → kein Teilwrite.
- manipulierte Entity → `CHECKSUM_MISMATCH`.
- beschädigtes Backup → Restore abgelehnt.
- Read-only, Permission denied und Disk-full sind klar klassifizierbare Failure Codes.

## Noch nicht als OS-nativ bewiesen
Disk-full, Read-only und Permission-denied werden in V0.3 deterministisch klassifiziert und teilweise preflight-geprüft. Echte plattformspezifische Failure-Injection folgt im jeweiligen Plattform-Acceptance-Gate, weil Container/Root-Rechte OS-Verhalten verfälschen können.
