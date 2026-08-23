# PROVOWARE – NAQYA Memo Tool 2026

> **Aktueller Entwicklungsstand:** 0.5.1-E7 – Geführte reale Linux-Smoke-Hardwareabnahme vorbereitet  
> **Produktversion:** 0.5.0  
> **Status:** Entwicklung – E7-Hardware-Smoke fail-closed vorbereitet, reale Geräteabnahme ausstehend  
> **Fortschritt 0.5.1:** **89 %** – **8 von 9 Hauptpunkten erledigt**  
> **Nächster Schritt:** 0.5.1-E7 – reale Linux-Smoke-Hardwareabnahme durchführen

## Fortschritt auf einen Blick

Die Prozentangabe basiert auf 9 definierten Hauptpunkten des Entwicklungsblocks 0.5.1. Aktuell sind 8 abgeschlossen: `8 / 9 = 88,9 %`, gerundet **89 %**. `README.md` und `PROJEKTSTATUS.json` verwenden dieselbe Berechnungsbasis und werden automatisiert auf Gleichstand geprüft.

### Erledigt – 8 von 9

- [x] Produktversion und Backup-Metadaten konsistent abgesichert
- [x] Desktop-Frontend deterministisch in `dist/` gestagt
- [x] Linux-Tauri-DEB mit gebündeltem Sidecar erzeugt
- [x] Sidecar im Paketkontext gestartet und Laufzeitabhängigkeiten geprüft
- [x] maschinen- und menschenlesbaren Release-Nachweis erzeugt
- [x] Diagnose-/Debugging-/Logging-Modul mit stabilen Fehlercodes integriert
- [x] Diagnosevertrag und Release Evidence über SHA-256, Schema und Ereignisformat gekoppelt
- [x] Windows-x86_64-NSIS, gepackten Sidecar-Start und Linux/Windows-Evidence-Fingerprint vollständig nachgewiesen

### Offen – 1 von 9

- [ ] reale Linux-/Windows-Hardware- und Mikrofonabnahme sowie AudioWorklet-/Langzeithärtung abschließen

## Was NAQYA ist

NAQYA ist ein **offline-first Memo-, Dokument-, Audio- und Diktatwerkzeug**. Es kombiniert eine installierbare PWA mit einer Tauri-Desktop-App und speichert Inhalte lokal. Kernbereiche sind Notizen, Termine, Fristen, Aufgaben, Dokumente, Projekte, Kategorien, Tags, Chronologie, Audio-Memos, Live-Diktat und lokale Backups.

Technischer Kern:

- **Offline-first:** kein Account, keine Cloudpflicht, keine Telemetrie, kein automatischer Cloud-STT-Fallback
- **Lokale Datenhaltung:** IndexedDB für Einträge, Projekte, Einstellungen, Audiosegmente, Dateien und Modellmetadaten
- **Audio-Recovery:** 3-Sekunden-Segmente
- **STT-Normalisierung:** 16 kHz, Mono, PCM16/WAV
- **Live-STT:** 4-Sekunden-Segmente mit geordneter lokaler Transkriptionswarteschlange
- **Desktop-STT:** bevorzugter Tauri-Sidecar `naqya-whisper`; kontrollierter lokaler `whisper-cli` nur als Fallback
- **STT-Providervertrag:** plattformneutral; Linux/Windows aktiv, Android/iOS fail-closed vorbereitet
- **whisper.cpp:** `v1.9.2`, Commit `306c88f4d1286aec1bf96e544632897886af5501`
- **Modellsicherheit:** 4-MiB-Transferblöcke, SHA-256, geschützter App-Modellpfad, atomare Aktivierung
- **Desktop-Build:** deterministisches `dist/`; Tauri `frontendDist` zeigt auf `../dist`
- **Release-Nachweis:** Paket, Sidecar, Toolchain, Zielplattform, CI-Lauf, Diagnosevertrag und gemeinsamer Evidence-Fingerprint werden maschinenlesbar gebunden
- **Hardware-Abnahmevertrag:** `hardware/HARDWARE_ACCEPTANCE.schema.json` bindet reale Linux-/Windows-Messungen an denselben Evidence-Fingerprint; ohne reale Messdaten entsteht keine Hardwarefreigabe
- **Hardware-Evidence-Kette E2–E6:** Collector, Runtime-Metrikexport, Prozessressourcenmessung sowie direkte SHA-gebundene Importe für Runtime- und Ressourcenwerte sind vorhanden
- **E7-Hardware-Smoke-Harness:** geführter Linux-Ablauf bündelt die vorhandenen Evidence-Bausteine; ohne interaktive reale Bestätigungen bleibt der Nachweis fail-closed

## Diagnose-, Logging- und Evidence-Vertrag

Kanonische Quelle ist `diagnostics/DIAGNOSTICS_CONTRACT.json`.

- Schema-Version: **1**
- Ereignisschema: **1**
- Format: **`NAQYA-DIAGNOSTICS`**
- Contract-SHA-256: **`fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425`**
- aktueller plattformübergreifender Evidence-Fingerprint: **`018452a4b7683cba40dbce2a2c221aa6b31e55c846470baef35e4baa13081aaf`**

Der Evidence-Fingerprint wird ausschließlich aus gemeinsamen Invarianten gebildet: NAQYA-Version, Quellcommit, whisper.cpp-Commit, Diagnose-Contract-SHA, Diagnose-Schema, Ereignisschema und kanonischem Fehlercode-Katalog-SHA. Paket-, Plattform- und Sidecar-Binärhashes gehören bewusst **nicht** hinein.

Damit ist folgende Kette maschinenlesbar nachvollziehbar:

```text
Git-Commit
  → Linux-DEB / Windows-NSIS
  → gepackter Sidecar
  → Diagnosevertrag
  → Evidence-Fingerprint
  → E3-Runtime-Messung + E4-Ressourcenmessung
  → E5/E6-Import in HARDWARE_ACCEPTANCE.json
  → E7 geführter Linux-Smoke
  → reale Hardware-Abnahme
  → Runtime-Ereignis / Fehlercode
  → sichere Benutzeraktion
```

## Hardware-Abnahmevertrag 0.5.1-E1 bis E7

E1 definiert den maschinenlesbaren Hardwarevertrag. E2 erzeugt `HARDWARE_ACCEPTANCE.json`. E3 erfasst reale Segment- und RTF-Metriken der Live-STT-Sitzung. E4 misst CPU und Peak-RAM der NAQYA-Prozessfamilie. E5 importiert `RESOURCE_METRICS.json` direkt und SHA-gebunden. E6 exportiert `NAQYA-LIVE-STT-RUNTIME` und importiert Dauer, Segmentbilanz und RTF ebenfalls direkt und SHA-gebunden. E7 stellt dafür einen geführten Linux-Smoke-Harness bereit, der reale Bestätigungen verlangt und ohne interaktives Terminal keinen Hardware-PASS erzeugt.

Ein Hardware-`PASS` verlangt weiterhin mindestens: installierte und gestartete App, tatsächlich verwendeten gebündelten Sidecar, Modell aus dem geschützten Pfad, funktionierende Mikrofonaufnahme und Live-Diktat, erfolgreiche Temp-WAV-Bereinigung sowie **0 verlorene Segmente**. Die Profile `long30` und `long60` erzwingen mindestens 1800 beziehungsweise 3600 Sekunden reale Testdauer.

Die Evidence-Kette ist automatisiert prüfbar; **reale Linux-/Windows-Hardwaremessungen stehen weiterhin aus** und werden nicht aus CI-Paketdaten abgeleitet.

## Aktueller Plattform-Nachweis

Der D2-Nachweis wurde für Quellcommit `afe968e84678b056e9a4074b6bd76c4529095c73` erzeugt.

- Qualitätsprüfung: Run **#328**, Run-ID `32492639621` – erfolgreich
- Plattform-Bundle-Nachweis: Run **#8**, Run-ID `32492640017` – erfolgreich
- Linux-Bundle: vollständig erfolgreich
- Windows-NSIS-Bundle: vollständig erfolgreich
- gepackter Windows-Sidecar: gestartet und geprüft
- Linux/Windows-Evidence-Vergleich: erfolgreich
- Plattformvergleich-Artefakt: ID `9451013994`, SHA-256 `6b1ea4e8cf123957af9f8ef622e2e98eb42d1bc831932c9fc72c99cd0b9e0c49`
- Linux-Artefakt: ID `9450688197`, SHA-256 `cac1c82a581c8a698d7ce207fa543d33d234a15388699c51cb5463da2928e70e`
- Windows-Artefakt: ID `9451007827`, SHA-256 `5c6f4de33a2abee4be5d0e0d4cce6648d7cde05464e5f230b0bd128818be1e87`
- gemeinsamer Evidence-Fingerprint: `018452a4b7683cba40dbce2a2c221aa6b31e55c846470baef35e4baa13081aaf`

**Wichtig:** Dies ist eine belastbare CI-Paketabnahme für Linux und Windows, aber noch keine reale Endgeräte-, Mikrofon- oder Langzeitabnahme.

## Schnellstart PWA

### Linux

```bash
chmod +x START_NAQYA.sh
./START_NAQYA.sh
```

### Windows

Doppelklick auf `START_NAQYA.bat`.

### Manuell

```bash
python3 -m http.server 8765 --bind 127.0.0.1
```

Danach `http://127.0.0.1:8765` öffnen.

## Entwickler-Einstieg

1. `CONTRIBUTING.md` – kurzer GitHub-Einstieg und Mindestprüfungen
2. `docs/ENTWICKLERDOKUMENTATION.md` – Architekturkarte, Vertrauensgrenzen und lokale Prüfungen
3. `docs/DIAGNOSE_LOGGING.md` – Diagnose-, Privacy- und Evidence-Vertrag
4. `docs/HARDWARE_ACCEPTANCE.md` – realer Hardware-Abnahmevertrag und Prüfprofile
5. `AGENTS.md` – verbindlicher Entwicklungs-, Merge- und Freigabevertrag
6. `TODO.md` – Prioritäten und Abnahmekriterien
7. `PROJEKTSTATUS.json` – maschinenlesbarer aktueller Stand und Release-Nachweis

## Was aktuell validiert ist

- PWA-Grundfunktionen und lokaler Datenpfad
- 3-Sekunden-Audio-Recovery
- 16-kHz-Mono-WAV-Normalisierung
- 4-Sekunden-Live-STT-Segmentierung
- geschützter nativer Modellpfad und SHA-256-Modelltransfer
- plattformneutraler STT-Providervertrag mit rückwärtskompatiblem Desktop-Pfad
- deterministisches Desktop-Frontend-Staging
- Linux-DEB und Windows-NSIS im CI
- Sidecars im Paketkontext vorhanden, startbar und integritätsgeprüft
- Diagnose-Laufzeitregression, Privacy-Redaktion und sichere Aktionen
- SHA-256-Bindung von Diagnosevertrag und Release Evidence
- plattformübergreifender Evidence-Fingerprint
- automatisierter Linux/Windows-Evidence-Paarvergleich
- maschinenlesbares Hardware-Abnahmeschema und Validator
- Hardware-Collector, Runtime-Metrikexport und Prozessressourcenmessung
- direkter SHA-gebundener Import von Runtime- und Ressourcenmetriken in Hardware-Evidence
- geführter Linux-Hardware-Smoke-Harness mit fail-closed Verhalten

## Noch offen bzw. nicht als Hardware-Release abgenommen

- reale Mikrofon-/Hardwareabnahme unter Linux und Windows
- 30-/60-Minuten-Langzeitmessungen für CPU, RAM, Latenz und Echtzeitfaktor
- `AudioWorklet` als Ersatz für `ScriptProcessor`
- native Android-/iPhone-/iPad-Adapter

## Nächster Entwicklungsblock

**0.5.1-E7 – REALE LINUX-SMOKE-HARDWAREABNAHME**

Priorität:

1. validiertes Linux-Paket auf realem Referenzgerät installieren und starten
2. `python3 tools/run_linux_hardware_smoke.py` interaktiv ausführen
3. echtes Mikrofon + geschützten Modellpfad + gebündelten Sidecar verwenden
4. Runtime- und Ressourcenmetriken exportieren und über E5/E6 in `HARDWARE_ACCEPTANCE.json` importieren
5. Nachweis mit `tests/validate_hardware_acceptance.py` prüfen
6. erst danach Windows-Smoke, `long30`, `long60` und schließlich `AudioWorklet`
