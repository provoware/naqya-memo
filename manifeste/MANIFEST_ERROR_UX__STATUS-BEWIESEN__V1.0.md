# ERROR-UX-001 – Sichere Mutation-Fehlergrenze

Status: **BEWIESEN nach grünem SHA-genauem CI-Lauf**

## Befund
Unbekannte Ausnahmen in schreibenden HTTP-Anfragen wurden zuvor pauschal als HTTP 400 behandelt. Dadurch konnten interne Fehlertexte als vermeintlicher Bedienfehler bis an die Oberfläche gelangen. Zusätzlich blieb nach einem unklaren Schreibfehler offen, ob weitere Mutationen sicher ausgeführt werden dürfen.

## Vertrag
- Nur ausdrücklich bekannte Fehlercodes dürfen die HTTP-Grenze passieren.
- Unbekannte Fehler werden zu `INTERNAL_ERROR`; interne Exception-Texte, lokale Pfade und technische Details bleiben verborgen.
- Ein unbekannter Fehler während einer Mutation aktiviert eine fail-closed Schreibsperre.
- Im Degraded Mode bleiben Lesezugriffe verfügbar; weitere POST-Schreibzugriffe werden mit `MUTATION_DEGRADED_MODE` und HTTP 503 abgewiesen.
- Die Fehlermeldung ist deutsch und handlungsorientiert: Zustand neu laden, nicht blind erneut speichern, anschließend sauber über `SCHNELLSTART.sh` neu starten.
- `/api/health` meldet `mutation_mode` als `READY` oder `DEGRADED`.
- Bekannte Validierungs-, Konflikt-, Not-Found-, Security- und Größenfehler behalten stabile Codes und passende HTTP-Statuswerte.

## Fehlerprävention
Der Mutation-Barrier verhindert Kaskadenfehler und Doppelwrites nach einem Zustand, dessen Commit-Ergebnis nicht sicher bestätigt werden konnte. Ein Neustart setzt die Sperre nur zusammen mit dem kompletten Prozess- und Datenbank-Lifecycle zurück.

## Regression
`tests/security/test_error_ux_contract.py` prüft:
- bekannte Clientfehler bleiben stabil,
- Revisionskonflikte bleiben HTTP 409,
- ungültiges JSON wird stabil klassifiziert,
- unbekannte interne Details werden nicht geleakt,
- unbekannte Mutationsfehler aktivieren den Degraded Mode,
- Degraded Mode liefert HTTP 503 und Recovery-Hinweis,
- der Server enthält die verbindliche Mutation-Barrier und Health-Anzeige.

## Release-Grenze
Keine neue Produktfunktion. Keine Änderung an Datenmodell, Mutation-Semantik oder UI-Layout. Die Änderung beschränkt sich auf Fehlerklassifizierung, sichere Mutation-Sperre, Regression und Evidence.
