# Native Whisper Desktop – historischer Entwicklungsvertrag 0.3.0

> **Dokumentenstatus:** Historische Entwicklungsstufe. Der aktuelle Runtime-Stand steht in `README.md`, `docs/ARCHITEKTUR.md` und `docs/WHISPER_SIDECAR.md`.

## damaliges Ziel

Die Desktop-Ausgabe von NAQYA sollte eine lokale Tauri-Brücke zu whisper.cpp erhalten. Ein Cloud-Fallback war bereits ausgeschlossen.

## damaliger Laufzeitvertrag

Die Rust-Seite erkannte `whisper-cli` beziehungsweise den über `NAQYA_WHISPER_CLI` gesetzten Pfad. `naqya_capabilities` meldete Plattform, CPU-Anzahl und Verfügbarkeit. `naqya_transcribe` nahm Base64-WAV, Modellpfad, Sprache und optionale Threadzahl an.

## damalige Sicherheitsregeln

- Modellpfad musste auf eine vorhandene Datei zeigen.
- Einzeltranskriptionen waren auf 512 MiB Audiodaten begrenzt.
- temporäre Audiodateien wurden nach dem Prozess entfernt.
- Netzwerkzugriff war für STT nicht erforderlich.
- Browserbetrieb blieb funktionsfähig, auch wenn keine native Brücke vorhanden war.

## damals noch offene Punkte und heutiger Status

1. WebM/Opus lokal zu WAV/PCM normalisieren → **in 0.4 umgesetzt**.
2. importierte IndexedDB-Modelle in kontrollierte Desktop-Modellpfade materialisieren → **in 0.4 umgesetzt**.
3. whisper.cpp als reproduzierbaren Sidecar anbinden → **Runtimevertrag und Tauri-Integration in 0.5 umgesetzt; vollständige Release-Bundle-Abnahme noch offen**.
4. segmentierte Live-Transkription verbinden → **in 0.4 umgesetzt**.
5. reale Latenz-, CPU-, RAM- und Langzeittests auf Linux und Windows → **weiterhin offen**.

## Historischer Folgemeilenstein

Der damalige Folgemeilenstein war `0.4.0 – AUDIO NORMALISIERUNG, MODELLPFAD & LIVE-SEGMENT-STT` und ist inzwischen umgesetzt.
