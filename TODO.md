# TODO – NAQYA

Stand: 2026-08-21
Validierter Basisstand: **0.5.1-C – Diagnose, Logging & Evidence-Bindung**
Aktueller Arbeitsstand: **0.5.1-C – Diagnosevertrag und Linux-Bundle CI-validiert**
Fortschritt 0.5.1: **78 % – 7 von 9 Hauptpunkten erledigt**
Nächster Entwicklungsblock: **0.5.1-D – Windows-Bundle mit identischem Diagnosevertrag**

## P0 – Freigabekritisch

### [offen] Windows-x86_64-Sidecar reproduzierbar bauen und bundeln
Komponente: whisper.cpp / Tauri / Windows / Diagnose

Abnahmekriterien:
- Build aus demselben fest gepinnten whisper.cpp-Upstream `v1.9.2` / Commit `306c88f4d1286aec1bf96e544632897886af5501`
- Tauri-konformer `.exe`-Sidecarname
- vollständiges Windows-Bundle erzeugen
- Sidecar aus dem erzeugten Paketkontext tatsächlich starten
- SHA-256 für Paket und Sidecar im Release Evidence führen
- Runtime-Diagnose zeigt den gebündelten Sidecar als bevorzugte Quelle
- `diagnostics/DIAGNOSTICS_CONTRACT.json` bleibt bytegenau unverändert
- erwarteter Diagnose-Contract-SHA-256: `fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425`
- Schema-Version `1` und Ereignisschema-Version `1` bleiben identisch
- vorhandene Fehlercodes werden unter Windows nicht umgedeutet oder wiederverwendet
- Windows-Release-Evidence bindet denselben Contract-SHA wie der validierte Linux-Nachweis

### [offen] Reale Linux-/Windows-Hardwareabnahme abschließen
Komponente: Desktop / Mikrofon / STT / Diagnose

Abnahmekriterien:
- validierte Pakete auf realen Referenzgeräten installieren und starten
- gebündelter Sidecar wird tatsächlich verwendet
- echtes Modell aus geschütztem NAQYA-Modellpfad funktioniert
- Mikrofonaufnahme und segmentiertes Live-Diktat funktionieren
- temporäre WAV-Dateien werden zuverlässig bereinigt
- Providerdiagnose zeigt `whisper.cpp-sidecar`
- absichtlich provozierte Fehler ergeben auf Linux und Windows dieselben NAQYA-Codes bei gleicher Ursache
- mindestens 30-minütige Sitzung ohne Datenverlust

## P1 – Hohe Priorität

### [offen] Windows-Release-Nachweis gegen Linux-Vertrag vergleichen
Komponente: Release / Diagnose / Nachweisbarkeit

Abnahmekriterien:
- Windows Evidence enthält Plattform, Architektur, Paket- und Sidecar-SHA
- Diagnosevertrag-SHA ist exakt `fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425`
- Ereignisschema und Safe Actions stimmen bytegenau mit Linux überein
- CI bricht bei stiller Contract-Drift ab

### [offen] Reale Linux-Desktop-Abnahme durchführen
Komponente: Linux / Mikrofon / STT

### [offen] Reale Windows-Desktop-Abnahme durchführen
Komponente: Windows / Mikrofon / STT

## P2 – Qualitätsausbau

### [offen] `ScriptProcessor` durch `AudioWorklet` ersetzen
Komponente: Web Audio / Live-STT

Abnahmekriterien:
- gleiche oder bessere 16-kHz-Mono-Normalisierung
- stabile Segmentbildung
- keine Regression bei Live-Diktat und Recovery
- Diagnosemetriken bleiben erhalten

### [offen] Langzeit- und Lasttests für Live-STT durchführen
Komponente: Performance / Stabilität

Abnahmekriterien:
- 30- und 60-Minuten-Diktatsitzungen ohne Segmentverlust
- CPU-/RAM-Verhalten dokumentiert
- Echtzeitfaktor pro Referenzmodell dokumentiert
- Diagnose-Ringpuffer bleibt begrenzt und performant

## P3 – Wartbarkeit

### [offen] Alte erledigte Entwicklungszweige auf GitHub entfernen
Komponente: Repository-Hygiene

### [offen] Historischen Modulnamen `services/release-04.js` bewerten
Komponente: Wartbarkeit

## Entwickler-Übergabecheckliste

### Aktuelle Übergabebereitschaft 0.5.1-C

- [x] `CONTRIBUTING.md` und `docs/ENTWICKLERDOKUMENTATION.md` vorhanden
- [x] Produktversion und Backup-Metadaten konsistent
- [x] deterministisches Desktop-Frontend-`dist/` geprüft
- [x] Linux-DEB mit enthaltenem und startbarem Sidecar im CI nachgewiesen
- [x] Release Evidence erzeugt
- [x] professionelles Diagnose-/Debugging-/Logging-Modul integriert
- [x] Diagnose-/Release-Evidence-Vertrag verbunden
- [x] Diagnose-Contract-SHA `fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425` als plattformübergreifende Referenz festgelegt
- [ ] Windows-x86_64-Bundle nachweisen
- [ ] reale Linux-/Windows-Hardwareabnahme abschließen

### Vor jeder künftigen Entwicklerübergabe

- [ ] realen `main`-Commit, offene PRs und CI-Stand geprüft
- [ ] README, TODO, CHANGELOG, Entwicklerdokumentation und maschinenlesbare Statusdateien gegen den Code geprüft
- [ ] neue oder veränderte Vertrauensgrenzen dokumentiert
- [ ] Repository-Landkarte und lokale Befehle noch korrekt
- [ ] Qualitätsgate für den exakten Übergabe-Head vollständig grün
- [ ] paketbezogene Evidence bei Release-relevanten Änderungen geprüft
- [ ] nach Merge resultierenden `main` erneut geprüft

## Erledigt

### [erledigt] 0.5.1-C – Professionelles Diagnose-/Debugging-/Logging-Modul integrieren
Ergebnis:
- `diagnostics/DIAGNOSTICS_CONTRACT.json` als kanonischer Maschinenvertrag
- fail-safe Offline-Diagnosemodul mit maximal 200 bereinigten Ereignissen
- 5-Sekunden-Deduplizierung und `repeat_count`
- Privacy-Redaction für sensible Nutzdaten
- laienverständlicher Fehlerdialog und JSON-/TXT-Export
- Safe Actions mit maximal einmaligem `retry-once`
- Native-Bridge- und Live-STT-Instrumentierung mit stabilen NAQYA-Codes

### [erledigt] 0.5.1-C – Diagnose-/Release-Evidence-Vertrag verbinden
Ergebnis:
- Release Evidence bindet Diagnosevertrag per SHA-256
- Schema und Ereignisschema versioniert
- Diagnose-Laufzeitregression und statischer Vertragstest im Qualitätsgate
- validierter Contract-SHA: `fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425`
- Qualitätsprüfung #268 und Linux-Bundle-Nachweis #14 erfolgreich

### [erledigt] 0.5.1-B – Deterministisches Desktop-Frontend stagen
### [erledigt] 0.5.1-B – Linux-Tauri-Bundle und Sidecar paketbezogen validieren
### [erledigt] 0.5.1-B – Release-Nachweis erzeugen
### [erledigt] 0.5.1-A – PWA-Produktversion atomar synchronisieren
### [erledigt] Professionelle Entwicklerübergabe 0.5.0 aufbauen
### [erledigt] Repository-Konsolidierung 0.5.0
### [erledigt] Reproduzierbaren whisper.cpp-Runtimevertrag festlegen
### [erledigt] Native Runtime-Sicherheit härten

## Pflegevertrag

Diese Datei wird bei jeder relevanten funktionalen, technischen, sicherheitsrelevanten, Build-, CI-, Release- oder Architekturänderung geprüft und aktualisiert. Vor und nach jeder Iteration wird der reale Repository-, PR-, Merge- und CI-Stand geprüft. Erledigte Punkte werden nachvollziehbar dokumentiert.
