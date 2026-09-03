# Desktop-PIN: Schutz gegen automatisiertes Durchprobieren

## Zweck

Diese Release-Härtung verändert keine Produktfunktion. Sie begrenzt ausschließlich wiederholte falsche Desktop-PIN-Versuche im lokalen HTTP-Zugang.

## Sicherheitsvertrag

- Anfragen ohne `Authorization` verbrauchen kein Fehlversuchsbudget.
- Mehrere Browser-Asset-Anfragen mit exakt denselben falschen Zugangsdaten zählen innerhalb des Zeitfensters nur einmal.
- Gezählt werden unterschiedliche falsche Authorization-Werte pro Client.
- Produktionsstandard: 5 unterschiedliche Fehlversuche innerhalb von 120 Sekunden.
- Danach gilt eine temporäre Sperre von 30 Sekunden.
- Während der Sperre antwortet der Server mit HTTP `429` und `Retry-After`.
- Auch eine korrekte PIN umgeht eine aktive Sperre nicht.
- Nach Ablauf kann sich der Nutzer wieder normal anmelden.
- Eine erfolgreiche Anmeldung löscht den Fehlversuchszustand.

## Warum unterschiedliche Zugangsdaten gezählt werden

Browser senden dieselben Basic-Auth-Daten häufig parallel für HTML, JavaScript, CSS und weitere Assets. Würde jede einzelne HTTP-Anfrage zählen, könnte bereits ein einziger Tippfehler mehrere Fehlversuche erzeugen und den Nutzer unnötig aussperren. Deshalb wird pro Zeitfenster nur der SHA-256-Digest eines jeweils unterschiedlichen Authorization-Headers gezählt; die Zugangsdaten selbst werden dafür nicht gespeichert.

## Konfiguration

Die Grenzwerte können für Tests über `PROVOWARE_AUTH_MAX_FAILURES`, `PROVOWARE_AUTH_FAILURE_WINDOW` und `PROVOWARE_AUTH_LOCKOUT_SECONDS` angepasst werden. Die Produktionsdefaults bleiben 5 / 120 s / 30 s.

## Release-Grenze

Dieser Schutz ersetzt keine realen Browser-, Android-, iOS-, Mikrofon- oder Hardware-Gates. Der Release bleibt `NO-GO`, bis die getrennten Release-Gates tatsächlich erfüllt sind.
