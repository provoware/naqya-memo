# Audio & Offline-STT – technischer Vertrag 0.2.0

## Ziel

Audio und Diktat müssen ohne Cloud funktionieren und bei Unterbrechungen möglichst wenig Daten verlieren.

## Segmentierung

- MediaRecorder schreibt alle 3000 ms ein Segment.
- Jedes Segment wird sofort in `audioSegments` gespeichert.
- `audioSessions` hält Status, Segmentzahl, MIME-Typ und Diktat-Entwurf.
- Beim normalen Stop werden alle Segmente in Reihenfolge zu einer Datei zusammengeführt.
- Nach erfolgreicher Finalisierung werden die temporären Segmente gelöscht.

## Recovery

Beim Start sucht NAQYA Audio-Sitzungen mit Status `recording`, `stopping` oder `recoverable`.

Wenn Segmente vorhanden sind:

1. Segmente sortieren.
2. lokale Audiodatei rekonstruieren.
3. neuen Eintrag mit Tag `wiederhergestellt` anlegen.
4. Chronologie ergänzen.
5. temporäre Segmente löschen.
6. Sitzung auf `recovered` setzen.

Damit gehen bei einem Absturz typischerweise nur Daten verloren, die seit dem letzten ausgelieferten MediaRecorder-Segment noch nicht persistiert wurden.

## Sprache-zu-Text Provider

`services/stt-core.js` definiert zwei lokale Providerklassen:

1. **Browser On-Device** – nur wenn `SpeechRecognition.processLocally` verfügbar ist.
2. **Native whisper.cpp Bridge** – über `window.NAQYANativeSTT`.

Es gibt keinen Cloud-Fallback.

### Native Bridge Vertrag

Eine spätere Desktop-/Mobilhülle stellt mindestens bereit:

```js
window.NAQYANativeSTT = {
  transcribe(blob, { language, profile }) {
    // Promise -> { text, segments?, timing? }
  }
}
```

Optional kann später `startLive` ergänzt werden.

## Modellprofile

| Profil | Whisper-Zielmodell | Richtgröße |
|---|---|---:|
| Schnell | tiny | ~75 MiB |
| Ausgewogen | base | ~142 MiB |
| Genau | small | ~466 MiB |
| Maximum | medium | ~1536 MiB |

Die Größen dienen der Geräteführung. Ein importiertes Modell aktiviert ohne passende native/WASM-Laufzeit noch keine Transkription.

## Modellimport

- akzeptiert `.bin` und `.gguf`
- Mindestgröße 10 MiB als Plausibilitätsprüfung
- lokale Speicherung in IndexedDB
- SHA-256 wird über WebCrypto berechnet, wenn verfügbar
- kein Upload

## Backup

Backup-Schema 2 enthält:

- Einträge
- Projekte
- Einstellungen
- sämtliche Nutzerdokumente und Audio-Dateien
- SHA-256 je Binärdatei
- Modellmetadaten, aber bewusst keine großen Sprachmodell-Binärdateien

Binärdateien werden derzeit Base64-kodiert in einem selbstenthaltenden JSON-Paket gespeichert. Das ist dependency-frei und robust, aber noch nicht streamingoptimiert.

## Nächste technische Stufe

0.3.0 soll die tatsächliche native whisper.cpp-Laufzeit über Tauri anbinden, Modellpfade sicher verwalten und messbare Kennzahlen für Echtzeitfaktor, Latenz, RAM-Verbrauch und Langzeitstabilität liefern.
