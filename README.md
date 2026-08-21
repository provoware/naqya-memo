# PROVOWARE – NAQYA Memo Tool 2026

> **Aktueller Entwicklungsstand:** 0.5.1-C – Diagnose, Logging & Evidence-Bindung  
> **Produktversion:** 0.5.0  
> **Status:** Entwicklung – Linux-Bundle + Diagnose-Evidence CI-validiert  
> **Fortschritt 0.5.1:** **78 %** – **7 von 9 Hauptpunkten erledigt**  
> **Nächster Schritt:** 0.5.1-D – Windows-x86_64-Bundle & plattformübergreifender Evidence-Nachweis

## Fortschritt auf einen Blick

Die Prozentangabe wird aus **9 definierten Hauptpunkten des Entwicklungsblocks 0.5.1** berechnet. Aktuell sind 7 abgeschlossen: `7 / 9 = 77,8 %`, gerundet **78 %**. `README.md` und `PROJEKTSTATUS.json` verwenden dieselbe Berechnungsbasis und werden automatisiert auf Gleichstand geprüft.

### Erledigt – 7 von 9

- [x] Produktversion und Backup-Metadaten auf 0.5.0 konsistent und regressionssicher synchronisiert
- [x] Desktop-Frontend deterministisch in `dist/` mit Allowlist und SHA-256-Manifest gestagt
- [x] echtes Linux-Tauri-DEB im CI erzeugt
- [x] gebündelten `naqya-whisper` im Paket gestartet, Laufzeitabhängigkeiten und Bytegleichheit geprüft
- [x] maschinenlesbaren `RELEASE_EVIDENCE.json` und menschenlesbaren Release-Nachweis erzeugt
- [x] professionelles Offline-Diagnose-/Debugging-/Logging-Modul mit stabilen Ereignis- und Fehlercodes integriert
- [x] Diagnosevertrag und Release Evidence über Schema, Format und SHA-256 zu einer durchgehenden Evidence-Kette verbunden

### Offen – 2 von 9

- [ ] Windows-x86_64-Sidecar und Windows-Tauri-Bundle reproduzierbar bauen und mit **demselben Diagnosevertrag** nachweisen
- [ ] reale Linux-/Windows-Hardware- und Mikrofonabnahme sowie AudioWorklet-/Langzeithärtung abschließen

## Was NAQYA ist

NAQYA ist ein **offline-first Memo-, Dokument-, Audio- und Diktatwerkzeug**. Es kombiniert eine installierbare PWA mit einer Tauri-Desktop-App und speichert Inhalte lokal. Kernbereiche sind Notizen, Termine, Fristen, Aufgaben, Dokumente, Projekte, Kategorien, Tags, Chronologie, Audio-Memos, Live-Diktat und vollständige lokale Backups.

Technischer Kern:

- **Offline-first:** kein Account, keine Cloudpflicht, keine Telemetrie, kein automatischer Cloud-STT-Fallback
- **Lokale Datenhaltung:** IndexedDB für Einträge, Projekte, Einstellungen, Audiosegmente, Dateien und Modellmetadaten
- **Audio-Recovery:** 3-Sekunden-Segmente für Wiederherstellung nach Unterbrechungen
- **STT-Normalisierung:** 16 kHz, Mono, PCM16/WAV
- **Live-STT:** 4-Sekunden-Segmente mit geordneter lokaler Transkriptionswarteschlange
- **Desktop-STT:** bevorzugter Tauri-Sidecar `naqya-whisper`; kontrollierter lokaler `whisper-cli` nur als Fallback
- **whisper.cpp:** `v1.9.2`, Commit `306c88f4d1286aec1bf96e544632897886af5501`
- **Modellsicherheit:** 4-MiB-Transferblöcke, SHA-256, geschützter App-Modellpfad, atomare Aktivierung
- **Desktop-Build:** deterministisches `dist/`; Tauri `frontendDist` zeigt auf `../dist`
- **Release-Nachweis:** Paket, Sidecar, Toolchain, Zielplattform, CI-Lauf und Diagnosevertrag werden maschinenlesbar gebunden
- **Diagnose:** begrenzter Ringpuffer, Deduplizierung, Privacy-Redaktion, stabile Codes, sichere Aktionen, JSON-/TXT-Export

## Diagnose-, Logging- und Evidence-Vertrag

Kanonische Quelle ist `diagnostics/DIAGNOSTICS_CONTRACT.json`.

Der aktuell validierte Vertrag hat:

- Schema-Version: **1**
- Ereignisschema: **1**
- Format: **`NAQYA-DIAGNOSTICS`**
- SHA-256: **`fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425`**

Ereignisse enthalten unter anderem `event_id`, `correlation_id`, optional `parent_event_id`, Fehlercode sowie **Was / Wann / Wo / Wie / Ergebnis / sichere Optionen**.

Der Standarddiagnosepfad speichert keine Audio-/Base64-Inhalte, Transkripte, Dokument-/Notiztexte, Tokens, Secrets oder unnötigen vollständigen Benutzerpfade. Der Ringpuffer ist auf 200 bereinigte Ereignisse begrenzt; identische Wiederholungen werden innerhalb des Vertragsfensters gezählt statt endlos angehängt. `retry-once` ist nur als explizite, einmalige Safe Action erlaubt.

`RELEASE_EVIDENCE.json` führt exakt denselben Contract-SHA. Dadurch ist folgende Kette maschinenlesbar:

```text
Git-Commit
  → Desktop-Paket
  → Sidecar
  → Diagnosevertrag
  → Runtime-Ereignis / Fehlercode
  → sichere Benutzeraktion
```

**Plattforminvariante für 0.5.1-D:** Linux und Windows müssen denselben Diagnosevertrag verwenden. Ein Code wie `NAQYA-STT-4002` darf auf Windows keine andere Bedeutung erhalten als auf Linux. Eine Änderung am Vertrag ist ein eigener versionierter Vertragswechsel und darf nicht still im Windows-Build erfolgen.

## Aktueller Linux-Release-Nachweis

Der aktuelle C-Nachweis wurde für Quellcommit `0388cda77c6696017c5b00cb795f5758af2d5e22` erzeugt.

- Qualitätsprüfung: Run **#268**, Run-ID `32482553363` – erfolgreich
- Linux-Bundle-Nachweis: Run **#14**, Run-ID `32482553418` – erfolgreich
- CI-Artefakt: `naqya-linux-bundle-nachweis-14`, Artefakt-ID `9446843382`
- Artefakt-SHA-256: `8e2efd73b581bd420f348b129e554363aaf4cdbbcb4ca65ffa7b9ba3290074f1`
- Linux-Paket: `NAQYA-0.5.0-linux-x86_64.deb`, **4.989.730 Bytes**
- Paket-SHA-256: `491f8d8c16683a9dd93695acfe9ad8b4a03fa3e07cb29a22184f5187491874c8`
- gebündelter Sidecar: **2.828.584 Bytes**
- Sidecar-SHA-256: `6c4805c72c855ea5b627b10450bb3feec56ea31b8038aed052ce9260bc11529b`
- Frontend-Buildmanifest-SHA-256: `b9c08e6aa6dc04ec18d0934862b58272a052f6a18740e831e1217519380d8a51`
- Diagnosevertrag-SHA-256: `fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425`
- Toolchain: Rust/Cargo 1.97.1, CMake 3.31.6, Tauri CLI 2.11.4, GCC/CC 13.3.0

Der Sidecar wurde aus dem extrahierten Paketkontext gestartet, seine Laufzeitabhängigkeiten wurden geprüft und sein SHA-256 stimmt bytegenau mit dem validierten Build-Sidecar überein.

**Wichtig:** Das ist eine belastbare CI-Paketabnahme, aber **noch keine reale Endgeräte-/Mikrofon-/Langzeitabnahme**.

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
4. `AGENTS.md` – verbindlicher Entwicklungs-, Merge- und Freigabevertrag
5. `TODO.md` – Prioritäten und Abnahmekriterien
6. `PROJEKTSTATUS.json` – maschinenlesbarer aktueller Stand und Release-Nachweis

## Was aktuell validiert ist

- PWA-Grundfunktionen und lokaler Datenpfad
- 3-Sekunden-Audio-Recovery
- 16-kHz-Mono-WAV-Normalisierung
- 4-Sekunden-Live-STT-Segmentierung
- geschützter nativer Modellpfad
- blockweiser Modelltransfer mit SHA-256 und atomarer Aktivierung
- reproduzierbarer Linux-x86_64-Sidecar
- deterministisches Desktop-Frontend-Staging und deterministisches DEB-Repacking
- vollständiger Linux-DEB-Build im CI
- Sidecar im Paket vorhanden und startbar
- Sidecar-Laufzeitabhängigkeiten und Bytegleichheit
- maschinen- und menschenlesbarer Release-Nachweis
- Diagnose-Laufzeitregression: Ringpuffer, Deduplizierung, Privacy, Safe Actions und `retry-once`
- SHA-256-Bindung von Diagnosevertrag und Release Evidence
- Rust/Tauri-Kompilierung, JavaScript-Syntax, Text-/Merge- und statische Verträge

## Noch offen bzw. nicht als Hardware-Release abgenommen

- Windows-x86_64-Sidecar und Windows-Bundle
- reale Mikrofon-/Hardwareabnahme unter Linux und Windows
- 30-/60-Minuten-Langzeitmessungen für CPU, RAM, Latenz und Echtzeitfaktor
- `AudioWorklet` als Ersatz für `ScriptProcessor`
- native Android-/iPhone-/iPad-Adapter

## Nächster Entwicklungsblock

**0.5.1-D – WINDOWS-X86_64-BUNDLE & PLATTFORMÜBERGREIFENDER EVIDENCE-NACHWEIS**

Reihenfolge:

1. Diagnosevertrag-SHA `fa160ea4…5425` als plattformübergreifende Invariante im Windows-Gate festschreiben
2. whisper.cpp aus demselben Upstream-Commit für `x86_64-pc-windows-msvc` reproduzierbar bauen
3. Tauri-Windows-Bundle erzeugen und `naqya-whisper.exe` aus dem Paketkontext starten
4. Paket-/Sidecar-SHA-256 und Toolchain in Windows-Release-Evidence aufnehmen
5. Linux- und Windows-Evidence gegen identische Diagnose-Schema-/Codebedeutung prüfen
6. danach reale Linux-/Windows-Hardwareabnahme und AudioWorklet-/Langzeithärtung
