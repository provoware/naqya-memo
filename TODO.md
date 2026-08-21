# TODO – NAQYA

Stand: 2026-08-21
Validierter Basisstand: **0.5.0 – Tauri-Sidecar-Integration & Repository-Konsolidierung**
Aktueller Arbeitsstand: **0.5.1-C – Diagnose, Logging & Evidence-Bindung**
Fortschritt 0.5.1: **78 % – 7 von 9 Hauptpunkten erledigt**
Nächster Entwicklungsblock: **0.5.1-D – Windows-x86_64-Bundle & plattformübergreifender Evidence-Nachweis**

## P0 – Freigabekritisch

### [offen] Diagnosevertrag auf Windows unverändert erzwingen
Komponente: Diagnose / Release / Plattformvertrag

Abnahmekriterien:
- Windows verwendet `diagnostics/DIAGNOSTICS_CONTRACT.json` unverändert
- erwarteter SHA-256: `fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425`
- Schema-Version 1 und Ereignisschema 1 bleiben identisch
- `NAQYA-STT-4002` und alle bestehenden Codes behalten plattformübergreifend dieselbe Bedeutung
- Windows-Release-Evidence enthält denselben Contract-SHA
- CI bricht bei stiller Contract-Abweichung hart ab
- ein notwendiger Vertragswechsel erfolgt nur als eigener versionierter Diagnosevertrag, niemals implizit im Windows-Build

## P1 – Hohe Priorität

### [offen] Windows-x86_64-Sidecar reproduzierbar bauen und bundeln
Komponente: whisper.cpp / Tauri / Windows

Abnahmekriterien:
- Build aus `ggml-org/whisper.cpp` `v1.9.2`, Commit `306c88f4d1286aec1bf96e544632897886af5501`
- Ziel `x86_64-pc-windows-msvc`
- Tauri-konformer Binärname `naqya-whisper-...exe`
- Sidecar-SHA-256 erzeugen und prüfen
- vollständiges Windows-Tauri-Bundle erzeugen
- `.exe`-Sidecar aus dem Paketkontext tatsächlich starten
- Runtime-Diagnose zeigt den Sidecar als bevorzugte Quelle
- Windows-Paket, Sidecar, Toolchain und Diagnosevertrag in Release Evidence aufnehmen

### [offen] Reale Linux-Desktop-Abnahme durchführen
Komponente: Linux / Mikrofon / STT

Abnahmekriterien:
- validiertes Desktop-Paket auf Referenzgerät installieren und starten
- gebündelter Sidecar wird real von NAQYA verwendet
- echtes Modell aus geschütztem NAQYA-Modellpfad funktioniert
- Mikrofonaufnahme und segmentiertes Live-Diktat funktionieren
- temporäre WAV-Dateien werden zuverlässig bereinigt
- Providerdiagnose zeigt `whisper.cpp-sidecar`
- kurze sowie mindestens 30-minütige Sitzung ohne Datenverlust
- absichtlich provozierte Diagnose-/Fehlercodes entsprechen dem Vertrag

### [offen] Reale Windows-Desktop-Abnahme durchführen
Komponente: Windows / Mikrofon / STT

Abnahmekriterien analog zur Linux-Abnahme, zusätzlich Prüfung des Windows-Pakets, `.exe`-Sidecars und des identischen Diagnosevertrags.

## P2 – Qualitätsausbau

### [offen] `ScriptProcessor` durch `AudioWorklet` ersetzen
Komponente: Web Audio / Live-STT

Abnahmekriterien:
- gleiche oder bessere 16-kHz-Mono-Normalisierung
- stabile Segmentbildung
- keine Regression bei Live-Diktat und Recovery
- Firefox- und Chrome-Kompatibilität geprüft
- Diagnosemetriken und Fehlercodes bleiben erhalten

### [offen] Langzeit- und Lasttests für Live-STT durchführen
Komponente: Performance / Stabilität

Abnahmekriterien:
- 30- und 60-Minuten-Diktatsitzungen ohne Segmentverlust
- CPU-/RAM-Verhalten dokumentiert
- Echtzeitfaktor pro Referenzmodell dokumentiert
- kontrolliertes Verhalten bei langsamer Transkription
- Diagnose-Ringpuffer bleibt begrenzt und performant

## P3 – Wartbarkeit

### [offen] Alte bereits erledigte Entwicklungszweige und überholte PRs bereinigen
Komponente: Repository-Hygiene

Abnahmekriterien:
- nur Zweige löschen, deren Inhalt nachweislich in `main` enthalten oder bewusst verworfen ist
- überholte Parallel-PRs nachvollziehbar schließen
- keine aktive oder ungeprüfte Arbeit entfernen
- nach Bereinigung offene PRs und Branchliste erneut prüfen

### [offen] Historischen Modulnamen `services/release-04.js` bewerten
Komponente: Wartbarkeit

Abnahmekriterien:
- feststellen, ob der Name nur historisch oder technisch störend ist
- keine reine Umbenennung ohne Nutzen
- bei Änderung HTML-, Service-Worker-, Staging-Allowlist, Tests und Modulreferenzen atomar anpassen

## Entwickler-Übergabecheckliste

### Aktuelle Übergabebereitschaft 0.5.1-C

- [x] professioneller Entwickler-Einstieg und technische Übergabedokumentation
- [x] PWA-/Backup-Produktversion gegen `VERSION.json` abgesichert
- [x] deterministisches Desktop-Frontend-`dist/`
- [x] Linux-DEB mit enthaltenem und startbarem Sidecar im CI nachgewiesen
- [x] Sidecar-Laufzeitabhängigkeiten und Bytegleichheit geprüft
- [x] deterministisches DEB-Repacking nachgewiesen
- [x] maschinen- und menschenlesbarer Release-Nachweis erzeugt
- [x] professionelles Diagnose-/Debugging-/Logging-Modul integriert
- [x] Ringpuffer, Deduplizierung, Privacy-Redaktion und `retry-once` real regressionsgetestet
- [x] Diagnosevertrag über SHA-256 mit Release Evidence verbunden
- [x] aktueller Contract-SHA: `fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425`
- [ ] Windows-x86_64-Bundle mit identischem Diagnosevertrag nachweisen
- [ ] reale Linux-/Windows-Hardwareabnahme abschließen

### Vor jeder künftigen Entwicklerübergabe

- [ ] realen `main`-Commit, offene PRs und CI-Stand geprüft
- [ ] README, TODO, CHANGELOG, Entwicklerdokumentation und maschinenlesbare Statusdateien gegen den Code geprüft
- [ ] neue oder veränderte Vertrauensgrenzen direkt am Code knapp und in der Fachdokumentation ausführlich erklärt
- [ ] Repository-Landkarte und lokale Befehle noch korrekt
- [ ] Qualitätsgate für den exakten Übergabe-Head vollständig grün
- [ ] paketbezogene Evidence bei Release-relevanten Änderungen geprüft
- [ ] Diagnose-Contract-SHA zwischen Plattformen geprüft
- [ ] nach Merge resultierenden `main` erneut geprüft

## Erledigt

### [erledigt] 0.5.1-C – Professionelles Diagnose-/Debugging-/Logging-Modul
Ergebnis:
- `diagnostics/DIAGNOSTICS_CONTRACT.json` als kanonischer versionierter Vertrag
- stabile NAQYA-Codefamilien für App, Daten, Audio, STT, Modell, Runtime, Bundle und Release
- `services/diagnostics.js` mit hart begrenztem Ringpuffer
- 5-Sekunden-Deduplizierung mit `repeat_count`
- Ereignis-ID, Korrelation und Parent-Beziehungen
- Privacy-Redaktion für Audio/Base64, Transkripte, Dokumentinhalte, Secrets/Tokens und Benutzerpfade
- menschenlesbarer Dialog mit sichtbarem Fehlercode und vorab registrierten Safe Actions
- JSON- und TXT-Diagnoseexport vollständig offline
- `retry-once` maximal einmal; keine automatische Retry-Endlosschleife
- Native-Bridge- und Live-STT-Fehlerpfade instrumentiert
- echter Node-Laufzeittest und statischer Diagnosevertrag grün

### [erledigt] 0.5.1-C – Diagnose-/Release-Evidence-Vertrag verbinden
Ergebnis:
- Release Evidence enthält Diagnoseformat, Schema, Ereignisschema und Contract-SHA
- Runtime-Diagnoseexporte führen denselben Contract-SHA mit
- Linux-Bundle-Nachweis Run #14 bindet Contract-SHA `fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425`
- Qualitätsprüfung #268 und Bundle-Nachweis #14 für Quellcommit `0388cda77c6696017c5b00cb795f5758af2d5e22` erfolgreich
- Kette Build → Paket → Sidecar → Diagnosevertrag → Ereigniscode → sichere Benutzeraktion maschinenlesbar nachvollziehbar

### [erledigt] 0.5.1-B1 – Deterministische DEB-Reproduzierbarkeit
Ergebnis:
- DEB-Zeit-/Archivmetadaten normalisiert
- festes `SOURCE_DATE_EPOCH`
- deterministisches `dpkg-deb`-Profil
- Regressionstest verlangt Bytegleichheit normalisierter Pakete

### [erledigt] 0.5.1-B – Deterministisches Desktop-Frontend, Linux-Bundle & Release-Nachweis
Ergebnis:
- Tauri `frontendDist` auf `../dist`
- explizite Runtime-Allowlist
- `BUILD_MANIFEST.json` mit Dateigröße und SHA-256
- reales Linux-DEB mit startbarem Sidecar
- Laufzeitabhängigkeiten und Bytegleichheit geprüft
- `RELEASE_EVIDENCE.json` und `RELEASE_EVIDENCE.txt`

### [erledigt] 0.5.1-A – PWA-Produktversion atomar synchronisieren
Ergebnis:
- `app.js` verwendet Produktversion 0.5.0
- PWA-/Backup-Version gegen `VERSION.json` automatisiert abgesichert
- historischer `release-04.js`-Override an kanonische `VERSION` gebunden
- `DB_VERSION=2` als separates IndexedDB-Schema unverändert

### [erledigt] Repository-Konsolidierung und Entwicklerübergabe 0.5.0
Ergebnis:
- Tauri-Sidecar-Integration, Dokumentations- und Mergeverträge
- `AGENTS.md`, `TODO.md`, `CONTRIBUTING.md` und Entwicklerdokumentation
- Text-/Duplicate-Key-/Merge-Integritätsprüfungen
- reproduzierbarer whisper.cpp-Runtimevertrag und native Runtime-Härtung

## Pflegevertrag

Diese Datei wird bei jeder relevanten funktionalen, technischen, sicherheitsrelevanten, Build-, CI-, Release- oder Architekturänderung geprüft und aktualisiert. Vor und nach jeder Iteration wird der reale Repository-, PR-, Merge- und CI-Stand geprüft. Erledigte Punkte werden nicht kommentarlos gelöscht, sondern hier nachvollziehbar dokumentiert.
