# Native Whisper Desktop – 0.3.0

## Ziel

Die Desktop-Ausgabe von NAQYA erhält eine lokale Tauri-Brücke zu whisper.cpp. Es gibt keinen Cloud-Fallback.

## Laufzeit

Die Rust-Seite erkennt `whisper-cli` beziehungsweise den über `NAQYA_WHISPER_CLI` gesetzten Pfad. `naqya_capabilities` meldet Plattform, CPU-Anzahl und Verfügbarkeit. `naqya_transcribe` nimmt Base64-WAV, Modellpfad, Sprache und optionale Threadzahl an.

## Sicherheitsregeln

- Modellpfad muss auf eine vorhandene Datei zeigen.
- Einzeltranskriptionen sind auf 512 MiB Audiodaten begrenzt.
- temporäre Audiodateien werden nach dem Prozess entfernt.
- Netzwerkzugriff wird für STT nicht benötigt.
- Browserbetrieb bleibt funktionsfähig, auch wenn keine native Brücke vorhanden ist.

## Noch offen

1. WebM/Opus aus MediaRecorder lokal zu WAV/PCM normalisieren.
2. importierte IndexedDB-Modelle in kontrollierte Desktop-Modellpfade materialisieren.
3. whisper.cpp als reproduzierbares Sidecar bündeln, statt eine externe Installation vorauszusetzen.
4. segmentierte Live-Transkription mit Interim-/Final-Text verbinden.
5. reale Latenz-, CPU-, RAM- und Langzeittests auf Linux und Windows durchführen.

## Nächster Meilenstein

`0.4.0 – AUDIO NORMALISIERUNG, MODELLPFAD & LIVE-SEGMENT-STT`
