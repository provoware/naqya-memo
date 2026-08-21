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

## Audio aufnehmen
1. `Audio & Diktat` öffnen.
2. Den roten Aufnahmebutton drücken.
3. Sprechen.
4. Nochmals drücken, um zu stoppen.

NAQYA sichert die Aufnahme währenddessen ungefähr alle 3 Sekunden in kleinen lokalen Segmenten. Wenn Browser oder Gerät unerwartet beendet werden, versucht NAQYA beim nächsten Start die bereits gespeicherten Segmente automatisch zu retten.

Gespeicherte Audioeinträge können mit `▶` direkt abgespielt werden.

## Offline-Diktat
NAQYA startet keinen Cloud-Fallback.

Wenn das Gerät eine lokale Browser-Spracherkennung anbietet, erscheint der Text live während des Sprechens. Wenn keine lokale Engine verfügbar ist, bleibt die normale Audioaufnahme nutzbar.

Unter `Einstellungen` zeigt NAQYA deutlich an, welche Funktionen auf dem aktuellen Gerät vorhanden sind.

## Sprachmodell
Unter `Einstellungen` kannst du ein Leistungsprofil wählen:

- Schnell
- Ausgewogen
- Genau
- Maximum

Zusätzlich können lokale `.bin`- oder `.gguf`-Modelldateien gespeichert werden. Wichtig: Ein importiertes Modell allein aktiviert noch keine whisper.cpp-Engine. Die native Laufzeit folgt im nächsten Entwicklungsblock.

## Vollbackup
Unter `Einstellungen` → `Vollbackup exportieren`.

Version 0.2 sichert:

- Termine und Notizen
- Projekte und Einstellungen
- Dokumente und Fotos
- Audio-Dateien

Beim Import werden vorhandene SHA-256-Prüfsummen kontrolliert. Sehr große Backups brauchen während des Exports zusätzlichen Arbeitsspeicher; NAQYA warnt vorher.

## Wenn etwas unterbrochen wurde
Nach einem Absturz oder Browserabbruch NAQYA erneut starten. Falls sichere Audiosegmente vorhanden sind, wird daraus automatisch ein Eintrag `Wiederhergestellte Aufnahme` erzeugt und in der Chronologie protokolliert.
