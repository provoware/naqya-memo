# Audio & Offline-STT – technischer Vertrag 0.3.0

## Ziel

Audio und Diktat funktionieren ohne Cloud. Die Desktop-App enthält eine native `whisper.cpp`-Laufzeit über `whisper-rs 0.16.0`; die PWA nutzt weiterhin ausschließlich echte lokale Browser-Spracherkennung, sofern diese verfügbar ist.

Es gibt keinen Cloud-Fallback.

## Zwei parallele Audiodatenpfade

### 1. Beweissichere Aufnahme

- `MediaRecorder` schreibt ungefähr alle 3000 ms ein Segment.
- Jedes Segment wird sofort in `audioSegments` persistiert.
- `audioSessions` hält Status, Segmentzahl, MIME-Typ und Diktat-Entwurf.
- Beim normalen Stop werden die Segmente in Reihenfolge zu einer Audiodatei zusammengeführt.
- Nach erfolgreicher Finalisierung werden temporäre Segmente gelöscht.

### 2. Native Live-Transkription

In Tauri wird derselbe Mikrofonstream zusätzlich über Web Audio verarbeitet:

1. `AudioWorklet` liest Mono-PCM.
2. PCM wird in ungefähr 3-Sekunden-Fenstern gesammelt.
3. Das Fenster wird lokal auf 16 kHz resampelt.
4. `services/native-bridge.js` ruft `naqya_transcribe_pcm` über Tauri IPC auf.
5. Rust verarbeitet das Fenster mit `whisper-rs` / `whisper.cpp`.
6. Text, Segmentzeitstempel, Verarbeitungszeit und Echtzeitfaktor werden zurückgegeben.
7. Das Transkript wird fortlaufend in `audioSessions.transcriptDraft` gesichert.

Die Audioaufnahme bleibt unabhängig von der Transkription erhalten. Ein STT-Fehler darf deshalb nicht die Originalaufnahme vernichten.

## Native Runtime

Hauptmodul: `src-tauri/src/lib.rs`

Kernbefehle:

- `naqya_native_status`
- `naqya_transcribe_pcm`
- `naqya_model_import_begin`
- `naqya_model_import_chunk`
- `naqya_model_import_finish`
- `naqya_model_import_abort`

Die Runtime lädt `WhisperContext` pro Modell nur einmal und hält ihn in einem Thread-sicheren Kontextcache. Neue Transkriptionsblöcke erzeugen jeweils einen frischen `WhisperState`.

## PCM-Vertrag

Native Transkriptionsblöcke müssen folgende Bedingungen erfüllen:

- Mono
- `Float32`
- 16.000 Hz
- endliche Samplewerte
- maximal 180 Sekunden pro Einzelaufruf

Für das Live-Diktat werden derzeit ungefähr 3-Sekunden-Blöcke verwendet.

## Messwerte je Transkriptionsblock

Die native Antwort liefert mindestens:

- `text`
- `segments[]`
- `modelFile`
- `language`
- `samples`
- `durationMs`
- `processingMs`
- `realtimeFactor`

`realtimeFactor < 1.0` bedeutet, dass die Verarbeitung schneller als die Audiolänge war.

## Recovery

Beim Start sucht NAQYA Audio-Sitzungen mit Status `recording`, `stopping` oder `recoverable`.

Wenn Segmente vorhanden sind:

1. Segmente sortieren.
2. lokale Audiodatei rekonstruieren.
3. neuen Eintrag mit Tag `wiederhergestellt` anlegen.
4. Chronologie ergänzen.
5. temporäre Segmente löschen.
6. Sitzung auf `recovered` setzen.

Damit sind Aufnahme und Transkriptionspfad bewusst entkoppelt.

## Providerpriorität

1. **Native Desktop whisper.cpp**, wenn Tauri-Runtime und mindestens ein lokales Modell vorhanden sind.
2. **Browser On-Device**, wenn `SpeechRecognition.processLocally` verfügbar ist.
3. Nur Audioaufnahme, wenn keine lokale STT-Engine vorhanden ist.

Cloud-STT wird nicht automatisch verwendet.

## Modellprofile

| Profil | Whisper-Zielmodell | Richtgröße |
|---|---|---:|
| Schnell | tiny | ~75 MiB |
| Ausgewogen | base | ~142 MiB |
| Genau | small | ~466 MiB |
| Maximum | medium | ~1536 MiB |

Für Deutsch sind mehrsprachige Modelle erforderlich.

## Nativer Modellimport

Große Modelle werden nicht als ein einzelner IPC-Block übertragen.

Ablauf:

1. Dateityp und Mindestgröße im UI prüfen.
2. nativen Import starten.
3. Datei in 1-MiB-Blöcke teilen.
4. jeden Block lokal über Tauri IPC übertragen.
5. temporäre `.part`-Datei fortlaufend schreiben.
6. Endgröße prüfen.
7. SHA-256 streamingbasiert berechnen.
8. optional erwartete SHA-256 vergleichen.
9. Modell atomar in den lokalen Modellordner verschieben.

Maximal akzeptierte Modellgröße dieser Stufe: 4 GiB.

## Modellsuche

Die Desktop-Runtime sucht:

1. im persistenten App-Datenordner `models/`,
2. danach in mit dem Release gebündelten Modellressourcen.

Für das Profil wird bevorzugt nach `tiny`, `base`, `small` oder `medium` im Dateinamen gesucht.

## Backup

Backup-Schema 2 enthält weiterhin:

- Einträge
- Projekte
- Einstellungen
- Nutzerdokumente und Audio-Dateien
- SHA-256 je Nutzdatei
- Modellmetadaten

Große Whisper-Modellbinärdateien werden bewusst nicht in jedes Benutzerbackup kopiert.

## Bekannte Grenzen 0.3.0

- Native Linux-/Windows-Paketabnahme steht bis zum Release-Gate noch aus.
- Live-Fenster sind derzeit zeitbasiert; adaptive VAD-Fenster folgen.
- sehr langsame Geräte können eine Transkriptionswarteschlange aufbauen.
- das allgemeine Vollbackup ist noch Base64/JSON-basiert und benötigt bei großen Beständen zusätzlichen RAM.
- native iOS-/Android-Runtime folgt in einer späteren Plattformstufe.

## Nächste technische Stufe

`0.3.1 – DESKTOP HARDENING & RELEASE PACKAGING`:

- reale Linux-Build-/Startabnahme
- Windows-Buildabnahme
- native Modellentfernung
- adaptive VAD-/Fenstersteuerung
- Warteschlangenbegrenzung und Lastregelung
- Release-Paket mit optional gebündeltem Base-Modell
- reproduzierbare Performance-Messung
