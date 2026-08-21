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

NAQYA sichert die Originalaufnahme ungefähr alle 3 Sekunden in kleinen lokalen Segmenten. Wenn Browser oder Gerät unerwartet beendet werden, versucht NAQYA beim nächsten Start die bereits gespeicherten Segmente automatisch zu retten.

Gespeicherte Audioeinträge können mit `▶` direkt abgespielt werden.

## Offline-Live-Diktat auf dem Desktop
NAQYA startet keinen Cloud-Fallback.

Für die native Desktop-Transkription werden benötigt:

1. die NAQYA-Desktop-App,
2. eine lokal verfügbare `whisper-cli`,
3. ein importiertes lokales Sprachmodell (`.bin` oder `.gguf`).

Beim ersten Diktat kann die Vorbereitung des Sprachmodells etwas dauern. NAQYA kopiert die Datei nicht auf einmal in den Arbeitsspeicher, sondern überträgt sie in 4-MiB-Blöcken in den eigenen lokalen Modellbereich. Danach wird die vollständige Datei mit SHA-256 geprüft.

Erst wenn die Prüfung erfolgreich ist, darf die native Spracherkennung dieses Modell verwenden.

Während des Diktats passiert lokal:

```text
Mikrofon
→ 16 kHz Mono
→ WAV-Segment
→ whisper.cpp
→ Text
```

Der Text wird ungefähr in 4-Sekunden-Arbeitsfenstern erzeugt. Die Originalaufnahme bleibt parallel erhalten.

Wenn du `Stop` drückst, wird die Mikrofonaufnahme sofort beendet. Ein bereits aufgenommenes letztes Segment darf anschließend noch lokal fertig transkribiert werden.

## Browser-Diktat
Wenn ein Browser tatsächlich eine lokale On-Device-Spracherkennung anbietet, kann NAQYA diese weiterhin verwenden. Eine Online-Spracherkennung wird nicht automatisch als Ersatz gestartet.

## Sprachmodell
Unter `Einstellungen` kannst du ein Leistungsprofil wählen:

- Schnell
- Ausgewogen
- Genau
- Maximum

Zusätzlich können lokale `.bin`- oder `.gguf`-Modelldateien gespeichert werden.

Die Diagnose zeigt, ob die Desktop-Brücke und whisper.cpp auf dem aktuellen Gerät erkannt werden.

## Vollbackup
Unter `Einstellungen` → `Vollbackup exportieren`.

Gesichert werden unter anderem:

- Termine und Notizen
- Projekte und Einstellungen
- Dokumente und Fotos
- Audio-Dateien

Beim Import werden vorhandene SHA-256-Prüfsummen kontrolliert. Sehr große Backups brauchen während des Exports zusätzlichen Arbeitsspeicher; NAQYA warnt vorher.

Native Modellpfade selbst werden nicht als vertrauenswürdige Pfade in ein Backup übernommen. Auf einem neuen Gerät wird ein Modell erneut lokal vorbereitet.

## Wenn etwas unterbrochen wurde
Nach einem Absturz oder Browserabbruch NAQYA erneut starten. Falls sichere Audiosegmente vorhanden sind, wird daraus automatisch ein Eintrag `Wiederhergestellte Aufnahme` erzeugt und in der Chronologie protokolliert.

## Wenn Live-Diktat nicht startet
Unter `Einstellungen` die Fähigkeiten prüfen:

- Mikrofon vorhanden?
- Web Audio vorhanden?
- Native Desktop-Brücke erkannt?
- whisper.cpp erkannt?
- Sprachmodell importiert?

Fehlt whisper.cpp, funktioniert die normale Offline-Audioaufnahme weiterhin. Es wird kein Cloud-Ersatz aktiviert.
