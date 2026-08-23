# TODO – NAQYA

Stand: 2026-08-23  
Validierter Basisstand: **0.5.0 – Tauri-Sidecar-Integration & Repository-Konsolidierung**  
Aktueller Arbeitsstand: **0.5.1-E7 – geführter Linux-Hardware-Smoke bereit**  
Fortschritt 0.5.1: **89 % – 8 von 9 Hauptpunkten erledigt**  
Nächster Entwicklungsblock: **reale Linux-Smoke-Hardwareabnahme mit validierter `HARDWARE_ACCEPTANCE.json`**

## P0 – Freigabekritisch

### [offen] Reale Linux- und Windows-Desktop-Abnahme durchführen
Komponente: Hardware / Mikrofon / STT / Release

Abnahmekriterien:
- validierte Linux- und Windows-Pakete auf realen Referenzgeräten installieren und starten
- gebündelter `naqya-whisper` wird real von NAQYA verwendet
- echtes Modell aus dem geschützten NAQYA-Modellpfad funktioniert
- Mikrofonaufnahme und segmentiertes Live-Diktat funktionieren
- temporäre WAV-Dateien werden zuverlässig bereinigt
- Providerdiagnose zeigt den lokalen whisper.cpp-Pfad
- Evidence-Fingerprint der getesteten Software wird in `HARDWARE_ACCEPTANCE.json` gebunden
- E3-Runtime-Metriken und E4-Ressourcenmessung werden über E5/E6 importiert
- geführten E7-Assistenten `tools/run_linux_hardware_smoke.py` verwenden
- `tests/validate_hardware_acceptance.py HARDWARE_ACCEPTANCE.json` muss PASS liefern
- keine Hardware-Freigabe ohne real gemessenen und validierten Nachweis

### [erledigt] E7-Hardware-Smoke-Assistent bereitstellen
Ergebnis:
- interaktiver Linux-Assistent vorhanden
- sieben reale Bestätigungen einzeln, Standard `NEIN`
- nicht-interaktive PASS-Erzeugung blockiert
- vorhandener Collector und Validator werden wiederverwendet
- Regressionstest im Qualitätsworkflow
- Quality #445 für den Merge-Head erfolgreich
- Fortschritt bleibt 89 %, weil der Assistent die reale Abnahme nicht ersetzt

## P1 – Hohe Priorität

### [offen] Langzeit- und Lasttests für Live-STT durchführen
Abnahmekriterien:
- `long30`: mindestens 30 Minuten reale Sitzung ohne Segmentverlust
- `long60`: mindestens 60 Minuten reale Sitzung ohne Segmentverlust
- CPU-/RAM-Verhalten und Echtzeitfaktor dokumentiert
- kontrolliertes Verhalten bei langsamer Transkription
- Diagnose-Ringpuffer bleibt begrenzt und performant

## P2 – Qualitätsausbau

### [offen] `ScriptProcessor` durch `AudioWorklet` ersetzen
Abnahmekriterien:
- reale Hardware-/Performance-Baseline zuerst dokumentieren
- gleiche oder bessere 16-kHz-Mono-Normalisierung
- stabile Segmentbildung
- keine Regression bei Live-Diktat und Recovery
- Firefox- und Chrome-Kompatibilität geprüft

### [offen] Native Mobiladapter implementieren
Reihenfolge:
1. Android `whisper.cpp` über JNI/NDK
2. iPhone/iPad über Swift-native Bridge
3. derselbe `NAQYA-STT-PROVIDER`-Vertrag bleibt verbindlich
4. keine Cloud-Fallbacks

## P3 – Wartbarkeit

### [offen] Alte erledigte Entwicklungszweige bereinigen
- nur Zweige löschen, deren Inhalt nachweislich in `main` enthalten oder bewusst verworfen ist
- keine aktive oder ungeprüfte Arbeit entfernen

### [offen] Historischen Modulnamen `services/release-04.js` bewerten
- nur ändern, wenn ein realer Wartbarkeitsnutzen besteht
- keine reine Umbenennung ohne Nutzen

## Entwickler-Übergabecheckliste

### Aktuelle Übergabebereitschaft 0.5.1-E7

- [x] professioneller Entwickler-Einstieg und technische Übergabedokumentation
- [x] PWA-/Backup-Produktversion gegen `VERSION.json` abgesichert
- [x] deterministisches Desktop-Frontend-`dist/`
- [x] Linux-DEB und Windows-NSIS im CI nachgewiesen
- [x] echter Linux-GUI-Smoke im Release-Gate
- [x] Sidecar-Laufzeitabhängigkeiten und Bytegleichheit geprüft
- [x] Diagnosevertrag über SHA-256 mit Release Evidence verbunden
- [x] Linux-/Windows-Evidence automatisiert verglichen
- [x] maschinenlesbares Hardware-Abnahmeschema und Validator vorhanden
- [x] Hardware-Collector, Runtime-Metrikexport und Prozessressourcenmessung vorhanden
- [x] Runtime- und Ressourcenmesswerte werden SHA-gebunden importiert
- [x] geführter Linux-Hardware-Smoke-Harness vorhanden und fail-closed getestet
- [ ] echte Linux-Hardware-/Mikrofonabnahme abschließen
- [ ] echte Windows-Hardware-/Mikrofonabnahme abschließen
- [ ] `long30` und `long60` abschließen

## Erledigt

### [erledigt] 0.5.1-E6 – Runtime-Metriken direkt in Hardware-Evidence
- kanonischer `NAQYA-LIVE-STT-RUNTIME`-Export
- direkte Übernahme von Dauer, Segmentbilanz und RTF
- Runtime-Quelldatei per SHA-256 gebunden
- inkonsistente Werte werden fail-closed abgelehnt

### [erledigt] 0.5.1-E5 – Ressourcenmetriken direkt importieren
- `RESOURCE_METRICS.json` direkt importierbar
- Peak-RAM und CPU-Werte SHA-gebunden

### [erledigt] 0.5.1-E4 – Prozess-Ressourcenmessung
- Linux-/Windows-Messer für NAQYA-Prozessfamilie und Sidecar

### [erledigt] 0.5.1-E3 – Runtime-Messadapter
- Segmente, Segmentverlust und RTF werden real erfasst

### [erledigt] 0.5.1-E2 – Hardware-Evidence-Collector
- `HARDWARE_ACCEPTANCE.json` wird fail-closed erzeugt

### [erledigt] 0.5.1-E1 – Maschinenlesbarer Hardware-Abnahmevertrag
- versioniertes Schema
- reale Messwerte, Paket-/Modell-SHA und Evidence-Fingerprint gebunden
- PASS verlangt gestartete App, Sidecar, Modellpfad, Mikrofon, Live-Diktat, WAV-Bereinigung und 0 Segmentverluste

### [erledigt] Plattform- und Releasebasis
- Linux-DEB und Windows-NSIS im CI
- whisper.cpp-Sidecars für Linux/Windows
- echter Linux-GUI-Start im Release-Gate
- plattformneutraler STT-Providervertrag
- Diagnose-, Privacy- und Evidence-Verträge

## Pflegevertrag

README, TODO und `PROJEKTSTATUS.json` müssen denselben realen Arbeitsstand abbilden. Ein E7-Harness zählt nicht als Hardwarefreigabe; 89 % bleibt bestehen, bis ein echter validierter Hardware-Nachweis vorliegt.
