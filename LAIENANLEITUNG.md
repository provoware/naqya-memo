# NAQYA – einfache Anleitung

## Starten

### Linux
1. Ordner öffnen.
2. Rechtsklick auf `START_NAQYA.sh` und Ausführen erlauben, falls nötig.
3. Doppelklick oder im Terminal `./START_NAQYA.sh`.

### Windows
Doppelklick auf `START_NAQYA.bat`.

## Etwas speichern
1. Oben rechts `＋ Neu` wählen.
2. Art auswählen.
3. Titel/Text eingeben.
4. Optional Projekt, Kategorie und Tags ergänzen.
5. `Speichern`.

## Audio
`Audio & Diktat` öffnen und den roten Aufnahmebutton drücken. Nochmals drücken beendet und speichert die Aufnahme lokal.

## Offline-Diktat
NAQYA verwendet niemals absichtlich eine Cloud-Spracherkennung als Fallback. Wenn dein Browser lokale On-Device-Spracherkennung anbietet, erscheint sie als verfügbar. Andernfalls bleibt nur Audioaufnahme aktiv, bis die geplante whisper.cpp-Engine integriert ist.

## Backup
Unter `Einstellungen` → `Backup exportieren`. Der aktuelle Stand exportiert Metadaten. Binäre Audio- und Dokumentdateien werden im nächsten Backup-Ausbauschritt in ein Komplettpaket aufgenommen.
