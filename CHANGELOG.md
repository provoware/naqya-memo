# Änderungsprotokoll

## 0.3.0 – NATIVE WHISPER RUNTIME & DESKTOP BRIDGE

- Tauri-2-Desktopkern für Linux und Windows ergänzt
- echte lokale `whisper.cpp`-Runtime über `whisper-rs 0.16.0`
- thread-sicherer Kontextcache pro Sprachmodell
- nativer Status-/Diagnosebefehl mit Runtime-, Modell- und Threadinformationen
- native PCM-Transkription mit 16 kHz Mono und Segmentzeitstempeln
- Verarbeitungszeit und Echtzeitfaktor (RTF) je Transkriptionsblock
- AudioWorklet für Live-PCM mit kompatiblem ScriptProcessor-Fallback
- lineares lokales Resampling auf 16 kHz
- natives Live-Diktat priorisiert Desktop-Whisper vor Browser-On-Device-STT
- Originalaudio bleibt parallel in persistenten 3-Sekunden-Segmenten gesichert
- blockweiser nativer Modellimport mit 1-MiB-Frontendblöcken
- Größen- und SHA-256-Validierung vor Modellaktivierung
- persistenter lokaler Modellordner plus optionale Release-Modelle
- vier Leistungsprofile weiterhin unterstützt
- Fähigkeiten-Diagnose um Desktop-/Whisper-Status erweitert
- PWA-Offlinecache auf 0.3-Komponenten erweitert
- Linux-CI um `cargo check` für Tauri + whisper.cpp ergänzt
- bekannte Grenzen und nächster Härtungsmeilenstein dokumentiert

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
