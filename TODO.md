# TODO – NAQYA

Stand: 2026-08-21
Validierter Basisstand: **0.5.0 – Tauri-Sidecar-Integration & Repository-Konsolidierung**
Aktueller Arbeitsstand: **0.5.1-D – Windows-Bundle & Plattform-Evidence**
Fortschritt 0.5.1: **89 % – 8 von 9 Hauptpunkten erledigt**
Nächster Entwicklungsblock: **0.5.1-E – Reale Hardwareabnahme, AudioWorklet & Langzeithärtung**

## P0 – Freigabekritisch

### [offen] Reale Linux- und Windows-Desktop-Abnahme durchführen
Komponente: Hardware / Mikrofon / STT / Release

Abnahmekriterien:
- validierte Linux- und Windows-Pakete auf realen Referenzgeräten installieren und starten
- gebündelter `naqya-whisper` wird real von NAQYA verwendet
- echtes Modell aus dem geschützten NAQYA-Modellpfad funktioniert
- Mikrofonaufnahme und segmentiertes Live-Diktat funktionieren
- temporäre WAV-Dateien werden zuverlässig bereinigt
- Providerdiagnose zeigt `whisper.cpp-sidecar`
- absichtlich provozierte Diagnose-/Fehlercodes entsprechen dem unveränderten Diagnosevertrag
- Evidence-Fingerprint der getesteten Software wird in `HARDWARE_ACCEPTANCE.json` gebunden
- kurze sowie mindestens 30-minütige Sitzung ohne Datenverlust
- keine Hardware-Freigabe ohne real gemessenen und validierten Nachweis

## P1 – Hohe Priorität

### [offen] Langzeit- und Lasttests für Live-STT durchführen
Komponente: Performance / Stabilität

Abnahmekriterien:
- 30- und 60-Minuten-Diktatsitzungen ohne Segmentverlust
- CPU-/RAM-Verhalten dokumentiert
- Echtzeitfaktor pro Referenzmodell dokumentiert
- kontrolliertes Verhalten bei langsamer Transkription
- Diagnose-Ringpuffer bleibt begrenzt und performant
- Messwerte werden im Hardware-Abnahmevertrag erfasst

## P2 – Qualitätsausbau

### [offen] `ScriptProcessor` durch `AudioWorklet` ersetzen
Komponente: Web Audio / Live-STT

Abnahmekriterien:
- bestehende Hardware-/Performance-Baseline zuerst dokumentieren
- gleiche oder bessere 16-kHz-Mono-Normalisierung
- stabile Segmentbildung
- keine Regression bei Live-Diktat und Recovery
- Firefox- und Chrome-Kompatibilität geprüft
- Diagnosemetriken und Fehlercodes bleiben erhalten

## P3 – Wartbarkeit

### [offen] Alte erledigte Entwicklungszweige bereinigen
Komponente: Repository-Hygiene

Abnahmekriterien:
- nur Zweige löschen, deren Inhalt nachweislich in `main` enthalten oder bewusst verworfen ist
- keine aktive oder ungeprüfte Arbeit entfernen
- offene PRs und Branchliste danach erneut prüfen

### [offen] Historischen Modulnamen `services/release-04.js` bewerten
Komponente: Wartbarkeit

Abnahmekriterien:
- feststellen, ob der Name nur historisch oder technisch störend ist
- keine reine Umbenennung ohne Nutzen
- bei Änderung HTML-, Service-Worker-, Staging-Allowlist, Tests und Modulreferenzen atomar anpassen

## Entwickler-Übergabecheckliste

### Aktuelle Übergabebereitschaft 0.5.1-D / E1-Vertrag

- [x] professioneller Entwickler-Einstieg und technische Übergabedokumentation
- [x] PWA-/Backup-Produktversion gegen `VERSION.json` abgesichert
- [x] deterministisches Desktop-Frontend-`dist/`
- [x] Linux-DEB mit enthaltenem und startbarem Sidecar im CI nachgewiesen
- [x] Windows-NSIS mit enthaltenem und startbarem Sidecar im CI nachgewiesen
- [x] Sidecar-Laufzeitabhängigkeiten und Bytegleichheit geprüft
- [x] deterministisches DEB-Repacking nachgewiesen
- [x] maschinen- und menschenlesbarer Release-Nachweis erzeugt
- [x] Diagnosevertrag über SHA-256 mit Release Evidence verbunden
- [x] Linux-/Windows-Evidence automatisiert verglichen
- [x] plattformübergreifender Evidence-Fingerprint validiert: `018452a4b7683cba40dbce2a2c221aa6b31e55c846470baef35e4baa13081aaf`
- [x] Diagnose-Contract-SHA: `fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425`
- [x] maschinenlesbares Hardware-Abnahmeschema und Validator vorhanden
- [ ] reale Linux-/Windows-Hardware-, Mikrofon- und Langzeitabnahme abschließen

### Vor jeder künftigen Entwicklerübergabe

- [ ] realen `main`-Commit, offene PRs und CI-Stand geprüft
- [ ] README, TODO, CHANGELOG, AGENTS und maschinenlesbare Statusdateien gegen den Code geprüft
- [ ] Qualitätsgate für den exakten Übergabe-Head vollständig grün
- [ ] paketbezogene Evidence bei Release-relevanten Änderungen geprüft
- [ ] Diagnose-Contract-SHA und Evidence-Fingerprint zwischen Plattformen geprüft
- [ ] reale Hardwarefreigaben nur mit validiertem `HARDWARE_ACCEPTANCE.json`
- [ ] nach Merge resultierenden `main` erneut geprüft

## Erledigt

### [erledigt] 0.5.1-E1 – Maschinenlesbarer Hardware-Abnahmevertrag
Ergebnis:
- `hardware/HARDWARE_ACCEPTANCE.schema.json` als versionierter Vertrag eingeführt
- Hardware-Nachweise an den aktuell validierten Evidence-Fingerprint und Diagnosevertrag gebunden
- Linux/Windows, OS-Version, CPU/RAM, Mikrofon, Paket-/Modell-SHA und geschützten Modellpfad erfassbar
- Testdauer, Segmentzahl/-verlust, Echtzeitfaktor, Peak-RAM und beobachtete Diagnosecodes erfassbar
- Profile `long30` / `long60` erzwingen mindestens 1800 / 3600 Sekunden reale Messdauer
- `PASS` verlangt gestartete App, gebündelten Sidecar, geschützten Modellpfad, funktionierende Mikrofon-/Live-Diktat-/WAV-Bereinigung und 0 Segmentverluste
- `tests/validate_hardware_acceptance.py` prüft Schema und reale Nachweise; CI-Paketdaten allein erzeugen ausdrücklich keine Hardwarefreigabe
- Hauptfortschritt bleibt korrekt bei 8 von 9 / 89 %, da reale Hardwaremessungen noch fehlen

### [erledigt] 0.5.1-D – Windows-Bundle & Plattform-Evidence
Ergebnis:
- whisper.cpp `v1.9.2` aus Commit `306c88f4d1286aec1bf96e544632897886af5501` für Windows x86_64/MSVC gebaut
- echtes Tauri-NSIS-Bundle erzeugt
- gepackten Windows-Sidecar extrahiert, gestartet und per SHA-256 gegen den Build-Sidecar geprüft
- Linux- und Windows-Release-Evidence automatisiert verglichen
- Diagnosevertrag plattformübergreifend identisch gebunden
- Evidence-Fingerprint `018452a4b7683cba40dbce2a2c221aa6b31e55c846470baef35e4baa13081aaf` als gemeinsame Software-/Diagnoseidentität validiert
- Projektfortschritt auf 8 von 9 Hauptpunkten beziehungsweise 89 % angehoben

### [erledigt] 0.5.1-C – Diagnose, Logging & Evidence-Bindung
Ergebnis:
- kanonischer `diagnostics/DIAGNOSTICS_CONTRACT.json`
- stabile Fehlercodes, Ringpuffer, Deduplizierung, Privacy-Redaktion und Safe Actions
- Diagnose-/Release-Evidence-Vertrag über SHA-256, Schema und Ereignisformat gekoppelt

### [erledigt] 0.5.1-B1 – Deterministische DEB-Reproduzierbarkeit
Ergebnis:
- Zeit-/Archivmetadaten normalisiert
- festes `SOURCE_DATE_EPOCH`
- deterministisches `dpkg-deb`-Profil mit Bytegleichheitsprüfung

### [erledigt] 0.5.1-B – Linux-Bundle & Release-Nachweis
Ergebnis:
- deterministisches `dist/`
- reales Linux-DEB mit startbarem Sidecar
- Laufzeitabhängigkeiten und Bytegleichheit geprüft
- `RELEASE_EVIDENCE.json` und menschenlesbarer Nachweis

### [erledigt] 0.5.1-A – Produktversions-Konsistenz
Ergebnis:
- Produktversion 0.5.0 konsistent gebunden
- Backup-Metadaten synchronisiert
- IndexedDB-Schema bewusst getrennt gehalten

## Pflegevertrag

Diese Datei wird bei jeder relevanten funktionalen, technischen, sicherheitsrelevanten, Build-, CI-, Release- oder Architekturänderung geprüft und aktualisiert. Fortschritt und aktueller Arbeitsstand müssen mit `README.md` und `PROJEKTSTATUS.json` übereinstimmen.