# Release-Härtung: sichere Erst-PIN

Status: **P0 geschlossen / Release weiterhin NO-GO**

## Befund

Der Desktop-Transport erzwingt seit dem vorherigen Härtungsschritt die Profil-PIN. Bei einem komplett neuen Projekt erzeugte der darunterliegende Referenzserver jedoch weiterhin das bekannte Profil `Standardprofil` mit der festen PIN `0000`. Dadurch war die Authentifizierungsgrenze beim Erststart vorhersagbar.

## Änderung

`app/secure_server.py` erkennt **vor** dem Import des Produktservers, ob bereits ein aktives Profil existiert. Nur wenn noch kein aktives Profil vorhanden ist, wird der vom Referenzserver erzeugte Erstzugang unmittelbar vor dem ersten HTTP-Request gehärtet:

1. kryptografisch sichere, zwölfstellige Zufalls-PIN erzeugen (`secrets`),
2. Einmaldatei `nutzer-einstellungen/ERSTSTART_PIN_EINMAL.txt` mit Dateirecht `0600` schreiben,
3. vorhandene Bootstrap-PIN `0000` über den vorhandenen `ProfileService.change_pin()` ersetzen,
4. bei erster erfolgreicher Anmeldung die Einmaldatei automatisch entfernen.

Falls der erwartete Bootstrap-Vertrag künftig nicht mehr `0000` ist, startet die Härtung **fail-closed** mit `FIRST_PIN_BOOTSTRAP_CONTRACT_CHANGED`, statt still eine unbekannte Sicherheitsannahme zu übernehmen.

## Regression

`tests/security/test_desktop_pin_gate.py` beweist jetzt neun Verträge:

- zufällige 12-stellige Erst-PIN,
- Einmaldatei mit `0600`,
- UI ohne Authentifizierung `401`,
- `0000` beim frischen Projekt abgewiesen,
- falsche PIN abgewiesen,
- generierte PIN akzeptiert,
- Einmaldatei nach erfolgreichem Login entfernt,
- API mit gültiger PIN erreichbar,
- beide Linux-Starter verwenden weiterhin ausschließlich `secure_server.py`.

Der Test ist bereits Bestandteil des bestehenden GitHub-Quality-Workflows. Reale Browser-, Mikrofon-, Android- und iPhone-Gates werden dadurch nicht simuliert oder hochgestuft.

## Sicherheitsgrenze

Die Erst-PIN-Datei ist ein lokales Übergangsgeheimnis. Ein Angreifer mit Zugriff auf den Projektordner und das Benutzerkonto kann ohnehin die lokalen Projektdaten lesen. Die Datei wird deshalb restriktiv mit `0600` angelegt und nach dem ersten erfolgreichen Login entfernt. Eine spätere explizite PIN-Änderungsoberfläche oder Lock/Logout-UX ist ein separater Produkt-/Security-Slice und nicht Bestandteil dieser Änderung.
