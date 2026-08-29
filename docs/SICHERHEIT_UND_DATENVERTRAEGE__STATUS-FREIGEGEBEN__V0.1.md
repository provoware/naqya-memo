# 🛡️ SICHERHEIT UND DATENVERTRÄGE — STATUS: FREIGEGEBEN — V0.1

## Universal Mutation Contract
**PRE:** Berechtigung, Pfad, Speicher, Lock, Schema, Eingaben, Backupfähigkeit prüfen.  
**ACTION:** ausschließlich in kontrollierter Transaktion.  
**POST:** Existenz, Schema, Hash, Referenzen, Index und erwartete Semantik prüfen.  
**EVIDENCE:** Operation-ID, Zeit, Ergebnis, Dauer, betroffene IDs, Fehlercode.  
**ROLLBACK:** Temp entfernen oder auf letzte verifizierte Generation zurück.  
**COMMIT:** erst nach erfolgreicher Nachprüfung.

## Destruktionsschutz
- Standard: Archiv/Papierkorb
- endgültiges Löschen: zweite Bestätigung + klare Konsequenz
- außerhalb Projektordner: explizite Pfadfreigabe
- Massenaktionen: Vorschau der Anzahl und Wirkung
- kein Auto-Repair, das Nutzerdaten überschreibt

## Backups
Rotationsidee: `B-2, B-1, CURRENT, B+1, B+2` als Generationenmodell; praktisch werden zwei verifizierte ältere Generationen dauerhaft vorgehalten und neue erfolgreiche Zustände rollierend ergänzt.
Jede Generation enthält Manifest, Hashes, Schema-Version, Zeit, Operation-ID.

## Debugbericht
Enthält:
- Tool-/Buildversion
- Plattform/OS-Version
- Display-/Capability-Infos
- letzte kontrollierte Operationen
- Fehlercode
- Stacktrace im Entwicklerteil
- Recovery-Versuche
- bekannte passende BRAIN-Regeln
- Lösungsvorschläge
- Privacy-Filter-Ergebnis

Nicht automatisch: Memo-Inhalt, PIN, Tokens, unnötige persönliche Pfade.

## Exit/Crash
Bei regulärem Schließen: Session-/Integrity-Check, Diagnosebericht nur bei Fehler oder Nutzeroption.
Bei Crash: beim nächsten Start Crash-Report erzeugen und nach Möglichkeit im Standardeditor öffnen. Mobile Plattformen können das Öffnen einschränken; dort sichere In-App-Ansicht + Teilen-Button.
