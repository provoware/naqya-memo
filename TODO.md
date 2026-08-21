# TODO – NAQYA

Stand: 2026-08-21
Validierter Basisstand: **0.5.0 – Tauri-Sidecar-Integration & Repository-Konsolidierung**
Nächster Entwicklungsblock: **0.5.1 – Linux-Bundle-Abnahme, Release-Nachweis & Windows-Sidecar**

## P0 – Freigabekritisch

### [offen] Vollständiges Linux-Tauri-Bundle end-to-end validieren
Komponente: Tauri / Linux / Sidecar

Abnahmekriterien:
- reproduzierbaren Linux-x86_64-Sidecar aus dem fest gepinnten whisper.cpp-Commit bauen
- Tauri-Frontend deterministisch in einem eigenen Desktop-`dist/` bereitstellen
- `src-tauri/tauri.conf.json` nicht mehr auf den gesamten Repository-Stamm als `frontendDist` zeigen lassen
- vollständiges Linux-Desktop-Bundle erzeugen
- nachweisen, dass `naqya-whisper` im Bundle enthalten ist
- notwendige Sidecar-Laufzeitbibliotheken im Paketkontext prüfen
- gebündelten Sidecar aus dem erzeugten Paket tatsächlich starten
- Runtime-Diagnose meldet den Sidecar als bevorzugte Quelle
- kein stiller Rückfall auf PATH bei erfolgreichem Sidecar

### [offen] Release-Nachweis für Sidecar- und Desktop-Artefakte erzeugen
Komponente: Release / Integrität / Supply Chain

Abnahmekriterien:
- NAQYA-Version
- Zielplattform und Zielarchitektur
- whisper.cpp-Version und Upstream-Commit
- Sidecar-Dateiname und Dateigröße
- Sidecar-SHA-256
- Desktop-Paket-Dateiname, Dateigröße und SHA-256
- Compiler-/CMake-/Rust-/Tauri-Versionen
- Buildzeitpunkt und CI-Run-Zuordnung
- maschinenlesbares Nachweisformat

## P1 – Hohe Priorität

### [offen] PWA-Produktversionskonstante mit 0.5.0 synchronisieren
Komponente: PWA / Backup-Metadaten / Diagnose

Befund:
- `VERSION.json`, `PROJEKTSTATUS.json` und Tauri stehen auf 0.5.0
- `app.js` enthält derzeit noch `const VERSION='0.2.0'`
- diese Konstante erscheint in der UI und im exportierten Backupfeld `version`

Abnahmekriterien:
- `app.js` verwendet die reale Produktversion 0.5.0
- `DB_VERSION=2` bleibt unverändert, da dies ausschließlich das IndexedDB-Schema ist
- automatischer Test verhindert künftige Drift zwischen `app.js` und `VERSION.json`
- Backup-Kompatibilität bleibt unverändert; nur die Produktversionsmetadaten werden korrigiert

### [offen] Windows-x86_64-Sidecar reproduzierbar bauen und bundeln
Komponente: whisper.cpp / Tauri / Windows

Abnahmekriterien:
- Build aus demselben fest gepinnten Upstream-Commit
- Tauri-konformer Binärname
- SHA-256-Nachweis
- vollständiges Windows-Bundle erzeugen
- `.exe`-Sidecar aus dem Bundle tatsächlich starten
- Runtime-Diagnose zeigt den Sidecar als bevorzugte Quelle

### [offen] Reale Linux-Desktop-Abnahme durchführen
Komponente: Linux / Mikrofon / STT

Abnahmekriterien:
- Desktop-Paket auf Referenzgerät starten
- gebündelter Sidecar wird verwendet
- echtes Modell aus geschütztem NAQYA-Modellpfad funktioniert
- Mikrofonaufnahme und segmentiertes Live-Diktat funktionieren
- temporäre WAV-Dateien werden zuverlässig bereinigt
- Providerdiagnose zeigt `whisper.cpp-sidecar`
- kurze sowie mindestens 30-minütige Sitzung ohne Datenverlust

### [offen] Reale Windows-Desktop-Abnahme durchführen
Komponente: Windows / Mikrofon / STT

Abnahmekriterien analog zur Linux-Abnahme, zusätzlich Prüfung des Windows-Pakets und des `.exe`-Sidecars.

## P2 – Qualitätsausbau

### [offen] Runtime-Diagnose in der Oberfläche deutlicher darstellen
Komponente: UI / Diagnose

Abnahmekriterien:
- Sidecar / externer Fallback / nicht verfügbar klar unterscheidbar
- verwendeter Provider nach einer Transkription sichtbar
- laienverständliche Fehlermeldung mit konkretem nächsten Schritt
- Version und Integritätsstatus der Runtime darstellbar

### [offen] `ScriptProcessor` durch `AudioWorklet` ersetzen
Komponente: Web Audio / Live-STT

Abnahmekriterien:
- gleiche oder bessere 16-kHz-Mono-Normalisierung
- stabile Segmentbildung
- keine Regression bei Live-Diktat und Recovery
- Firefox- und Chrome-Kompatibilität geprüft

### [offen] Langzeit- und Lasttests für Live-STT durchführen
Komponente: Performance / Stabilität

Abnahmekriterien:
- 30- und 60-Minuten-Diktatsitzungen ohne Segmentverlust
- CPU-/RAM-Verhalten dokumentiert
- Echtzeitfaktor pro Referenzmodell dokumentiert
- kontrolliertes Verhalten bei langsamer Transkription

## P3 – Wartbarkeit

### [offen] Alte bereits erledigte Entwicklungszweige auf GitHub entfernen
Komponente: Repository-Hygiene

Abnahmekriterien:
- nur Zweige löschen, deren Inhalt nachweislich in `main` enthalten oder bewusst verworfen ist
- keine aktive oder ungeprüfte Arbeit entfernen
- nach Bereinigung offene PRs und Branchliste erneut prüfen

### [offen] Historischen Modulnamen `services/release-04.js` bewerten
Komponente: Wartbarkeit

Abnahmekriterien:
- feststellen, ob der Name nur historisch oder technisch störend ist
- keine reine Umbenennung ohne Nutzen
- bei Änderung HTML-, Service-Worker-, Test- und Modulreferenzen atomar anpassen

## Entwickler-Übergabecheckliste

### Aktuelle Übergabebereitschaft 0.5.0

- [x] `CONTRIBUTING.md` als kurzer GitHub-Einstieg angelegt
- [x] `docs/ENTWICKLERDOKUMENTATION.md` mit Schnellübernahme, Repository-Landkarte und exakten lokalen Prüfungen angelegt
- [x] aktuelle Architektur-, Daten-, STT- und Sidecar-Verträge verlinkt und voneinander abgegrenzt
- [x] nächster Arbeitsblock 0.5.1 mit konkreten Touchpoints und Nicht-Zielen dokumentiert
- [x] schwer erkennbare Invarianten an Native Bridge, Live-STT, Audio-Normalisierung, Rust-Runtime und Sidecar-Build sparsam direkt im Code markiert
- [x] Dokumentations- und Kommentierregeln in `AGENTS.md` verbindlich festgelegt
- [x] Entwicklerdokumentation in Text-/Statikverträge aufgenommen
- [ ] bekannte PWA-Produktversionsdrift in `app.js` von 0.2.0 auf 0.5.0 korrigieren und automatisiert absichern
- [ ] deterministisches Desktop-Frontend-`dist/` für 0.5.1 erzeugen
- [ ] vollständiges Linux-Endanwender-Bundle nachweisen
- [ ] maschinenlesbaren Release-Nachweis erzeugen
- [ ] Windows-x86_64-Bundle nachweisen
- [ ] reale Linux-/Windows-Hardwareabnahme abschließen

### Vor jeder künftigen Entwicklerübergabe

- [ ] realen `main`-Commit, offene PRs und CI-Stand geprüft
- [ ] README, TODO, CHANGELOG, Entwicklerdokumentation und maschinenlesbare Statusdateien gegen den Code geprüft
- [ ] neue oder veränderte Vertrauensgrenzen direkt am Code knapp und in der Fach­dokumentation ausführlich erklärt
- [ ] Repository-Landkarte und lokale Befehle noch korrekt
- [ ] Qualitätsgate für den exakten Übergabe-Head vollständig grün
- [ ] nach Merge resultierenden `main` erneut geprüft

## Erledigt

### [erledigt] Professionelle Entwicklerübergabe 0.5.0 aufbauen
Ergebnis:
- GitHub-Einstieg über `CONTRIBUTING.md`
- kanonische technische Übergabe unter `docs/ENTWICKLERDOKUMENTATION.md`
- Repository-Landkarte, Vertrauensgrenzen, lokale Prüfmatrix und 0.5.1-Übergabepunkt dokumentiert
- Codekommentare auf wenige nicht offensichtliche Architektur-/Sicherheitsinvarianten beschränkt
- Übergabecheckliste und verbindliche Pflegeverträge ergänzt

### [erledigt] Mergebedingte Text- und Metadatenfehler nach Repository-Konsolidierung reparieren
Ergebnis:
- doppelte README-Abschnitte entfernt
- doppelte bzw. widersprüchliche TODO-Blöcke konsolidiert
- doppelte JSON-Schlüssel aus `VERSION.json` und `PROJEKTSTATUS.json` entfernt
- veraltete Sidecar-Dokumentation korrigiert
- historische 0.2-/0.3-/0.4-Dokumente klar als historische Verträge gekennzeichnet
- README als kanonischer Gesamtstand aktualisiert
- automatischer Textintegritäts- und Duplicate-Key-Test ergänzt

### [erledigt] Repository-Konsolidierung 0.5.0
Ergebnis:
- PR #8 mit Tauri-Sidecar-Integration in `main`
- veralteter Parallel-PR #3 geschlossen
- `.gitignore` für Build-, Runtime- und Modellartefakte ergänzt
- Versions- und Tauri-Metadaten auf 0.5.0 angehoben

### [erledigt] Reproduzierbaren whisper.cpp-Runtimevertrag festlegen
Ergebnis:
- Upstream `ggml-org/whisper.cpp` auf Version `v1.9.2` und Commit `306c88f4d1286aec1bf96e544632897886af5501` fest gepinnt
- CPU-Releaseprofil mit `GGML_NATIVE=OFF`
- Linux-/Windows-Zielnamen definiert
- Laufzeit-Downloads und ungeprüfte Aktivierung ausgeschlossen

### [erledigt] Native Runtime-Sicherheit härten
Ergebnis:
- generische `main`-PATH-Erkennung entfernt
- `NAQYA_WHISPER_CLI` kanonisiert
- private STT-Tempdateien im Tauri-App-Cache
- kollisionsgeschützte Dateierzeugung
- `sync_all()` vor Übergabe an whisper.cpp

## Pflegevertrag

Diese Datei wird bei jeder relevanten funktionalen, technischen, sicherheitsrelevanten, Build-, CI-, Release- oder Architekturänderung geprüft und aktualisiert. Vor und nach jeder Iteration wird der reale Repository-, PR-, Merge- und CI-Stand geprüft. Erledigte Punkte werden nicht kommentarlos gelöscht, sondern zunächst hier dokumentiert.
