# PROVOWARE – NAQYA Memo Tool 2026

Offline-first Organizer für Termine, Fristen, Aufgaben, Dokumente, Fotos, Audio-Memos, Live-Diktat, Projekte, Kategorien, Tags und Chronologie.

## Stand

**0.5.0 – TAURI-SIDECAR-INTEGRATION & REPOSITORY-KONSOLIDIERUNG**

NAQYA verarbeitet Sprache weiterhin lokal und ohne Cloudpflicht. Der aktuelle Desktoppfad bündelt whisper.cpp als bevorzugten Tauri-Sidecar, baut den Linux-x86_64-Sidecar reproduzierbar aus einem fest gepinnten Upstream-Commit und prüft das erzeugte Artefakt per SHA-256. Ein expliziter lokaler `whisper-cli`-Fallback bleibt nur als diagnostizierbarer Ersatzpfad erhalten.

## Schnellstart PWA

### Linux

```bash
chmod +x START_NAQYA.sh
./START_NAQYA.sh
```

### Windows

Doppelklick auf `START_NAQYA.bat`.

### Manuell

```bash
python3 -m http.server 8765 --bind 127.0.0.1
```

Dann `http://127.0.0.1:8765` öffnen.

## Neu in 0.5.0

- reproduzierbarer whisper.cpp-Runtimevertrag mit festem Upstream-Tag und Commit
- Linux-/Windows-Zielnamen für Tauri-Sidecars definiert
- `tauri-plugin-shell` und `bundle.externalBin` integriert
- gebündelter `naqya-whisper`-Sidecar wird vor externem CLI-Fallback verwendet
- Runtime-Diagnose unterscheidet Sidecar, Fallback und Nichtverfügbarkeit
- Linux-x86_64-Sidecar wird im CI real gebaut und per SHA-256 geprüft
- Laufzeit-Downloads ungeprüfter kritischer Binärdateien bleiben verboten
- temporäre STT-WAV-Dateien liegen im privaten Tauri-App-Cache
- `AGENTS.md` und `TODO.md` steuern Entwicklung, Freigabe und Restarbeiten verbindlich
- `.gitignore` schützt Buildausgaben, Sidecar-Artefakte und lokale Sprachmodelle vor versehentlichem Commit
- Versions-, Status- und Offline-Cache-Metadaten sind auf 0.5.0 konsolidiert

## Desktop-Spracherkennung

Priorität der nativen Runtime:

1. gebündelter Tauri-Sidecar `naqya-whisper`
2. explizit freigegebener lokaler `whisper-cli`-Fallback über `NAQYA_WHISPER_CLI` bzw. kontrollierte PATH-Erkennung

Ein importiertes Modell wird zuerst in den eigenen App-Datenbereich übertragen, per SHA-256 geprüft und erst anschließend für native Transkription verwendet.

## Datenschutz

Der Kern benötigt keinen Account, keine Cloud und keine Telemetrie. Es gibt keinen automatischen Online-STT-Fallback.

## Qualitätsprüfung

GitHub Actions prüft unter anderem:

- JSON-Struktur
- JavaScript-Syntax
- reproduzierbaren Linux-Sidecar-Build
- SHA-256 des erzeugten Sidecars
- Rust-Formatierung
- Rust/Tauri-Kompilierung
- statische Architektur-/Projektverträge
- Shell-Syntax

## Bekannte Grenzen

- reale Linux-Desktop-/Mikrofonabnahme auf Referenzhardware steht noch aus
- Windows-x86_64-Sidecar benötigt noch Build-, Bundle- und Hardwareabnahme
- Live-PCM nutzt weiterhin `ScriptProcessor`; `AudioWorklet` folgt als Qualitätsausbau
- sehr große Vollbackups sind durch JSON/Base64 speicherintensiv
- native Mobiladapter für Android und iPhone/iPad stehen noch aus

## Nächster Hauptblock

**0.5.x – WINDOWS-SIDECAR, RELEASE-NACHWEIS & REAL-HARDWARE-ABNAHME**.
