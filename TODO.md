# TODO – NAQYA

Stand: 2026-08-21
Validierter Basisstand: **0.5.0 – Tauri-Sidecar-Integration & Repository-Konsolidierung**
Aktueller Arbeitsstand: **0.5.1-B – Linux-Bundle & Release-Nachweis**
Fortschritt 0.5.1: **56 % – 5 von 9 Hauptpunkten erledigt**
Nächster Entwicklungsblock: **0.5.1-C – Diagnose, Debugging, Logging & Evidence-Bindung**

## P0 – Freigabekritisch

### [offen] Professionelles Diagnose-/Debugging-/Logging-Modul integrieren
Komponente: Diagnose / UX / Wartbarkeit / Regression

Abnahmekriterien:
- zentrale Ereignisstruktur mit stabilen Codefamilien
- jedes relevante Ereignis beschreibt mindestens: Was, Wann, Wo, Wie, Ergebnis
- menschenlesbare Kurzbeschreibung und maschinenlesbare JSON-Struktur aus derselben Quelle
- begrenzter Ringpuffer statt unbegrenztem Logwachstum
- wiederholte identische Fehler werden kontrolliert dedupliziert bzw. gezählt
- Loggingfehler dürfen den eigentlichen Produktablauf nicht zum Absturz bringen
- keine Audio-, Transkript-, Dokumentinhalte oder unnötigen vollständigen Dateipfade im Standardlog
- Export als Diagnose-JSON und menschenlesbarer Textbericht
- laienverständlicher Fehlerdialog mit sichtbarem Fehlercode
- nur vorab registrierte sichere Benutzeraktionen wie „Erneut versuchen“, „Diagnose anzeigen“, „Einstellungen öffnen“, „Schließen“
- kein automatischer unendlicher Retry
- Regressionstests für Fehlercode-Eindeutigkeit, Deduplizierung, Puffergrenze und Offline-Verhalten

### [offen] Diagnose-/Release-Evidence-Vertrag verbinden
Komponente: Release / Diagnose / Nachweisbarkeit

Abnahmekriterien:
- Ereignis- und Fehlercode-Schema versionieren
- `RELEASE_EVIDENCE.json` referenziert die verwendete Diagnose-Schema-Version
- Laufzeitdiagnosen enthalten Release-/Build-Identität ohne sensible Nutzdaten
- Beziehung Build → Paket → Sidecar → Runtime → Ereigniscode → sichere Benutzeraktion maschinenlesbar abbildbar
- Evidence- und Diagnose-IDs dürfen nicht zufällig kollidieren
- Export muss vollständig offline funktionieren
- statische und Laufzeittests verhindern stille Schema-Drift

## P1 – Hohe Priorität

### [offen] Windows-x86_64-Sidecar reproduzierbar bauen und bundeln
Komponente: whisper.cpp / Tauri / Windows

Abnahmekriterien:
- Build aus demselben fest gepinnten Upstream-Commit
- Tauri-konformer Binärname
- SHA-256-Nachweis
- vollständiges Windows-Bundle erzeugen
- `.exe`-Sidecar aus dem Bundle tatsächlich starten
- Runtime-Diagnose zeigt den Sidecar als bevorzugte Quelle
- Windows-Paket und Sidecar in den Release-Nachweis aufnehmen

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
- Diagnose-/Fehlercodes bei absichtlich provozierten Fehlerfällen verifizieren

### [offen] Reale Windows-Desktop-Abnahme durchführen
Komponente: Windows / Mikrofon / STT

Abnahmekriterien analog zur Linux-Abnahme, zusätzlich Prüfung des Windows-Pakets und des `.exe`-Sidecars.

## P2 – Qualitätsausbau

### [offen] `ScriptProcessor` durch `AudioWorklet` ersetzen
Komponente: Web Audio / Live-STT

Abnahmekriterien:
- gleiche oder bessere 16-kHz-Mono-Normalisierung
- stabile Segmentbildung
- keine Regression bei Live-Diktat und Recovery
- Firefox- und Chrome-Kompatibilität geprüft
- Diagnosemetriken bleiben erhalten

### [offen] Langzeit- und Lasttests für Live-STT durchführen
Komponente: Performance / Stabilität

Abnahmekriterien:
- 30- und 60-Minuten-Diktatsitzungen ohne Segmentverlust
- CPU-/RAM-Verhalten dokumentiert
- Echtzeitfaktor pro Referenzmodell dokumentiert
- kontrolliertes Verhalten bei langsamer Transkription
- Diagnose-Ringpuffer bleibt begrenzt und performant

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
- bei Änderung HTML-, Service-Worker-, Staging-Allowlist, Tests und Modulreferenzen atomar anpassen

## Entwickler-Übergabecheckliste

### Aktuelle Übergabebereitschaft 0.5.1-B

- [x] `CONTRIBUTING.md` als kurzer GitHub-Einstieg angelegt
- [x] `docs/ENTWICKLERDOKUMENTATION.md` mit Schnellübernahme, Repository-Landkarte und exakten lokalen Prüfungen angelegt
- [x] aktuelle Architektur-, Daten-, STT- und Sidecar-Verträge verlinkt und voneinander abgegrenzt
- [x] schwer erkennbare Invarianten an Native Bridge, Live-STT, Audio-Normalisierung, Rust-Runtime und Sidecar-Build sparsam direkt im Code markiert
- [x] Dokumentations- und Kommentierregeln in `AGENTS.md` verbindlich festgelegt
- [x] Entwicklerdokumentation in Text-/Statikverträge aufgenommen
- [x] PWA-Produktversionsdrift in `app.js` auf 0.5.0 korrigiert und gegen `VERSION.json` automatisiert abgesichert
- [x] deterministisches Desktop-Frontend-`dist/` erzeugt und geprüft
- [x] Linux-DEB mit enthaltenem und startbarem Sidecar im CI nachgewiesen
- [x] Sidecar-Laufzeitabhängigkeiten im Paketkontext ohne fehlende Bibliotheken geprüft
- [x] maschinen- und menschenlesbaren Release-Nachweis erzeugt
- [ ] professionelles Diagnose-/Debugging-/Logging-Modul vollständig integrieren
- [ ] Diagnose-/Release-Evidence-Vertrag verbinden
- [ ] Windows-x86_64-Bundle nachweisen
- [ ] reale Linux-/Windows-Hardwareabnahme abschließen

### Vor jeder künftigen Entwicklerübergabe

- [ ] realen `main`-Commit, offene PRs und CI-Stand geprüft
- [ ] README, TODO, CHANGELOG, Entwicklerdokumentation und maschinenlesbare Statusdateien gegen den Code geprüft
- [ ] neue oder veränderte Vertrauensgrenzen direkt am Code knapp und in der Fachdokumentation ausführlich erklärt
- [ ] Repository-Landkarte und lokale Befehle noch korrekt
- [ ] Qualitätsgate für den exakten Übergabe-Head vollständig grün
- [ ] paketbezogene Evidence bei Release-relevanten Änderungen geprüft
- [ ] nach Merge resultierenden `main` erneut geprüft

## Erledigt

### [erledigt] 0.5.1-B – Deterministisches Desktop-Frontend stagen
Ergebnis:
- Tauri `frontendDist` von Repository-Stamm auf `../dist` umgestellt
- explizite Runtime-Allowlist eingeführt
- Symlinks im Staging verboten
- `BUILD_MANIFEST.json` mit Dateigröße und SHA-256 erzeugt
- Tests verhindern zusätzliche oder fehlende Runtime-Dateien im `dist/`

### [erledigt] 0.5.1-B – Linux-Tauri-Bundle und Sidecar paketbezogen validieren
Ergebnis:
- reales DEB im GitHub-Actions-Workflow gebaut
- whisper.cpp-Sidecar mit `BUILD_SHARED_LIBS=OFF` paketierbar gehärtet
- DEB extrahiert und genau einen `naqya-whisper` nachgewiesen
- Sidecar aus dem Paketkontext erfolgreich gestartet
- Laufzeitabhängigkeiten mit `ldd` geprüft; keine `not found`-Abhängigkeit
- Build- und Paket-Sidecar per SHA-256 bytegenau abgeglichen

### [erledigt] 0.5.1-B – Release-Nachweis erzeugen
Ergebnis:
- `RELEASE_EVIDENCE.schema.json` versioniert
- `RELEASE_EVIDENCE.json` im realen Bundle-Workflow erzeugt und validiert
- menschenlesbaren `RELEASE_EVIDENCE.txt` erzeugt
- Paket-, Sidecar-, Frontend-Manifest-, Toolchain-, Zielplattform- und CI-Identität dokumentiert
- erstes erfolgreiches Nachweisartefakt: `naqya-linux-bundle-nachweis-1`, Run-ID `32477864231`

### [erledigt] 0.5.1-A – PWA-Produktversion atomar synchronisieren
Ergebnis:
- `app.js` verwendet Produktversion 0.5.0
- `tests/validate_text_integrity.py` verlangt harte Gleichheit mit `VERSION.json`
- Backup-Metadaten verwenden dieselbe `VERSION`-Konstante und werden im Vertrag geprüft
- historischer `release-04.js`-Override kann UI und Backup nicht mehr still auf 0.4.0 zurücksetzen
- `DB_VERSION=2` blieb unverändert, weil Datenbankschema und Produktversion getrennte Verträge sind

### [erledigt] Professionelle Entwicklerübergabe 0.5.0 aufbauen
Ergebnis:
- GitHub-Einstieg über `CONTRIBUTING.md`
- kanonische technische Übergabe unter `docs/ENTWICKLERDOKUMENTATION.md`
- Repository-Landkarte, Vertrauensgrenzen, lokale Prüfmatrix und Übergabepunkt dokumentiert
- Codekommentare auf wenige nicht offensichtliche Architektur-/Sicherheitsinvarianten beschränkt
- Übergabecheckliste und verbindliche Pflegeverträge ergänzt

### [erledigt] Mergebedingte Text- und Metadatenfehler nach Repository-Konsolidierung reparieren
Ergebnis:
- doppelte README-Abschnitte entfernt
- doppelte bzw. widersprüchliche TODO-Blöcke konsolidiert
- doppelte JSON-Schlüssel aus `VERSION.json` und `PROJEKTSTATUS.json` entfernt
- veraltete Sidecar-Dokumentation korrigiert
- historische 0.2-/0.3-/0.4-Dokumente klar als historische Verträge gekennzeichnet
- automatischer Textintegritäts- und Duplicate-Key-Test ergänzt

### [erledigt] Repository-Konsolidierung 0.5.0
Ergebnis:
- Tauri-Sidecar-Integration in `main`
- veraltete Parallelentwicklung geschlossen
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

Diese Datei wird bei jeder relevanten funktionalen, technischen, sicherheitsrelevanten, Build-, CI-, Release- oder Architekturänderung geprüft und aktualisiert. Vor und nach jeder Iteration wird der reale Repository-, PR-, Merge- und CI-Stand geprüft. Erledigte Punkte werden nicht kommentarlos gelöscht, sondern hier nachvollziehbar dokumentiert.
