# NAQYA 0.4 – historischer Vertrag für Audio-Normalisierung, Modellpfad und Live-Segment-STT

> **Dokumentenstatus:** Historische Entwicklungsstufe 0.4. Der aktuelle Gesamtstand steht in `README.md`; aktuelle Runtime-Details stehen in `docs/WHISPER_SIDECAR.md`.

## Ziel der 0.4-Stufe

0.4 schloss drei technische Lücken zwischen Browseraufnahme und lokaler Desktop-Spracherkennung:

1. einheitliches Audioformat für whisper.cpp,
2. kontrollierter nativer Modellpfad,
3. segmentierte Offline-Live-Transkription.

## Audio-Pipeline

Die Originalaufnahme bleibt im MediaRecorder-/Recovery-Pfad. Parallel wird für native STT ein PCM-Pfad erzeugt:

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
lokale whisper.cpp-Runtime
```

Verbindliche Parameter:

- Sample-Rate: **16.000 Hz**
- Kanäle: **1 / Mono**
- Sampleformat: **PCM16 little-endian**
- Container: **WAV / RIFF**
- Live-STT-Fenster: **4.000 ms**
- Original-Audio-Recovery: **3.000 ms**

## Live-Verarbeitung

Native STT-Segmente werden in Aufnahme-Reihenfolge über eine lokale Warteschlange verarbeitet. Pro Sitzung werden unter anderem Segmentzahl, Audiozeit, STT-Verarbeitungszeit und Echtzeitfaktor erfasst.

Beim Stoppen endet die Mikrofonaufnahme sofort. Bereits aufgenommene letzte STT-Segmente dürfen danach lokal fertig verarbeitet werden.

## Sprachmodell-Transfer

Browser-/IndexedDB-Modelle werden blockweise in den nativen Modellbereich übertragen:

```text
Blob
  ↓
4-MiB-Slice
  ↓
Base64 IPC
  ↓
.part-Datei
  ↓
...
  ↓
SHA-256 über vollständige Datei
  ↓
atomare Aktivierung
```

Sicherheitsregeln:

- nur `.bin` und `.gguf`
- Dateiname wird bereinigt
- Transferkennung ist eingeschränkt
- einzelne IPC-Blöcke sind begrenzt
- erwartete SHA-256 muss gültig sein
- Aktivierung erst nach vollständiger Prüfung
- abgebrochene Transfers können bereinigt werden

## Vertrauensgrenze Modellpfad

Native Transkription akzeptiert nur kanonisierte Modellpfade innerhalb des geschützten NAQYA-Modellordners. Beliebige lokale Dateien dürfen nicht als Modellpfad durchgereicht werden.

## WAV-Validierung

Vor dem nativen Aufruf werden mindestens Mindestgröße, `RIFF`-/`WAVE`-Signatur und maximale Einzelgröße geprüft.

## Provider-Prinzip

```text
lokale native STT, wenn verfügbar
  ↓ sonst
lokale Browser-On-Device-STT, wenn wirklich lokal verfügbar
  ↓ sonst
nur Audioaufnahme
```

Ein Cloud-Fallback ist nicht vorgesehen.

## Historische Grenze von 0.4 und heutiger Status

In 0.4 war whisper.cpp noch nicht als reproduzierbarer Tauri-Sidecar integriert. **Dieser Punkt ist in 0.5 auf Quell-/CI-Ebene umgesetzt:** Upstream und Commit sind fest gepinnt, Tauri `externalBin` ist konfiguriert und Linux x86_64 wird im CI gebaut und gehasht. Eine vollständige Endanwender-Bundle-Abnahme steht weiterhin aus.

`ScriptProcessor` wird weiterhin als Übergangsadapter verwendet; `AudioWorklet` bleibt offen.

## Noch offene reale Abnahme

Weiterhin zu messen bzw. zu prüfen:

- Linux- und Windows-Referenzgeräte
- verschiedene Sprachmodelle
- kurze sowie 30-/60-Minuten-Sitzungen
- Hintergrundgeräusch und Pausen
- fehlende bzw. beschädigte Runtime/Modelle
- CPU-/RAM-Verhalten
- Echtzeitfaktor und sichtbare Latenz

Zielwerte bleiben Messziele und dürfen nicht als bereits erreicht dargestellt werden.
