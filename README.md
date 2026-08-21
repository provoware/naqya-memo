# PROVOWARE – NAQYA Memo Tool 2026

> **Aktueller Entwicklungsstand:** 0.5.1-C – Diagnose, Logging & Evidence-Bindung  
> **Produktversion:** 0.5.0  
> **Status:** Entwicklung – Diagnosevertrag und Linux-Bundle CI-validiert  
> **Fortschritt 0.5.1:** **78 %** – **7 von 9 Hauptpunkten erledigt**  
> **Nächster Schritt:** 0.5.1-D – Windows-Bundle mit identischem Diagnosevertrag

## Fortschritt auf einen Blick

Der Entwicklungsblock 0.5.1 besteht aus 9 definierten Hauptpunkten. **7 / 9 = 77,8 %**, gerundet **78 %**. Derselbe Stand wird in `PROJEKTSTATUS.json` maschinenlesbar geführt und durch CI-Verträge gegen Dokumentationsdrift abgesichert.

### Erledigt – 7 von 9

- [x] Produktversion und Backup-Metadaten konsistent absichern
- [x] Desktop-Frontend deterministisch in `dist/` stagen
- [x] Linux-Tauri-DEB mit gebündeltem Sidecar erzeugen
- [x] Sidecar im Paketkontext starten und Laufzeitabhängigkeiten prüfen
- [x] maschinen- und menschenlesbaren Release-Nachweis erzeugen
- [x] professionelles Diagnose-/Debugging-/Logging-Modul mit stabilen Fehlercodes integrieren
- [x] Diagnoseereignisse und Release Evidence über denselben versionierten Diagnosevertrag verbinden

### Offen – 2 von 9

- [ ] Windows-x86_64-Sidecar und Windows-Tauri-Bundle reproduzierbar bauen und nachweisen
- [ ] reale Linux-/Windows-Hardwareabnahme sowie AudioWorklet- und Langzeithärtung abschließen

## Was NAQYA ist

NAQYA ist ein offline-first Memo-, Dokument-, Audio- und Diktatwerkzeug als PWA und Tauri-Desktop-App. Daten, Audio, Sprachmodelle und Diagnosen bleiben standardmäßig lokal; es gibt keinen automatischen Cloud-STT-Fallback und keine Telemetriepflicht.

Technischer Kern:

- IndexedDB-Datenhaltung und lokales Vollbackup
- 3-Sekunden-Audio-Recovery
- 16 kHz / Mono / PCM16-WAV-Normalisierung
- 4-Sekunden-Live-STT-Segmente mit geordneter Warteschlange
- Tauri-Sidecar `naqya-whisper`, kontrollierter lokaler `whisper-cli` nur als Fallback
- whisper.cpp `v1.9.2`, Commit `306c88f4d1286aec1bf96e544632897886af5501`
- geschützter Modellpfad, SHA-256 und atomare Modellaktivierung
- deterministisches Desktop-Staging und reproduzierbares Linux-DEB
- versionierter Diagnosevertrag mit begrenztem Ringpuffer, Privacy-Redaction, Safe Actions und JSON-/TXT-Export

## Diagnosevertrag 0.5.1-C

Kanonische Datei: `diagnostics/DIAGNOSTICS_CONTRACT.json`

- Format: `NAQYA-DIAGNOSTICS`
- Schema-Version: `1`
- Ereignisschema-Version: `1`
- Contract-SHA-256: `fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425`
- Ringpuffer: maximal 200 bereinigte Ereignisse
- Deduplizierungsfenster: 5 Sekunden
- sensible Audio-, Transkript-, Dokument-, Token- und vollständige Benutzerpfaddaten sind im Standardlog ausgeschlossen
- Retry ist nur über die registrierte Safe Action `retry-once` und maximal einmal zulässig

**Plattforminvariante:** Linux und Windows müssen exakt denselben Diagnosevertrag und dieselbe Contract-SHA verwenden. Vorhandene Fehlercodes dürfen plattformspezifisch weder umgedeutet noch wiederverwendet werden. Damit bedeutet beispielsweise `NAQYA-STT-4002` auf Linux und Windows garantiert dasselbe Fehlerereignis.

## Aktueller validierter Nachweis

Für den exakten 0.5.1-C-Head `0388cda77c6696017c5b00cb795f5758af2d5e22` waren beide relevanten Prüfketten erfolgreich:

- Qualitätsprüfung: Run **#268**, Run-ID `32482553363`
- Linux-Bundle-Nachweis: Run **#14**, Run-ID `32482553418`
- CI-Artefakt: `naqya-linux-bundle-nachweis-14`, Artefakt-ID `9446843382`
- Artefakt-SHA-256: `8e2efd73b581bd420f348b129e554363aaf4cdbbcb4ca65ffa7b9ba3290074f1`
- Diagnosevertrag-SHA-256 im Release Evidence: `fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425`

Der Linux-Sidecar wurde im Paketkontext gestartet und seine Laufzeitabhängigkeiten geprüft. Das bleibt eine belastbare CI-Paketabnahme, **noch keine reale Endgeräte-/Mikrofon-/Langzeitabnahme**.

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

## Entwickler-Einstieg

1. `CONTRIBUTING.md`
2. `docs/ENTWICKLERDOKUMENTATION.md`
3. `AGENTS.md`
4. `TODO.md`
5. `PROJEKTSTATUS.json`
6. `docs/DIAGNOSE_LOGGING.md`

## Was aktuell validiert ist

- PWA-Grundfunktionen und lokale Datenhaltung
- Audio-Recovery und PCM-Normalisierung
- segmentiertes Live-STT
- geschützter nativer Modellpfad
- Linux-Sidecar-Build und Linux-DEB
- deterministisches Desktop-Staging und DEB-Repacking
- Release Evidence mit Paket-, Sidecar- und Diagnosevertragsbindung
- fail-safe Diagnosemodul, Ringpuffer, Deduplizierung, Privacy-Regeln und Retry-once
- JSON-/TXT-Diagnoseexport
- statische und Laufzeit-Regressionsprüfungen

## Noch offen bzw. nicht als Hardware-Release abgenommen

- reproduzierbarer Windows-x86_64-Sidecar und Windows-Bundle
- reale Mikrofon-/Hardwareabnahme unter Linux und Windows
- 30-/60-Minuten-Langzeittests
- `AudioWorklet` als Ersatz für `ScriptProcessor`
- native Android-/iPhone-/iPad-Adapter

## Qualitätsprüfung

GitHub Actions prüft unter anderem JSON-Struktur, Duplicate Keys, Text-/Merge-Integrität, JavaScript-Syntax, Diagnose-Laufzeitregression, Diagnose-/Evidence-Vertrag, deterministisches Desktop-Staging, DEB-Reproduzierbarkeit, Sidecar-Build und SHA-256, Rust/Tauri-Kompilierung, statische Verträge und Shell-Syntax.

## Dokumentationsstatus

Kanonische Referenzen sind `README.md`, `PROJEKTSTATUS.json`, `VERSION.json`, `AGENTS.md`, `TODO.md`, `CHANGELOG.md`, `docs/ENTWICKLERDOKUMENTATION.md`, `docs/DIAGNOSE_LOGGING.md`, `docs/ARCHITEKTUR.md`, `docs/WHISPER_SIDECAR.md` und `release/RELEASE_EVIDENCE.schema.json`.

## Nächster Entwicklungsblock

**0.5.1-D – WINDOWS-BUNDLE MIT IDENTISCHEM DIAGNOSEVERTRAG**

Reihenfolge:

1. Windows-x86_64-Sidecar aus demselben gepinnten whisper.cpp-Upstream bauen
2. Tauri-konformen `.exe`-Sidecar in das Windows-Bundle aufnehmen
3. Paket und Sidecar per SHA-256 nachweisen
4. Sidecar aus dem erzeugten Paketkontext tatsächlich starten
5. Release Evidence für Windows erzeugen
6. **vor Freigabe bytegenau prüfen, dass `diagnostics/DIAGNOSTICS_CONTRACT.json` weiterhin SHA-256 `fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425` besitzt**
7. Windows-Diagnosen gegen dasselbe Ereignisschema und dieselben Fehlercodes regressionsprüfen
8. erst danach reale Linux-/Windows-Hardwareabnahme fortsetzen
