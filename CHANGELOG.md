# Änderungsprotokoll

## 0.5.1-C – DIAGNOSE, LOGGING & EVIDENCE-BINDUNG

- kanonischen `diagnostics/DIAGNOSTICS_CONTRACT.json` eingeführt
- stabiles Fehlercode- und Ereignisschema mit Format `NAQYA-DIAGNOSTICS` und Schema-Version 1 festgelegt
- fail-safe Offline-Diagnosemodul `services/diagnostics.js` integriert
- Ringpuffer auf maximal 200 bereits bereinigte Ereignisse begrenzt
- 5-Sekunden-Deduplizierung mit `repeat_count` ergänzt
- sensible Audio-, Transkript-, Dokument-, Secret-, Token- und vollständige Benutzerpfaddaten aus Standarddiagnosen ausgeschlossen
- laienverständlichen Diagnose-/Fehlerdialog sowie JSON-/TXT-Export integriert
- sichere Aktionen registriert; `retry-once` maximal einmal pro Ereignis
- Native-Bridge- und Live-STT-Fehlerpfade mit stabilen NAQYA-Codes instrumentiert
- Diagnosevertrag in Offline-Cache und deterministisches Desktop-`dist/` aufgenommen
- `RELEASE_EVIDENCE.json` an exakten Diagnosevertrag per SHA-256 gebunden
- Laufzeit- und statische Regressionstests für Ringpuffer, Deduplizierung, Privacy und Retry-once ergänzt
- Qualitätsprüfung #268 und Linux-Bundle-Nachweis #14 für Head `0388cda77c6696017c5b00cb795f5758af2d5e22` erfolgreich
- validierter Diagnose-Contract-SHA-256: `fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425`
- Entwicklungsfortschritt nach vollständiger Validierung von 56 % / 5 von 9 auf 78 % / 7 von 9 angehoben

### Plattformvertrag für 0.5.1-D

- Linux und Windows müssen bytegenau denselben Diagnosevertrag verwenden
- `tests/validate_platform_diagnostics.py` verriegelt Contract-SHA, Schema und Ereignisschema
- `NAQYA-STT-4002` ist als expliziter plattformübergreifender Semantikanker regressionsgesichert
- Windows-Port darf Paketierung und Adapter erweitern, aber vorhandene Diagnosecodes nicht umdeuten

## 0.5.1-B1 – DETERMINISTISCHE DEB-REPRODUZIERBARKEIT

- deterministisches DEB-Repacking mit festem `SOURCE_DATE_EPOCH`
- Release Evidence um Reproduzierbarkeitsdaten erweitert
- Regressionstest für byteidentische DEB-Reproduktion ergänzt
- Linux-Bundle-Workflow auf den deterministischen Paketpfad umgestellt

## 0.5.1-B – LINUX-BUNDLE & RELEASE-NACHWEIS

- Tauri-`frontendDist` auf deterministisch gestagtes `../dist` umgestellt
- Runtime-Allowlist und `BUILD_MANIFEST.json` mit SHA-256 ergänzt
- whisper.cpp mit `BUILD_SHARED_LIBS=OFF` paketierbar gehärtet
- Linux-DEB im CI gebaut, extrahiert und Sidecar aus Paketkontext gestartet
- Laufzeitabhängigkeiten mit `ldd` geprüft
- Build- und Paket-Sidecar per SHA-256 abgeglichen
- `RELEASE_EVIDENCE.schema.json`, JSON- und Textnachweis eingeführt

## 0.5.1-A – PRODUKTVERSIONS-KONSISTENZ

- PWA-Produktversion auf 0.5.0 synchronisiert
- Gleichheit mit `VERSION.json` regressionsgesichert
- Backup-Metadaten an dieselbe Produktversion gebunden
- historischen 0.4.0-Runtimeoverride gegen Versionsdrift gehärtet
- `DB_VERSION=2` bewusst unverändert gelassen, da Produktversion und Datenbankschema getrennte Verträge sind

## 0.5.0 – TAURI-SIDECAR-INTEGRATION & REPOSITORY-KONSOLIDIERUNG

- Tauri-2-Desktop-Grundstruktur und whisper.cpp-Sidecar integriert
- Upstream auf `v1.9.2`, Commit `306c88f4d1286aec1bf96e544632897886af5501` gepinnt
- Sidecar gegenüber externem `whisper-cli` priorisiert
- Modellpfad, Temp-Audio und Runtime-Fallbacks gehärtet
- Repository-, Merge-, CI- und Entwicklerübergabeverträge eingeführt
- doppelte README-/TODO-/JSON-Mergefehler bereinigt

## 0.4.0 – AUDIO NORMALISIERUNG, MODELLPFAD & LIVE-SEGMENT-STT

- 16 kHz / Mono / PCM16-WAV-Normalisierung
- 4-Sekunden-Live-STT-Segmente und geordnete Warteschlange
- geschützter nativer Modellpfad, SHA-256 und atomare Aktivierung
- Fähigkeiten-Diagnose und Rust/Tauri-Prüfung ergänzt

## 0.3.0 – NATIVE WHISPER RUNTIME & DESKTOP BRIDGE

- Tauri-Desktop-Brücke und native Transkriptionscommands
- kontrollierte `whisper-cli`-Erkennung
- STT-Core auf Native Bridge erweitert

## 0.2.0 – AUDIO & OFFLINE-STT CORE

- persistente Audioaufnahme in 3-Sekunden-Segmenten
- Crash-/Unterbrechungs-Recovery
- lokaler STT-Providervertrag und Modellimport
- vollständiges Backup von Metadaten und Binärdateien

## 0.1.0 – OFFLINE FUNDAMENT PRO

- erste lauffähige Offline-PWA
- IndexedDB-Datenkern, Dashboard, Audio-Memos und lokale Suche
- Linux-/Windows-Starter und statische GitHub-Actions-Prüfung
