# NAQYA 0.4 – Audio-Normalisierung, Modellpfad und Live-Segment-STT

## Ziel

Version 0.4 schließt drei technische Lücken zwischen Browseraufnahme und echter lokaler Desktop-Spracherkennung:

1. einheitliches Audioformat für whisper.cpp,
2. kontrollierter nativer Modellpfad,
3. segmentierte Offline-Live-Transkription.

## 1. Audio-Pipeline

Die Originalaufnahme bleibt unverändert im vorhandenen MediaRecorder-/Recovery-Pfad.

Parallel dazu wird für die native Spracherkennung ein eigener PCM-Pfad erzeugt:

```text
MediaStream
  ↓
Web Audio
  ↓
Mono-Float32
  ↓
lineares Resampling
  ↓
16.000 Hz
  ↓
PCM16/WAV
  ↓
4-Sekunden-Segment
  ↓
whisper.cpp
```

### Verbindliche Zielparameter

- Sample-Rate: **16.000 Hz**
- Kanäle: **1 / Mono**
- Sampleformat: **PCM16 little-endian**
- Container: **WAV / RIFF**
- Live-STT-Fenster: **4.000 ms**
- Original-Audio-Recovery: **3.000 ms**

Die beiden Segmentgrößen erfüllen unterschiedliche Aufgaben: 3 Sekunden dienen der verlustarmen Originalaudio-Sicherung, 4 Sekunden dienen der STT-Verarbeitung.

## 2. Live-Verarbeitung

Native STT-Segmente werden nicht gleichzeitig unkontrolliert gestartet. Sie laufen über eine Promise-Warteschlange in Aufnahme-Reihenfolge.

Pro Sitzung werden mindestens gespeichert:

- Anzahl transkribierter Segmente
- kumulierte Audiozeit
- kumulierte whisper.cpp-Verarbeitungszeit
- Echtzeitfaktor = Verarbeitungszeit / Audiozeit
- verwendetes Modell
- nativer Modellpfad
- letzter Fehler, falls vorhanden

## 3. Stop-Verhalten

Beim Betätigen von Stop wird die Mikrofonaufnahme unmittelbar beendet. Das zuletzt bereits aufgenommene PCM-Segment darf danach noch lokal fertig transkribiert werden.

Der finale Diktattext wird nach Abschluss der STT-Warteschlange noch einmal in den bereits erzeugten Eintrag geschrieben. Dadurch muss das Mikrofon nicht während langsamer Nachverarbeitung aktiv bleiben.

## 4. Sprachmodell-Transfer

Browser-/IndexedDB-Modelle werden nicht als ein riesiger Base64-Block an Rust übergeben.

Transfer:

```text
Blob
  ↓
4 MiB Slice
  ↓
Base64 IPC
  ↓
.part-Datei
  ↓
weiteres Slice
  ↓
...
  ↓
SHA-256 über vollständige Datei
  ↓
atomare Aktivierung
```

### Sicherheitsregeln

- nur `.bin` und `.gguf`
- Dateiname wird bereinigt
- Transferkennung erlaubt nur ASCII-alphanumerisch und `-`
- einzelne IPC-Blöcke maximal 8 MiB dekodiert
- Modell kleiner als 10 MiB wird verworfen
- erwartete SHA-256 muss 64 Hex-Zeichen besitzen
- finale Datei erhält Hashpräfix im Namen
- erst nach erfolgreicher Prüfung wird `.part` umbenannt
- abgebrochene Transfers können entfernt werden

## 5. Vertrauensgrenze Modellpfad

`naqya_transcribe` akzeptiert keinen beliebigen Dateipfad mehr.

Vor dem whisper.cpp-Aufruf werden sowohl der konfigurierte NAQYA-Modellordner als auch der angeforderte Modellpfad kanonisiert. Der Modellpfad muss innerhalb des NAQYA-Modellordners liegen.

Damit kann die Web-Oberfläche nicht beliebige lokale Dateien als Modell an die native Runtime übergeben.

## 6. WAV-Validierung

Vor dem Aufruf von whisper.cpp prüft Rust mindestens:

- Mindestgröße 44 Byte
- Bytes 0–3 = `RIFF`
- Bytes 8–11 = `WAVE`
- maximale Einzelgröße 512 MiB

Diese Prüfung ersetzt keinen vollständigen WAV-Parser, verhindert aber offensichtliche Formatfehler an der Native-Grenze.

## 7. Provider-Priorität

```text
Tauri + whisper.cpp + lokales Modell
        ↓ bevorzugt
native segmentierte Offline-STT

sonst

lokale Browser-On-Device-STT

sonst

nur Audioaufnahme
```

Ein Cloud-Fallback ist nicht vorgesehen.

## 8. Aktuelle bekannte Grenze

Die 0.4-Live-Erfassung verwendet `ScriptProcessor` als kompatiblen Übergangsadapter. Dieser Web-Audio-Mechanismus ist veraltet, aber weiterhin breit verfügbar. Für die nächste Härtungsstufe wird `AudioWorklet` vorgesehen.

whisper.cpp selbst wird in 0.4 noch nicht reproduzierbar als Sidecar ausgeliefert. Die lokale CLI muss vorhanden sein.

## 9. Nächste Abnahme

Für 0.5 sind reale Messungen vorgesehen:

- Linux Referenzgerät
- Windows Referenzgerät
- tiny/base/small
- 1 / 10 / 30 / 60 Minuten
- leise und normale Sprache
- Hintergrundgeräusch
- Pause/Fortsetzen
- Abbruch während Modelltransfer
- fehlendes Modell
- gelöschtes natives Modell
- fehlende whisper-cli
- CPU-/RAM-Messung
- Echtzeitfaktor pro Profil

## 10. Zielwerte

Noch zu messen, nicht als bereits erreicht zu verstehen:

- Segmentstart bis Text sichtbar: möglichst < 1,5 s nach Segmentabschluss auf geeigneter Hardware
- Echtzeitfaktor: Ziel < 1,0 für Standardprofil auf Referenzdesktop
- Recovery gesicherter Originalsegmente: > 99 % im kontrollierten Unterbrechungstest
- Datenverlust bei normalem Crash: maximal aktuelles noch nicht persistiertes Originalsegment
