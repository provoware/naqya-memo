# NAQYA – einfache Anleitung

## 1. Welche Variante benutze ich?

NAQYA besitzt zwei Betriebsarten:

- **PWA / Browser:** Kalender, Dokumente, Audio, Projekte und alle Grundfunktionen funktionieren lokal. Live-Text gibt es nur, wenn der Browser ausdrücklich lokale Spracherkennung unterstützt.
- **Desktop-App:** Linux/Windows-Version mit zusätzlicher lokaler whisper.cpp-Spracherkennung. Hier kann NAQYA unabhängig vom Browser Sprache offline in Text umwandeln.

Es gibt keinen automatischen Cloud-Fallback.

## 2. PWA starten

### Linux
1. Ordner öffnen.
2. `START_NAQYA.sh` ausführbar machen, falls nötig.
3. Doppelklick oder im Terminal `./START_NAQYA.sh`.

### Windows
Doppelklick auf `START_NAQYA.bat`.

## 3. Etwas schnell speichern

1. Oben rechts `＋ Neu` wählen.
2. Art auswählen.
3. Titel oder Text eingeben.
4. Optional Projekt, Kategorie und Tags ergänzen.
5. `Speichern`.

Fehlende Zuordnungen verhindern das Speichern nicht. Erst speichern, später organisieren.

## 4. Audio aufnehmen

1. `Audio & Diktat` öffnen.
2. Den roten Aufnahmebutton drücken.
3. Sprechen.
4. Nochmals drücken, um zu stoppen.

NAQYA sichert die Aufnahme ungefähr alle 3 Sekunden in kleinen lokalen Segmenten. Wird die App unerwartet beendet, versucht NAQYA beim nächsten Start die bereits gespeicherten Segmente zu retten.

Gespeicherte Audioeinträge können mit `▶` direkt abgespielt werden.

## 5. Offline-Live-Diktat in der Desktop-App

Voraussetzung: Ein lokales Whisper-Sprachmodell ist installiert.

1. `Einstellungen` öffnen.
2. Unter **Offline-Sprachmodell** zunächst `Ausgewogen` wählen.
3. `Lokales Modell installieren` drücken.
4. Eine passende mehrsprachige `.bin`- oder `.gguf`-Datei auswählen.
5. Warten, bis die Fortschrittsanzeige 100 % erreicht.
6. `Audio & Diktat` öffnen.
7. Mikrofonknopf drücken und sprechen.
8. Erneut drücken, um Diktat und Aufnahme abzuschließen.

Der Text entsteht lokal auf dem Computer. Gleichzeitig bleibt die Originalaufnahme gespeichert.

Während des Diktats kann NAQYA Werte wie `RTF 0.62` anzeigen. Vereinfacht gilt:

- **unter 1,0:** Verarbeitung ist schneller als die Audiolänge
- **um 1,0:** ungefähr Echtzeit
- **über 1,0:** der Rechner verarbeitet langsamer als gesprochen wird

## 6. Welches Sprachprofil soll ich nehmen?

| Profil | Empfehlung |
|---|---|
| Schnell | schwächerer Rechner, kurze Memos |
| **Ausgewogen** | **empfohlener Startpunkt** |
| Genau | leistungsfähiger Rechner, bessere Erkennung |
| Maximum | nur leistungsfähige Desktop-Systeme |

Für Deutsch ein **mehrsprachiges** Whisper-Modell verwenden.

## 7. Warum wird Audio zusätzlich gespeichert?

Spracherkennung kann Wörter falsch verstehen. Deshalb behandelt NAQYA das Audio als Originalquelle und das Transkript als bearbeitbaren Text. Ein Fehler in der Transkription darf die Aufnahme nicht zerstören.

## 8. Diagnose

Unter `Einstellungen` zeigt NAQYA an, ob unter anderem folgende Funktionen verfügbar sind:

- IndexedDB
- Mikrofon
- MediaRecorder
- Service Worker
- lokale Browser-Spracherkennung
- native whisper.cpp-Runtime
- SHA-256-Prüfung
- persistenter Speicher

In der Desktop-App werden zusätzlich installierte native Sprachmodelle angezeigt.

## 9. Vollbackup

Unter `Einstellungen` → `Vollbackup exportieren`.

Gesichert werden unter anderem:

- Termine und Notizen
- Projekte und Einstellungen
- Dokumente und Fotos
- Audio-Dateien
- Transkripte
- Modellmetadaten

Große Whisper-Modelldateien selbst werden nicht in jedes Benutzerbackup kopiert. Sie können separat wieder installiert werden.

Beim Backup-Import prüft NAQYA vorhandene SHA-256-Prüfsummen.

## 10. Wenn etwas unterbrochen wurde

Nach Absturz oder Browserabbruch NAQYA erneut starten. Sind sichere Audiosegmente vorhanden, wird daraus automatisch eine `Wiederhergestellte Aufnahme` erzeugt und die Aktion in der Chronologie festgehalten.

## 11. Wichtig für Version 0.3.0

Die native Runtime ist implementiert. Linux- und Windows-Releasepakete befinden sich aber noch in der technischen Abnahme. Bis diese abgeschlossen ist, bleibt die PWA der einfachste sofort nutzbare Startweg.
