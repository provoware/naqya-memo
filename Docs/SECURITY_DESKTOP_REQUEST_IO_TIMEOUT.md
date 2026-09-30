# Desktop Request I/O Timeout

Status: Release-Härtung, kein Produktfeature.

## Befund

Der Desktop-HTTP-Pfad begrenzt bereits die Größe normaler JSON-Anfragen, aber eine verbundene lokale Gegenstelle konnte den Request-Thread weiterhin unbegrenzt blockieren, wenn angekündigte Request-Daten nur teilweise oder gar nicht übertragen wurden.

## Vertrag

`app/secure_response_server.py` setzt pro akzeptierter Verbindung einen Socket-I/O-Timeout.

- Standard: 30 Sekunden
- Konfigurationsvariable: `PROVOWARE_REQUEST_IO_TIMEOUT_SECONDS`
- zugelassener Bereich: 1 bis 120 Sekunden
- gilt verbindungsbezogen; der Serverprozess selbst läuft weiter
- keine Änderung an Datenmodell, Produktfunktion oder Release-Gate-Status

Der Timeout schützt sowohl normale JSON-Anfragen als auch Streaming-Uploads vor endlos stillstehenden lokalen Verbindungen. Er begrenzt keine Gesamtdauer eines Transfers, solange fortlaufend Daten eintreffen.

## Regression

`tests/security/test_desktop_request_io_timeout.py` startet den echten gehärteten Loopback-Server mit einem Testtimeout von einer Sekunde und beweist:

1. normaler unauthentifizierter Startvertrag bleibt intakt,
2. authentifizierter Zugriff funktioniert,
3. ein absichtlich nur teilweise gesendeter authentifizierter POST wird innerhalb der begrenzten Wartezeit freigegeben,
4. der Server bleibt danach erreichbar,
5. der Timeout beendet nur die betroffene Verbindung und nicht den Prozess.

## Release-Grenze

Dieser Slice hebt keine realen Browser-, Mikrofon-, Android- oder iPhone-Gates an. Der Release bleibt NO-GO, bis die getrennten realen Acceptance-Gates erfüllt sind.
