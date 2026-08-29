# BACKUP-RESTORE-CONTRACT V0.2

## Mindestanforderung
Ein Backup ist erst `VERIFIED`, wenn:
1. konsistenter Snapshot erstellt,
2. SHA-256 ermittelt,
3. Snapshot separat geöffnet,
4. SQLite `integrity_check == ok`,
5. Manifest atomar geschrieben wurde.

## Generationen
Zielrotation: mindestens zwei verifizierte ältere Generationen; neue erfolgreiche Generationen werden rollierend ergänzt. Ein fehlerhaftes Backup darf keine verifizierte Generation verdrängen.

## V0.3 Acceptance
Zusätzlich folgt ein echter Restore in einen frischen Projektordner mit Datensatz-/Hashvergleich.
