# PROVOWARE – NAQYA Memo Tool 2026

> **Aktueller Entwicklungsstand:** 0.5.1-E7 – geführter Linux-Hardware-Smoke bereit  
> **Produktversion:** 0.5.0  
> **Status:** Entwicklung – E7-Harness validiert und gemergt, reale Geräteabnahme ausstehend  
> **Fortschritt 0.5.1:** **89 %** – **8 von 9 Hauptpunkten erledigt**  
> **Nächster Schritt:** reale Linux-Smoke-Hardwareabnahme mit validierter `HARDWARE_ACCEPTANCE.json`

## Fortschritt auf einen Blick

Die Prozentangabe basiert auf 9 definierten Hauptpunkten des Entwicklungsblocks 0.5.1. Aktuell sind 8 abgeschlossen: `8 / 9 = 88,9 %`, gerundet **89 %**. Der E7-Assistent erleichtert die reale Abnahme, zählt aber bewusst noch nicht als abgeschlossene Hardwarefreigabe.

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
- **whisper.cpp:** `v1.9.2`, Commit `306c88f4d1286aec1bf96e544632897886af5501`
- **STT-Plattformvertrag:** gemeinsamer `NAQYA-STT-PROVIDER`; Linux/Windows aktiv, Android/iOS fail-closed vorbereitet
- **Modellsicherheit:** 4-MiB-Transferblöcke, SHA-256, geschützter App-Modellpfad, atomare Aktivierung
- **Desktop-Build:** deterministisches `dist/`; Tauri `frontendDist` zeigt auf `../dist`
- **Release-Nachweis:** Paket, Sidecar, Toolchain, Zielplattform, CI-Lauf, Diagnosevertrag und gemeinsamer Evidence-Fingerprint werden maschinenlesbar gebunden
- **Hardware-Abnahmevertrag:** `hardware/HARDWARE_ACCEPTANCE.schema.json` bindet reale Linux-/Windows-Messungen an denselben Evidence-Fingerprint; ohne reale Messdaten entsteht keine Hardwarefreigabe
- **Hardware-Evidence-Kette E2–E6:** Collector, Runtime-Metrikexport, Prozessressourcenmessung sowie direkte SHA-gebundene Importe für Runtime- und Ressourcenwerte sind vorhanden
- **E7-Assistent:** `tools/run_linux_hardware_smoke.py` führt die reale Linux-Smoke-Abnahme interaktiv und fail-closed; Standardantwort ist NEIN und CI kann kein Hardware-PASS vortäuschen

## Hardware-Abnahmevertrag 0.5.1-E1 bis E7

E1 definiert den maschinenlesbaren Hardwarevertrag. E2 erzeugt `HARDWARE_ACCEPTANCE.json`. E3 erfasst reale Segment- und RTF-Metriken. E4 misst CPU und Peak-RAM. E5/E6 importieren Ressourcen- und Runtime-Metriken SHA-gebunden. E7 stellt einen geführten Linux-Assistenten bereit, der diese vorhandenen Bausteine verwendet und keine eigene parallele Abnahmelogik einführt.

Ein Hardware-`PASS` verlangt weiterhin mindestens: installierte und gestartete App, tatsächlich verwendeten gebündelten Sidecar, Modell aus dem geschützten Pfad, funktionierende Mikrofonaufnahme und Live-Diktat, erfolgreiche Temp-WAV-Bereinigung sowie **0 verlorene Segmente**. Der E7-Assistent erzeugt ohne interaktives Terminal kein PASS.

### Geführter Linux-Smoke

Voraussetzungen: validiertes `.deb`, lokales Whisper-Modell, exportierte `RUNTIME_METRICS.json` und `RESOURCE_METRICS.json` sowie ein reales Mikrofon.

```bash
python3 tools/run_linux_hardware_smoke.py \
  --package /pfad/NAQYA_0.5.0_amd64.deb \
  --model /pfad/ggml-base.bin \
  --microphone "USB Audio Device" \
  --runtime-metrics RUNTIME_METRICS.json \
  --resource-metrics RESOURCE_METRICS.json \
  --profile smoke \
  --output HARDWARE_ACCEPTANCE.json
```

Der Assistent fragt sieben reale Beobachtungen einzeln ab. Nur wenn alle mit `ja` bestätigt sind und der vorhandene Hardware-Validator den Nachweis akzeptiert, endet der Lauf mit PASS. Andernfalls bleibt das Ergebnis FAIL.

## Diagnose-, Logging- und Evidence-Vertrag

Kanonische Quelle ist `diagnostics/DIAGNOSTICS_CONTRACT.json`. Hardware-PASS und Release-Evidence bleiben getrennt: CI kann Software und Pakete validieren, aber keine reale Mikrofon- oder Endgeräteabnahme ersetzen.

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
5. `docs/STT_PROVIDER_CONTRACT.md` – plattformneutraler STT-Adaptervertrag
6. `AGENTS.md` – verbindlicher Entwicklungs-, Merge- und Freigabevertrag
7. `TODO.md` – Prioritäten und Abnahmekriterien
8. `PROJEKTSTATUS.json` – maschinenlesbarer aktueller Stand und Release-Nachweis

## Was aktuell validiert ist

- PWA-Grundfunktionen und lokaler Datenpfad
- 3-Sekunden-Audio-Recovery
- 16-kHz-Mono-WAV-Normalisierung
- 4-Sekunden-Live-STT-Segmentierung
- plattformneutraler STT-Providervertrag mit fail-closed Mobiladaptern
- geschützter nativer Modellpfad und SHA-256-Modelltransfer
- deterministisches Desktop-Frontend-Staging
- Linux-DEB und Windows-NSIS im CI
- echter Linux-GUI-Smoke im Release-Gate
- Sidecars im Paketkontext vorhanden, startbar und integritätsgeprüft
- Diagnose-Laufzeitregression, Privacy-Redaktion und sichere Aktionen
- SHA-256-Bindung von Diagnosevertrag und Release Evidence
- plattformübergreifender Evidence-Fingerprint
- automatisierter Linux/Windows-Evidence-Paarvergleich
- maschinenlesbares Hardware-Abnahmeschema und Validator
- Hardware-Collector, Runtime-Metrikexport und Prozessressourcenmessung
- direkter SHA-gebundener Import von Runtime- und Ressourcenmetriken in Hardware-Evidence
- geführter, interaktiver und fail-closed Linux-Hardware-Smoke-Harness

## Noch offen bzw. nicht als Hardware-Release abgenommen

- reale Mikrofon-/Hardwareabnahme unter Linux und Windows
- 30-/60-Minuten-Langzeitmessungen für CPU, RAM, Latenz und Echtzeitfaktor
- `AudioWorklet` als Ersatz für `ScriptProcessor`
- native Android-/iPhone-/iPad-Adapter

## Nächster Entwicklungsblock

**0.5.1-E7 – REALE LINUX-SMOKE-HARDWAREABNAHME**

Priorität:

1. validiertes Linux-Paket auf realem Referenzgerät installieren und starten
2. echtes Mikrofon + geschützten Modellpfad + gebündelten Sidecar verwenden
3. Runtime- und Ressourcenmetriken exportieren
4. `tools/run_linux_hardware_smoke.py` ausführen und alle Beobachtungen real bestätigen
5. `HARDWARE_ACCEPTANCE.json` mit `tests/validate_hardware_acceptance.py` validieren
6. erst danach Windows-Smoke, `long30`, `long60` und schließlich `AudioWorklet`
