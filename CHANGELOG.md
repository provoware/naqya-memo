# Änderungsprotokoll

## 0.5.1-B – LINUX-BUNDLE & RELEASE-NACHWEIS

- Tauri-`frontendDist` vom Repository-Stamm auf ein deterministisch gestagtes `../dist` umgestellt
- explizite Desktop-Runtime-Allowlist eingeführt; Symlinks und unerwartete Dateien werden im Staging abgewiesen
- `BUILD_MANIFEST.json` mit Dateigröße und SHA-256 für jede gestagte Runtime-Datei ergänzt
- Desktop-Staging und Release-Evidence-Schema in das normale Qualitätsgate aufgenommen
- whisper.cpp-Buildprofil auf `cpu-release-static` gehärtet und `BUILD_SHARED_LIBS=OFF` ergänzt
- separaten Linux-Bundle-Workflow mit pfadbasierten Triggern eingeführt
- Tauri CLI für den Paketnachweis auf Version 2.11.4 gepinnt
- reales Linux-DEB im CI gebaut und extrahiert
- enthaltenen `naqya-whisper` aus dem Paketkontext erfolgreich gestartet
- Sidecar-Laufzeitabhängigkeiten mit `ldd` geprüft; keine fehlende Bibliothek erkannt
- Build- und Paket-Sidecar per SHA-256 auf Bytegleichheit geprüft
- `RELEASE_EVIDENCE.schema.json` als versionierten maschinenlesbaren Nachweisvertrag eingeführt
- `RELEASE_EVIDENCE.json` und `RELEASE_EVIDENCE.txt` aus dem realen Bundlelauf erzeugt
- Release-Nachweis enthält Quellcommit, Plattform, Architektur, Paket-/Sidecar-Größen und SHA-256, whisper.cpp-Identität, Toolchain sowie CI-Run
- erstes erfolgreiches Bundle-Evidence-Artefakt: `naqya-linux-bundle-nachweis-1`, Bundle-Run-ID `32477864231`, Qualitäts-Run-ID `32477864261`
- Projektfortschritt für den Entwicklungsblock 0.5.1 transparent auf 5 von 9 Hauptpunkten beziehungsweise 56 % festgelegt
- README oben um aktuellen Status, Fortschritt, Tool-Kurzprofil, erledigte und offene Punkte sowie den konkreten Linux-Nachweis erweitert

Nachgewiesene Artefakte des ersten erfolgreichen 0.5.1-B-Laufs:
- `NAQYA-0.5.0-linux-x86_64.deb`: 5.148.416 Bytes, SHA-256 `1721b92de3a23da0ece8e9833d6949bf9b9987d7cc3de69e76d1cd50fc83f2e4`
- `naqya-whisper`: 2.828.584 Bytes, SHA-256 `6c4805c72c855ea5b627b10450bb3feec56ea31b8038aed052ce9260bc11529b`
- CI-Artefakt-SHA-256: `6831027b0ed6f5dd1ee1137d2cb814d5e6868f4a2ef041169318b4a54be2661d`

Bekannte Grenze dieser Stufe:
- die Paket- und Sidecar-Abnahme ist im CI real erfolgt; Installation, Mikrofonbetrieb, echtes Sprachmodell und Langzeitsitzungen auf einem realen Linux-Endgerät bleiben eine getrennte Hardwareabnahme
- Windows-Bundle und Windows-Sidecar sind noch nicht nachgewiesen
- das professionelle Diagnose-/Debugging-/Logging-Modul und die durchgehende Diagnose↔Release-Evidence-Bindung folgen in 0.5.1-C

## 0.5.1-A – PRODUKTVERSIONS-KONSISTENZ

- PWA-Produktversionskonstante in `app.js` von 0.2.0 auf 0.5.0 synchronisiert
- harten Gleichheitstest zwischen `app.js` und `VERSION.json` eingeführt
- Backup-Vertrag prüft explizit, dass exportierte Produktmetadaten dieselbe `VERSION`-Konstante verwenden
- historischen `services/release-04.js`-Override an die kanonische `VERSION` gebunden
- `DB_VERSION=2` bewusst unverändert gelassen, da Produktversion und IndexedDB-Schema getrennte Verträge sind
- README und TODO von der zuvor dokumentierten Versionsdrift bereinigt
- versehentliche Nebenänderung an der HTML-Escaping-Funktion im Entwicklungszweig per Commit-Diff erkannt und vor Freigabe vollständig zurückgenommen

Die formale Produktversion bleibt bis zum Abschluss des 0.5.1-Releaseblocks bei 0.5.0.

## 0.5.0 – TAURI-SIDECAR-INTEGRATION & REPOSITORY-KONSOLIDIERUNG

- reproduzierbaren whisper.cpp-Runtimevertrag mit festem Upstream-Tag und Commit eingeführt
- Linux-/Windows-Zielplattformen und Tauri-konforme Sidecar-Dateinamen definiert
- `tauri-plugin-shell` und `bundle.externalBin` integriert
- Tauri-Sidecar `naqya-whisper` gegenüber externem `whisper-cli`-Fallback priorisiert
- Runtime-Diagnose für Sidecar/Fallback ergänzt
- Linux-x86_64-Sidecar im CI real gebaut und per SHA-256 geprüft
- ungeprüfte Laufzeit-Downloads für kritische Runtimeartefakte ausgeschlossen
- temporäre STT-WAV-Dateien im privaten Tauri-App-Cache abgesichert
- `AGENTS.md` und `TODO.md` als verbindliche Projektsteuerung eingeführt
- Repository-/Merge-/CI-Abgleich vor und nach jeder Iteration vorgeschrieben
- veralteten, durch spätere Entwicklung ersetzten PR #3 geschlossen
- `.gitignore` für Sidecar-Builds, Tauri-Targets, lokale Sprachmodelle und temporäre Dateien ergänzt
- Versions-, Projektstatus-, Tauri- und Service-Worker-Metadaten auf 0.5.0 konsolidiert
- mergebedingte doppelte README-/TODO-Blöcke entfernt
- doppelte bzw. widersprüchliche JSON-Schlüssel in `VERSION.json` und `PROJEKTSTATUS.json` beseitigt
- veraltete Sidecar-/Native-STT-Dokumentation korrigiert und historische 0.2-/0.3-/0.4-Verträge gekennzeichnet
- Textintegritätsprüfung gegen Merge-Konfliktmarker, doppelte JSON-Schlüssel und zentrale Dokumentationsdrift ergänzt
- `CONTRIBUTING.md` als kompakter GitHub-Einstieg für fremde Entwickler ergänzt
- `docs/ENTWICKLERDOKUMENTATION.md` mit Repository-Landkarte, Vertrauensgrenzen, lokalen Prüfungen, Fehlerdiagnose und konkretem 0.5.1-Übergabepunkt ergänzt
- TODO um eine dauerhaft nutzbare Entwickler-Übergabecheckliste erweitert
- wenige schwer erkennbare Architektur-/Sicherheitsinvarianten direkt im Code mit `ENTWICKLERHINWEIS` markiert
- Entwicklerdokumentation und Übergabeverträge in die automatischen Text-/Statikprüfungen aufgenommen
- beim Entwickleraudit eine Produktversionsdrift in `app.js` erkannt; Korrektur erfolgte anschließend in 0.5.1-A

Bekannte Grenzen:
- Windows-x86_64-Sidecar benötigt noch vollständige Build-/Bundle-/Hardwareabnahme
- reale Linux-Hardware-/Mikrofonabnahme steht noch aus
- AudioWorklet-Umstellung und Langzeittests folgen

## 0.4.0 – AUDIO NORMALISIERUNG, MODELLPFAD & LIVE-SEGMENT-STT

- lokale Web-Audio-Normalisierung auf 16 kHz, Mono, PCM16/WAV
- native Live-STT arbeitet mit 4-Sekunden-PCM-Segmenten
- Originalaufnahme und 3-Sekunden-Recovery bleiben parallel aktiv
- segmentierte whisper.cpp-Aufrufe werden über eine lokale Warteschlange serialisiert
- Audiozeit, Transkriptionszeit, Segmentzahl und Echtzeitfaktor werden pro Sitzung erfasst
- importierte `.bin`/`.gguf`-Modelle werden speicherschonend in 4-MiB-Blöcken in den nativen NAQYA-Modellpfad übertragen
- native SHA-256-Prüfung vor Aktivierung eines Sprachmodells
- atomare Modellaktivierung nach erfolgreicher Integritätsprüfung
- abgebrochene Modelltransfers werden bereinigt
- native Transkription akzeptiert nur Modelle innerhalb des geschützten NAQYA-Modellpfads
- WAV-Header wird vor whisper.cpp-Aufruf validiert
- Fähigkeiten-Diagnose fragt reale Tauri-/whisper.cpp-Fähigkeiten ab
- GitHub Actions um Rust/Tauri-Kompilierungsprüfung erweitert

## 0.3.0 – NATIVE WHISPER RUNTIME & DESKTOP BRIDGE

- Tauri-2-Desktop-Grundstruktur für Linux/Windows ergänzt
- native JavaScript↔Rust-Brücke für Fähigkeiten und Transkription
- kontrollierte `whisper-cli`-Erkennung und `NAQYA_WHISPER_CLI` unterstützt
- Größenbegrenzung und Fehlerbehandlung für native Einzeltranskription
- STT-Core und Offline-Service-Worker auf Native-Bridge erweitert

## 0.2.0 – AUDIO & OFFLINE-STT CORE

- persistente Audioaufnahme in 3-Sekunden-Segmenten
- Crash-/Unterbrechungs-Recovery
- Providervertrag für Browser-On-Device-STT und native whisper.cpp-Brücke
- lokale Sprachmodellprofile und SHA-256-Modellimport
- vollständiges Backup von Metadaten und Binärdateien

## 0.1.0 – OFFLINE FUNDAMENT PRO

- erste lauffähige Offline-PWA
- responsive Oberfläche, IndexedDB-Datenkern und Dashboard
- Audio-Memo-Aufnahme, lokale Suche und PWA-Service-Worker
- Linux-/Windows-Starter und statische GitHub-Actions-Prüfung
