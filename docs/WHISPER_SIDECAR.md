# NAQYA – reproduzierbarer whisper.cpp-Sidecar

## Status

Aktueller Stand: **0.5.0**.

Die Tauri-Integration ist umgesetzt: `bundle.externalBin` verweist auf `binaries/naqya-whisper`, `tauri-plugin-shell` startet den Sidecar, und die native Runtime priorisiert den Sidecar vor einem externen `whisper-cli`-Fallback.

Der Linux-x86_64-Sidecar wird im GitHub-Actions-Qualitätsgate reproduzierbar gebaut und per SHA-256 geprüft. Noch nicht abgeschlossen ist die vollständige Endanwender-Bundle-Abnahme, bei der nachgewiesen wird, dass der Sidecar im erzeugten Desktop-Paket enthalten und daraus tatsächlich startbar ist.

## Fest gebundener Upstream

- Projekt: `ggml-org/whisper.cpp`
- Version: `v1.9.2`
- Commit: `306c88f4d1286aec1bf96e544632897886af5501`
- Upstream-Zielprogramm: `whisper-cli`
- NAQYA-Sidecar-Basisname: `naqya-whisper`
- Buildprofil: CPU / Release / `GGML_NATIVE=OFF`

Der maschinenlesbare Herkunfts- und Buildvertrag liegt unter `src-tauri/sidecar/whisper-runtime.json`.

## Zielplattformen

- Linux x86_64: `x86_64-unknown-linux-gnu`
- Windows x86_64: `x86_64-pc-windows-msvc`

Andere Zielplattformen werden vom Vorbereitungsskript bewusst abgewiesen, bis sie separat in den Vertrag aufgenommen und geprüft wurden.

## Reproduzierbarer Build

`tools/build_whisper_sidecar.sh`:

1. bestimmt die lokale Rust-Zielplattform,
2. lädt ausschließlich den festgelegten whisper.cpp-Upstream,
3. checkt das festgelegte Tag aus,
4. verifiziert den daraus aufgelösten Commit gegen den NAQYA-Vertrag,
5. baut `whisper-cli` im Releaseprofil mit `GGML_NATIVE=OFF`,
6. legt das Ergebnis unter dem Tauri-konformen zielplattformgebundenen Namen in `src-tauri/binaries/` ab,
7. erzeugt einen SHA-256-Nachweis.

Die Binärdateien selbst werden nicht dauerhaft im Repository versioniert. Sie werden als Build-/Release-Artefakte erzeugt.

## Runtime-Priorität

```text
Tauri-Sidecar naqya-whisper
        ↓ wenn nicht verfügbar
expliziter lokaler whisper-cli-Fallback
        ↓ wenn nicht verfügbar
keine native STT
```

Der Fallback darf den Sidecar nicht still überstimmen. Die verwendete Runtimequelle muss diagnostizierbar sein.

## Sicherheitsgrenzen

- kein ungeprüfter Runtime-Download während der Anwendungslaufzeit
- kein automatisches Aktivieren einer unbekannten Sidecar-Binärdatei
- fest gebundener Upstream-Commit
- SHA-256-Nachweis für erzeugte Sidecar-Artefakte
- keine generische `main`-PATH-Erkennung
- expliziter Fallback nur über `whisper-cli` beziehungsweise `NAQYA_WHISPER_CLI`
- Sprachmodelle werden getrennt davon in den geschützten NAQYA-Modellpfad materialisiert und validiert

## Was noch fehlt

1. vollständiges Linux-Tauri-Bundle bauen
2. enthaltenen Sidecar im Paket nachweisen und aus dem Paket starten
3. Release-Nachweis mit Dateiname, Dateigröße, SHA-256 und Buildumgebung erzeugen
4. Windows-x86_64-Sidecar mit demselben Herkunftsvertrag bauen
5. Windows-Bundle end-to-end prüfen
6. reale Linux-/Windows-Hardware- und Mikrofonabnahme

## Nächster Entwicklungsblock

**0.5.1 – Linux-Bundle-Abnahme, Release-Nachweis & Windows-Sidecar**
