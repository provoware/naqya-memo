# NAQYA – reproduzierbarer whisper.cpp-Sidecar

## Zweck

NAQYA bindet die native Offline-Spracherkennung schrittweise an einen reproduzierbaren whisper.cpp-Runtimevertrag. Die Anwendung darf keine ungeprüfte Runtime zur Laufzeit herunterladen oder automatisch aktivieren.

## Fest gebundener Upstream

- Projekt: `ggml-org/whisper.cpp`
- Version: `v1.9.2`
- Commit: `306c88f4d1286aec1bf96e544632897886af5501`
- Zielprogramm: `whisper-cli`
- Buildprofil: CPU / Release / `GGML_NATIVE=OFF`

Der vollständige maschinenlesbare Vertrag liegt unter `src-tauri/sidecar/whisper-runtime.json`.

## Unterstützte Zielplattformen in dieser Ausbaustufe

- Linux x86_64: `x86_64-unknown-linux-gnu`
- Windows x86_64: `x86_64-pc-windows-msvc`

Andere Plattformen werden vom Vorbereitungsskript bewusst abgewiesen, bis sie separat gebaut und geprüft wurden.

## Reproduzierbarer Build

`tools/build_whisper_sidecar.sh` bestimmt die lokale Rust-Zielplattform, lädt ausschließlich das fest gebundene Upstream-Tag, prüft den daraus aufgelösten Commit gegen den Vertrag und baut `whisper-cli` im Releaseprofil. Das Ergebnis wird unter dem für Tauri vorgesehenen zielplattformgebundenen Namen in `src-tauri/binaries/` abgelegt.

Für jede erzeugte Binärdatei wird zusätzlich eine `.sha256`-Datei erzeugt. Ein produktives Release darf erst freigegeben werden, wenn der konkrete Binärhash in den Release-Nachweis übernommen und gegen das gebündelte Artefakt geprüft wird.

## Sicherheitsgrenzen

Diese Stufe bündelt noch keine Binärdateien im Repository. Sie schafft den reproduzierbaren Herkunfts-, Versions-, Zielplattform- und Integritätsvertrag. Der bestehende explizite `NAQYA_WHISPER_CLI`-/PATH-Fallback bleibt deshalb vorerst bestehen.

Der nächste Schritt ist die tatsächliche Tauri-`externalBin`-Integration der gebauten und per SHA-256 freigegebenen Linux- und Windows-Artefakte sowie die deterministische Runtime-Auflösung mit Diagnose der tatsächlich gestarteten Binärdatei.
