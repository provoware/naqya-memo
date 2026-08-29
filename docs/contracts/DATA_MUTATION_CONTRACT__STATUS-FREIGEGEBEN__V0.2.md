# DATA-MUTATION-CONTRACT V0.2
## Verbindliche Pipeline für jede kritische Änderung

### PRE
- Projektordner identifiziert und erlaubt
- freier Speicher ausreichend
- Datenbankschema kompatibel
- Profil/Entity vorhanden
- erwartete Revision stimmt
- keine inkompatible Migration aktiv
- Operation besitzt eindeutige Operation-ID

### ACTION
- eine SQLite-Transaktion pro atomarem fachlichem Use Case
- Asset-Dateien zuerst in Temp/Staging
- keine UI schreibt direkt Datenbank oder Asset-Datei

### POST
- SQLite `integrity_check` in passenden Gates
- Entity-Checksum validieren
- Revision exakt +1
- Referenzen auf Assets/Entities gültig
- erwartetes Ergebnis fachlich prüfen

### COMMIT
Erst nach erfolgreichem ACTION-Schritt. SQLite übernimmt Rollback bei Exception.

### EVIDENCE
- operation_id
- type
- target ids
- Zeit UTC + monotone Dauer
- PRE-Ergebnis
- POST-Ergebnis
- Fehlercode
- Recovery-/Rollback-Ergebnis
- Test-/Evidence-Referenzen

### Destruktive Aktionen
Standardmäßig nur `TRASHED`. Hard Delete ist ein späterer, ausdrücklich bestätigter Wartungsprozess.
