# PROVOWARE – NAQYA Memo Tool 2026

> **Aktueller Entwicklungsstand:** 0.5.1-B – Linux-Bundle & Release-Nachweis  
> **Produktversion:** 0.5.0  
> **Status:** Entwicklung – Linux-Bundle CI-validiert  
> **Fortschritt 0.5.1:** **56 %** – **5 von 9 Hauptpunkten erledigt**  
> **Nächster Schritt:** 0.5.1-C – Diagnose, Debugging, Logging & Evidence-Bindung

## Fortschritt auf einen Blick

Die Prozentangabe ist kein geschätzter Marketingwert, sondern wird aus **9 klar definierten Hauptpunkten des Entwicklungsblocks 0.5.1** berechnet. Aktuell sind 5 abgeschlossen: `5 / 9 = 55,6 %`, gerundet **56 %**. Dieselben Werte stehen maschinenlesbar in `PROJEKTSTATUS.json` und werden durch Tests gegen Dokumentationsdrift abgesichert.

### Erledigt – 5 von 9

- [x] Produktversion und Backup-Metadaten auf 0.5.0 konsistent und regressionssicher synchronisiert
- [x] Desktop-Frontend deterministisch in ein eigenes `dist/` mit Allowlist und SHA-256-Manifest gestagt
- [x] echtes Linux-Tauri-DEB im CI erzeugt
- [x] gebündelten `naqya-whisper` im extrahierten Paket gestartet, Laufzeitabhängigkeiten geprüft und Bytegleichheit zum Build-Sidecar bestätigt
- [x] maschinenlesbaren `RELEASE_EVIDENCE.json` sowie menschenlesbaren Release-Nachweis erzeugt

### Offen – 4 von 9

- [ ] professionelles Diagnose-/Debugging-/Logging-Modul mit stabilen Ereignis- und Fehlercodes
- [ ] Diagnoseereignisse und sichere Benutzeraktionen mit `RELEASE_EVIDENCE.json` zu einer durchgehenden Evidence-Kette verbinden
- [ ] Windows-x86_64-Sidecar und Windows-Tauri-Bundle reproduzierbar bauen und nachweisen
- [ ] reale Linux-/Windows-Hardware- und Mikrofonabnahme sowie AudioWorklet-/Langzeithärtung abschließen

## Was NAQYA ist

NAQYA ist ein **offline-first persönliches Memo-, Dokument-, Audio- und Diktatwerkzeug**. Es kombiniert eine installierbare PWA mit einer Tauri-Desktop-App und speichert Inhalte lokal. Kernbereiche sind Notizen, Termine, Fristen, Aufgaben, Dokumente, Projekte, Kategorien, Tags, Chronologie, Audio-Memos, Live-Diktat und vollständige lokale Backups.

Technischer Kern:

- **Offline-first:** kein Account, keine Cloudpflicht, keine Telemetrie und kein automatischer Cloud-STT-Fallback
- **Lokale Datenhaltung:** IndexedDB für Einträge, Projekte, Einstellungen, Audiosegmente, Dateien und Modellmetadaten
- **Audio-Recovery:** Originalaufnahme wird in 3-Sekunden-Segmenten lokal gesichert und kann nach Unterbrechungen rekonstruiert werden
- **Lokale STT-Normalisierung:** 16 kHz, Mono, PCM16/WAV
- **Live-STT:** 4-Sekunden-Segmente mit geordneter lokaler Transkriptionswarteschlange
- **Native Desktop-STT:** bevorzugter Tauri-Sidecar `naqya-whisper`, kontrollierter lokaler `whisper-cli` nur als Fallback
- **whisper.cpp:** fest gepinnt auf `v1.9.2`, Commit `306c88f4d1286aec1bf96e544632897886af5501`
- **Modellsicherheit:** 4-MiB-Transferblöcke, SHA-256, geschützter App-Modellpfad und atomare Aktivierung
- **Backup:** lokales Vollbackup einschließlich Binärdateien und Prüfsummen
- **Desktop-Build:** deterministisches Runtime-Staging statt Repository-Stamm als `frontendDist`
- **Release-Nachweis:** Paket, Sidecar, SHA-256, Toolchain, Zielplattform und CI-Lauf werden maschinenlesbar dokumentiert

## Aktueller Linux-Release-Nachweis

Der erste vollständig erfolgreiche 0.5.1-B-Paketnachweis wurde für Quellcommit `602d0dd974abc1fe17490492c7a453bce88089fe` erzeugt.

- Qualitätsprüfung: Run **#216**, Run-ID `32477864261` – erfolgreich
- Linux-Bundle-Nachweis: Run **#1**, Run-ID `32477864231` – erfolgreich
- CI-Artefakt: `naqya-linux-bundle-nachweis-1`, Artefakt-ID `9445169821`
- Artefakt-SHA-256: `6831027b0ed6f5dd1ee1137d2cb814d5e6868f4a2ef041169318b4a54be2661d`
- Linux-Paket: `NAQYA-0.5.0-linux-x86_64.deb`, **5.148.416 Bytes**
- Paket-SHA-256: `1721b92de3a23da0ece8e9833d6949bf9b9987d7cc3de69e76d1cd50fc83f2e4`
- gebündelter Sidecar: **2.828.584 Bytes**
- Sidecar-SHA-256: `6c4805c72c855ea5b627b10450bb3feec56ea31b8038aed052ce9260bc11529b`
- Frontend-Buildmanifest-SHA-256: `5290ff2a7e20c5b8c28e4e32ed727c08054ea38c0f4aabea924694f3ade97351`
- Toolchain des Nachweises: Rust/Cargo 1.97.1, CMake 3.31.6, Tauri CLI 2.11.4, GCC/CC 13.3.0

Der Sidecar wurde **aus dem extrahierten Paketkontext** gestartet. Die Laufzeitabhängigkeiten wurden mit `ldd` geprüft; es gab keine `not found`-Abhängigkeit. Zusätzlich wurde bestätigt, dass der im Paket enthaltene Sidecar bytegenau denselben SHA-256 wie der vorher validierte Build-Sidecar besitzt.

**Wichtig:** Das ist eine belastbare CI-Paketabnahme, aber noch keine reale Endgeräte-/Mikrofon-/Langzeitabnahme. Diese bleibt als separater Schritt offen.

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

Für eine sofortige technische Übernahme in dieser Reihenfolge lesen:

1. `CONTRIBUTING.md` – kurzer GitHub-Einstieg und Mindestprüfungen
2. `docs/ENTWICKLERDOKUMENTATION.md` – Architekturkarte, Vertrauensgrenzen und lokale Prüfungen
3. `AGENTS.md` – verbindlicher Entwicklungs-, Merge- und Freigabevertrag
4. `TODO.md` – Prioritäten, Abnahmekriterien und Entwickler-Übergabecheckliste
5. `PROJEKTSTATUS.json` – maschinenlesbarer aktueller Stand, Fortschritt und Release-Nachweis

## Neu in 0.5.1-A/B

- PWA-/Backup-Produktversion hart an `VERSION.json` gebunden
- historischen 0.4.0-Runtimeoverride gegen erneute Versionsdrift gehärtet
- deterministisches Desktop-`dist/` mit expliziter Runtime-Allowlist
- `BUILD_MANIFEST.json` mit Größe und SHA-256 jeder gestagten Runtime-Datei
- Tauri `frontendDist` vom Repository-Stamm auf `../dist` umgestellt
- whisper.cpp-Linux-Build mit `BUILD_SHARED_LIBS=OFF` paketierbar gehärtet
- separater Linux-Bundle-Workflow mit pfadbasierten Triggern
- Tauri CLI im Bundle-Nachweis auf 2.11.4 gepinnt
- echtes `.deb` im CI gebaut und extrahiert
- enthaltenen Sidecar gestartet, Abhängigkeiten geprüft und bytegenau gegen den Build-Sidecar verglichen
- `RELEASE_EVIDENCE.schema.json`, Generator und Validator eingeführt
- menschen- und maschinenlesbarer Release-Nachweis als CI-Artefakt

## Desktop-Spracherkennung

Die native Runtime-Priorität lautet:

1. Tauri-Sidecar `naqya-whisper`
2. explizit verfügbarer lokaler `whisper-cli`-Fallback (`NAQYA_WHISPER_CLI` beziehungsweise kontrollierte `whisper-cli`-PATH-Erkennung)
3. keine native Transkription

Der Fallback darf den Sidecar nicht still überstimmen. Ein Sidecar, der gestartet wurde und einen Laufzeitfehler meldet, wird nicht still durch einen PATH-Fallback ersetzt.

Ein importiertes Modell wird nicht aus einem beliebigen Dateipfad direkt an whisper.cpp übergeben. NAQYA überträgt es in den eigenen App-Datenbereich, prüft SHA-256 und aktiviert es erst danach atomar.

```text
Mikrofon
  ↓
Originalaufnahme + 3-s-Recovery
  ↓
Web Audio PCM
  ↓
16 kHz / Mono / PCM16-WAV
  ↓
4-s-Live-Segment
  ↓
Tauri-Sidecar, sonst expliziter lokaler CLI-Fallback
  ↓
Transkriptsegment
  ↓
persistenter Diktattext
```

## Datenschutz und Offline-Prinzip

Der Kern benötigt keinen Account, keine Cloud und keine Telemetrie. Es gibt keinen automatischen Online-STT-Fallback. Kritische Runtime- oder Modellartefakte werden nicht ungeprüft zur Laufzeit heruntergeladen.

## Was aktuell validiert ist

- PWA-Grundfunktionen und lokaler Datenpfad
- 3-Sekunden-Audio-Recovery
- 16-kHz-Mono-WAV-Normalisierung
- 4-Sekunden-Live-STT-Segmentierung
- geschützter nativer Modellpfad
- blockweiser Modelltransfer mit SHA-256 und atomarer Aktivierung
- native Runtime-Härtung und privater STT-Tempbereich
- fest gepinnter whisper.cpp-Upstream
- reproduzierbarer Linux-x86_64-Sidecar-Build
- deterministisches Desktop-Frontend-Staging
- vollständiger Linux-DEB-Build im CI
- Sidecar im Paket vorhanden und startbar
- Sidecar-Laufzeitabhängigkeiten ohne fehlende Bibliotheken im CI-Prüfkontext
- Bytegleichheit von Build- und Paket-Sidecar
- maschinen- und menschenlesbarer Release-Nachweis
- Tauri-/Rust-Kompilierungsprüfung
- statische Architektur-, Sicherheits-, Text- und Dokumentationsverträge
- Gleichheit von PWA-/Backup-Produktversion und `VERSION.json`

## Noch offen bzw. nicht als Hardware-Release abgenommen

- professionelles Diagnose-/Debugging-/Logging-Modul mit stabilen Ereignis- und Fehlercodes
- gemeinsamer Diagnose-/Release-Evidence-Vertrag
- reproduzierbarer Windows-x86_64-Sidecar und Windows-Bundle
- reale Mikrofon-/Hardwareabnahme unter Linux und Windows
- 30-/60-Minuten-Langzeitmessungen für CPU, RAM, Latenz und Echtzeitfaktor
- `AudioWorklet` als Ersatz für den derzeitigen `ScriptProcessor`
- native Android-/iPhone-/iPad-Adapter

## Qualitätsprüfung

GitHub Actions prüft derzeit unter anderem:

- JSON-Struktur und eindeutige JSON-Schlüssel
- Textintegrität und Merge-Konfliktmarker
- Produktversion gegen `VERSION.json`
- JavaScript-Syntax
- deterministisches Desktop-Staging und dessen SHA-256-Manifest
- reproduzierbaren statischen Linux-Sidecar-Build
- SHA-256 des Sidecars
- Rust-Formatierung und Rust/Tauri-Kompilierung
- statische Architektur- und Sicherheitsverträge
- echtes Linux-DEB
- Paketinhalt und Sidecar-Start
- Laufzeitabhängigkeiten
- Release-Evidence-Schema und erzeugten Nachweis
- Shell-Syntax

## Dokumentationsstatus

Aktuelle Referenzen:

- `README.md` – kanonischer sichtbarer Gesamtstand mit Fortschritt
- `PROJEKTSTATUS.json` – maschinenlesbarer Fortschritt und validierter Paketnachweis
- `VERSION.json` – Produkt-/Runtime-Vertrag
- `CONTRIBUTING.md` – kurzer Einstieg für neue Mitentwickler
- `docs/ENTWICKLERDOKUMENTATION.md` – technische Übergabe und lokale Prüfungen
- `AGENTS.md` – verbindlicher Entwicklungs-, Merge- und Freigabevertrag
- `TODO.md` – priorisierte Restarbeiten und Abnahmekriterien
- `CHANGELOG.md` – tatsächlich umgesetzte Änderungen
- `docs/ARCHITEKTUR.md` – technische Architektur
- `docs/WHISPER_SIDECAR.md` – Sidecar-/Supply-Chain-Vertrag
- `release/RELEASE_EVIDENCE.schema.json` – maschinenlesbarer Nachweisvertrag

## Nächster Entwicklungsblock

**0.5.1-C – DIAGNOSE, DEBUGGING, LOGGING & EVIDENCE-BINDUNG**

Geplante Reihenfolge:

1. zentrale Ereignisstruktur mit stabilen Codefamilien definieren
2. menschenlesbaren und JSON-fähigen Logger mit begrenztem Ringpuffer integrieren
3. Fehlerdialog mit „Was / Wann / Wo / Wie / Ergebnis / Optionen“ und ausschließlich registrierten sicheren Aktionen ergänzen
4. Wiederholungs-, Deduplizierungs- und Regressionsverhalten testen
5. sensible Nutzdaten standardmäßig aus Diagnosen ausschließen
6. Diagnoseexport als JSON und Text bereitstellen
7. Ereignis-/Fehlercodes bis in den Release-Evidence-Vertrag referenzierbar machen
8. danach Windows-Bundle und reale Hardwareabnahme fortsetzen
