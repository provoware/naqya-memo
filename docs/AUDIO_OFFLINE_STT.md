# Audio & Offline-STT – historischer technischer Vertrag 0.2.0

> **Dokumentenstatus:** Historische Entwicklungsstufe. Der aktuelle Gesamtstand steht in `README.md`; aktuelle native Runtime-Details stehen in `docs/WHISPER_SIDECAR.md`.

## Ziel der 0.2-Stufe

Audio und Diktat sollten ohne Cloud funktionieren und bei Unterbrechungen möglichst wenig Daten verlieren.

## Segmentierung und Recovery

- MediaRecorder schreibt ungefähr alle 3000 ms ein Segment.
- Jedes Segment wird in `audioSegments` gespeichert.
- `audioSessions` hält Status, Segmentzahl, MIME-Typ und Diktat-Entwurf.
- Beim normalen Stop werden Segmente in Reihenfolge zu einer Datei zusammengeführt.
- Nach erfolgreicher Finalisierung werden temporäre Segmente entfernt.
- Beim Start werden unterbrochene Sitzungen gesucht und vorhandene Segmente nach Möglichkeit rekonstruiert.

Dieses Recovery-Prinzip ist weiterhin Bestandteil des aktuellen 0.5.0-Stands.

## Sprache-zu-Text-Provider

Der damalige Providervertrag sah zwei ausschließlich lokale Wege vor:

1. **Browser On-Device** – nur wenn die Browserfunktion wirklich lokal verfügbar ist.
2. **Native whisper.cpp Bridge** – für die Desktop-Runtime.

Es gibt weiterhin keinen Cloud-Fallback.

## Modellprofile und Modellimport

Die Profile Schnell, Ausgewogen, Genau und Maximum dienen der Geräteführung. Lokale `.bin`-/`.gguf`-Modelle können importiert und per SHA-256 geprüft werden.

Der native Modellpfad wurde in 0.4 weiter gehärtet: Modelle werden blockweise in einen geschützten App-Datenbereich übertragen und erst nach vollständiger Integritätsprüfung atomar aktiviert.

## Backup

Backup-Schema 2 enthält Nutzdaten und Binärdateien mit Integritätsmetadaten. Große Sprachmodell-Binärdateien sind bewusst nicht Bestandteil des normalen Nutzbackups.

Das Backup ist weiterhin JSON/Base64-basiert und noch nicht streamingoptimiert.

## Historische Folgestufe und heutiger Status

Der damalige nächste Schritt war eine echte native whisper.cpp-Laufzeit über Tauri. Dieser Entwicklungsweg wurde in 0.3 bis 0.5 umgesetzt:

- Tauri-Desktop-Brücke vorhanden
- 16-kHz-Mono-WAV-Normalisierung vorhanden
- geschützter nativer Modellpfad vorhanden
- segmentiertes Live-STT vorhanden
- reproduzierbarer whisper.cpp-Sidecar-Vertrag vorhanden
- Tauri-Sidecar-Integration vorhanden
- Linux-x86_64-Sidecar-Build und SHA-256-Prüfung im CI vorhanden

Noch offen sind die vollständige Desktop-Bundle-Abnahme, Windows-Abnahme und reale Hardware-/Langzeittests.
