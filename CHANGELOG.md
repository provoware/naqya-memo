# Änderungsprotokoll

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
