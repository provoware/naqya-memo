# Änderungsprotokoll

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
- Fähigkeiten-Diagnose fragt jetzt reale Tauri-/whisper.cpp-Fähigkeiten ab
- Offline-Service-Worker auf alle 0.4-Laufzeitmodule erweitert
- GitHub Actions um JavaScript-Prüfung aller neuen Module sowie Rust/Tauri-Kompilierungsprüfung erweitert
- bekannte Grenze: whisper.cpp wird noch nicht als reproduzierbares Sidecar mitgeliefert

## 0.3.0 – NATIVE WHISPER RUNTIME & DESKTOP BRIDGE

- Tauri-2-Desktop-Grundstruktur für Linux/Windows ergänzt
- native JavaScript↔Rust-Brücke für Fähigkeiten und Transkription
- `naqya_capabilities` erkennt Plattform, CPU-Anzahl und verfügbare whisper.cpp-CLI
- `naqya_transcribe` führt vollständig lokale whisper.cpp-Transkription über WAV + lokalen Modellpfad aus
- `NAQYA_WHISPER_CLI` als expliziter lokaler Runtime-Pfad unterstützt
- Größenbegrenzung und Fehlerbehandlung für native Einzeltranskription
- temporäre Audiodateien werden nach der Verarbeitung entfernt
- STT-Core auf die Tauri-Brücke erweitert
- Offline-Service-Worker auf Native-Bridge-Komponente aktualisiert
- statische Tests für Tauri-, Rust- und Native-Bridge-Verträge ergänzt
- bekannte Grenzen für WebM→WAV, Modellmaterialisierung und gebündelte Runtime transparent dokumentiert

## 0.2.0 – AUDIO & OFFLINE-STT CORE

- persistente Audioaufnahme in 3-Sekunden-Segmenten
- Crash-/Unterbrechungs-Recovery für Audio und Diktat
- finale Zusammenführung der Segmente zu einer lokalen Audiodatei
- direktes Abspielen gespeicherter Audio-/Diktateinträge
- Fähigkeiten-Diagnose für Offline-Funktionen
- Providervertrag für Browser-On-Device-STT und native whisper.cpp-Brücke
- vier lokale Sprachmodellprofile: Schnell, Ausgewogen, Genau, Maximum
- lokaler Import von `.bin`/`.gguf`-Modellen inklusive SHA-256
- vollständiges Backup von Metadaten und Binärdateien
- SHA-256-Validierung beim Backup-Import
- Legacy-Import von 0.1-Backups
- Anforderung persistenten Browserspeichers, sofern unterstützt
- Service-Worker-Cache auf neue 0.2-Komponenten erweitert
- bekannte Grenzen transparent im Projektstatus dokumentiert

## 0.1.0 – OFFLINE FUNDAMENT PRO

- erste lauffähige Offline-PWA
- responsive Desktop-/Tablet-/Mobil-Oberfläche
- vier Farbthemes und fünf Sichtbarkeitsprofile
- IndexedDB-Datenkern für Einträge, Projekte, Dateien und Einstellungen
- Dashboard, Heute, Kalender, Dokumente, Projekte, Audio, Chronologie, Suche und Einstellungen
- dreistufiger Schnellerfassungs-Wizard
- Dokument-/Fotoimport als Blob in IndexedDB
- Audio-Memo-Aufnahme mit MediaRecorder
- strikt lokales Browser-Live-Diktat per On-Device SpeechRecognition, sofern unterstützt; kein Cloud-Fallback
- lokales JSON-Metadatenbackup
- PWA-Service-Worker
- Linux-/Windows-Starter
- statische GitHub-Actions-Qualitätsprüfung
