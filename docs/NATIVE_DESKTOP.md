# NAQYA 0.3 – Native Desktop-App

## Zweck

Die Desktop-Schicht erweitert dieselbe NAQYA-Oberfläche um lokale Betriebssystemdienste. In 0.3.0 liegt der Schwerpunkt auf `whisper.cpp` für vollständig lokale Sprache-zu-Text-Verarbeitung.

## Architektur

```text
Web-Oberfläche
   │
   ├─ PWA-Dienste
   │
   └─ services/native-bridge.js
            │ Tauri IPC
            ▼
      src-tauri/src/lib.rs
            │
            ├─ whisper-rs
            └─ whisper.cpp
```

Die PWA bleibt ohne Tauri lauffähig. Native Funktionen werden per Fähigkeiten-Erkennung aktiviert.

## Linux – Buildvoraussetzungen

Beispiel für Ubuntu/Kubuntu 24.04:

```bash
sudo apt update
sudo apt install -y \
  libwebkit2gtk-4.1-dev \
  libappindicator3-dev \
  librsvg2-dev \
  patchelf \
  libssl-dev \
  pkg-config \
  clang \
  cmake \
  build-essential
```

Rust installieren, falls noch nicht vorhanden:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
rustup default stable
```

## Entwicklungsstart Linux

Aus Repository-Wurzel:

```bash
chmod +x START_NAQYA_DESKTOP_DEV.sh
./START_NAQYA_DESKTOP_DEV.sh
```

Der Starter:

1. prüft Python und Cargo,
2. startet den lokalen Frontend-Server auf `127.0.0.1:8765`,
3. startet die Tauri-App,
4. beendet den Hilfsserver beim Schließen wieder.

## Manuelle Prüfung

Terminal 1:

```bash
python3 -m http.server 8765 --bind 127.0.0.1
```

Terminal 2:

```bash
cargo run --manifest-path src-tauri/Cargo.toml
```

## Windows – Entwicklungsstart

Voraussetzungen sind Rust stable, Microsoft C++ Build Tools, WebView2 und CMake/Clang entsprechend der Tauri-/whisper.cpp-Buildumgebung.

PowerShell aus Repository-Wurzel:

```powershell
powershell -ExecutionPolicy Bypass -File .\START_NAQYA_DESKTOP_DEV.ps1
```

Der Starter verwendet `py` oder `python` für den lokalen Frontend-Server und beendet diesen nach dem Schließen der Desktop-App.

## Sprachmodell installieren

Die Modelldatei wird **nicht** ins Git-Repository gelegt.

Empfohlen für den ersten deutschen Funktionstest:

- Profil: `Ausgewogen`
- mehrsprachiges `base`-Modell
- üblicher Name etwa `ggml-base.bin`

In NAQYA:

1. Einstellungen öffnen.
2. Offline-Sprachmodell → Ausgewogen.
3. Lokales Modell installieren.
4. Datei auswählen.
5. Fortschritt abwarten.
6. Diagnose prüfen: `Native whisper.cpp` und mindestens ein Modell müssen verfügbar sein.

## Modellimport intern

Große Modelle werden in 1-MiB-Blöcken übertragen. Rust schreibt sie in eine temporäre `.part`-Datei. Erst nach Größenprüfung und SHA-256-Berechnung wird die Datei in den persistenten Modellordner verschoben.

Das verhindert, dass ein unvollständiger Import als gültiges Modell erscheint.

## Diktat-Abnahme

Für eine manuelle Basisabnahme:

1. Mikrofonzugriff erlauben.
2. 10 Sekunden normalen deutschen Text sprechen.
3. prüfen, dass Live-Text erscheint.
4. prüfen, dass Modellname, Verarbeitungszeit und RTF sichtbar werden.
5. Aufnahme stoppen.
6. gespeicherten Diktateintrag öffnen bzw. abspielen.
7. App vollständig schließen und erneut starten.
8. Eintrag und Transkript müssen erhalten sein.

## Performance

Je Transkriptionsblock werden `durationMs`, `processingMs` und `realtimeFactor` geliefert.

```text
RTF = Verarbeitungszeit / Audiolänge
```

Ziel für flüssiges Live-Diktat:

- RTF möglichst < 1,0
- dauerhaft wachsende Warteschlange vermeiden
- auf schwächeren Geräten kleineres Modell wählen

## Sicherheitsregeln

- kein Cloud-Fallback
- Modellpfade werden nicht frei aus dem Frontend akzeptiert; ausgewählt wird nur aus bekannten lokalen Modellen
- Dateinamen dürfen keine Pfadbestandteile enthalten
- Modellgröße 10 MiB bis 4 GiB
- Transkriptionsblöcke maximal 180 Sekunden
- PCM muss 16 kHz und endlich sein
- Modellimport wird vor Aktivierung geprüft

## Release-Gate für 0.3.0

0.3.0 darf erst als native Referenz gelten, wenn:

- JavaScript-Prüfungen PASS
- statische Projektverträge PASS
- Rust/Tauri `cargo check` PASS
- Linux: Start und 10-/30-Minuten-Diktat geprüft
- Windows: Build und Start geprüft
- Recovery während laufender Aufnahme geprüft
- Modellimport mit korrekter und absichtlich falscher SHA-256 geprüft
- keine Netzwerkabhängigkeit für Transkription festgestellt

## Nächster Schritt 0.3.1

- adaptive VAD-Fenster
- Queue-/CPU-Lastregelung
- nativer Modell-Löschen-/Wechsel-Workflow
- richtige AppImage/DEB/MSI-Releasepipeline
- signiertes Manifest für freigegebene Modelle
- reproduzierbare Benchmarkberichte
