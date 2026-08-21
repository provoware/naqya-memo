# NAQYA – einfache Anleitung

## Starten

### Linux
1. Projektordner öffnen.
2. Rechtsklick auf `START_NAQYA.sh` und Ausführen erlauben, falls nötig.
3. Doppelklick oder im Terminal `./START_NAQYA.sh`.

### Windows
Doppelklick auf `START_NAQYA.bat`.

Diese Starter öffnen den lokalen PWA-Betrieb. Dafür ist keine Cloud und kein Benutzerkonto nötig.

## Etwas speichern
1. Oben rechts `＋ Neu` wählen.
2. Art auswählen.
3. Titel oder Text eingeben.
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

Der aktuelle Quellstand ist so vorbereitet, dass die Tauri-Desktop-App einen eigenen `naqya-whisper`-Sidecar bevorzugt. Der Linux-Sidecar wird im Qualitätsgate bereits reproduzierbar gebaut und geprüft. Ein vollständiges Endanwender-Desktop-Paket ist jedoch noch nicht als Release abgenommen.

Für native Transkription werden benötigt:

1. eine funktionsfähige NAQYA-Tauri-Desktop-Ausgabe,
2. der passende lokale `naqya-whisper`-Sidecar oder ersatzweise ein ausdrücklich verfügbarer lokaler `whisper-cli`,
3. ein importiertes lokales Sprachmodell (`.bin` oder `.gguf`).

Der externe `whisper-cli` ist nur ein Fallback. Wenn der Sidecar verfügbar ist, hat er Vorrang.

Beim ersten Diktat kann die Vorbereitung des Sprachmodells etwas dauern. NAQYA überträgt das Modell in 4-MiB-Blöcken in den eigenen lokalen Modellbereich und prüft anschließend die vollständige Datei mit SHA-256. Erst nach erfolgreicher Prüfung wird das Modell atomar aktiviert.

Während des Diktats passiert lokal:

```text
Mikrofon
→ 16 kHz Mono
→ PCM16/WAV-Segment
→ bevorzugt NAQYA-Sidecar, sonst lokaler CLI-Fallback
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

## Diagnose
Die Diagnose soll unterscheiden können:

- Tauri-Desktop-Brücke verfügbar oder nicht
- gebündelter Sidecar verfügbar oder nicht
- externer lokaler CLI-Fallback verfügbar oder nicht
- verwendete Runtimequelle
- Sprachmodell vorhanden oder nicht

Fehlt die native Runtime, funktioniert die normale Offline-Audioaufnahme weiterhin. Es wird kein Cloud-Ersatz aktiviert.

## Vollbackup
Unter `Einstellungen` → `Vollbackup exportieren`.

Gesichert werden unter anderem:

- Termine und Notizen
- Projekte und Einstellungen
- Dokumente und Fotos
- Audio-Dateien

Beim Import werden vorhandene SHA-256-Prüfsummen kontrolliert. Sehr große Backups brauchen während des Exports zusätzlichen Arbeitsspeicher.

Native Modellpfade selbst werden nicht als vertrauenswürdige Pfade in ein Backup übernommen. Auf einem neuen Gerät wird ein Modell erneut lokal vorbereitet.

## Wenn etwas unterbrochen wurde
Nach einem Absturz oder Browserabbruch NAQYA erneut starten. Falls sichere Audiosegmente vorhanden sind, wird daraus automatisch ein Eintrag `Wiederhergestellte Aufnahme` erzeugt und in der Chronologie protokolliert.

## Aktuelle Grenze
Der Quellstand enthält die Sidecar-Integration und den Linux-CI-Build. Die vollständige Linux-/Windows-Desktop-Paketabnahme mit echter Hardware und Mikrofon steht noch aus. Für einen Endanwender-Release darf dieser Schritt nicht übersprungen werden.
