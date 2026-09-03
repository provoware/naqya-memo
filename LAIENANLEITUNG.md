# Einfache Anleitung

## Tool starten

1. Projektordner öffnen.
2. `STARTEN_LINUX.sh` doppelklicken oder im Terminal ausführen:

```bash
./STARTEN_LINUX.sh
```

3. Beim Start erscheint die Profilwahl. Dort kannst du:
   - ein vorhandenes Profil auswählen oder
   - **＋ Neues Profil anlegen** wählen.
4. Für ein neues Profil einen Namen und eine eigene **4-stellige PIN** eingeben und die PIN einmal wiederholen.
5. Danach startet PROVOWARE mit genau diesem Profil. Im Browser bleibt die bestehende geschützte PIN-Anmeldung aktiv.
6. Öffnet sich der Browser nicht automatisch, zeigt das Terminal die lokale Adresse an.

Falls kein grafischer Dialog verfügbar ist, verwendet der Starthelfer das Terminal. Bei einem rein automatischen/headless Start wird nichts blockiert und das bisherige erste aktive Profil verwendet.

## Orientierung

- **Links:** Bereiche wie Memos, Todos und Kalender.
- **Oben:** Schnellmemo, nächste Aufgaben und **Ansicht**.
- **Mitte:** der aktuelle Arbeitsbereich.
- **Rechts:** Tool-Info und einfache Zähler.
- **Unten:** nur ein kompakter Systemstatus; Technik lässt sich bei Bedarf öffnen.

## Ansicht anpassen

Oben im Feld **ANSICHT**:
- Theme wechseln
- Schrift vergrößern/verkleinern
- Arbeitsbereich vergrößern/verkleinern

Die Oberfläche ordnet sich bei größerer Darstellung neu an, statt Bedienelemente
übereinander zu legen.

## Eingabefelder

Graue Beispieltexte sind nur Vorschläge. Sie werden nicht automatisch gespeichert.
Im knappen Hilfemodus erscheinen zusätzliche Hinweise erst, wenn du in ein Feld klickst.

## Wenn etwas nicht startet

Nichts erzwingen und keine fremden Prozesse beenden. Der Startmechanismus prüft belegte
Ports und wählt bei Bedarf einen sicheren freien Ersatzport.
