# PROVOWARE – NAQYA Memo Tool 2026

Offline-first Organizer für Termine, Fristen, Aufgaben, Dokumente, Fotos, Audio-Memos, Live-Diktat, Projekte, Kategorien, Tags und Chronologie.

## Aktueller Stand

**0.5.0 – TAURI-SIDECAR-INTEGRATION & REPOSITORY-KONSOLIDIERUNG**

NAQYA verarbeitet Sprache lokal und ohne Cloudpflicht. Der Quellstand integriert `whisper.cpp` als bevorzugte native Tauri-Runtime. Tauri ist über `bundle.externalBin` für den Sidecar `naqya-whisper` konfiguriert; GitHub Actions baut den Linux-x86_64-Sidecar reproduzierbar aus dem fest gepinnten Upstream-Commit und prüft das erzeugte Artefakt per SHA-256.

Wichtig: Ein vollständiges Endanwender-Desktoppaket mit eingebettetem Sidecar ist **noch nicht als Release end-to-end abgenommen**. Aktuell validiert CI den Sidecar-Build, seine Integrität sowie Rust/Tauri per `cargo check`. Die vollständige Bundle-Abnahme ist der nächste Freigabeschritt.

Beim Entwickleraudit wurde außerdem eine klar abgegrenzte Restinkonsistenz gefunden: `app.js` verwendet intern noch die Produktversionskonstante `0.2.0`, obwohl der kanonische Projektstand 0.5.0 ist. Diese Konstante beeinflusst UI- und Backup-Metadaten und ist als P1 in `TODO.md` aufgenommen. `DB_VERSION=2` ist davon unabhängig und korrekt das IndexedDB-Schema.

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
2. `docs/ENTWICKLERDOKUMENTATION.md` – Architekturkarte, Vertrauensgrenzen, exakte lokale Befehle und 0.5.1-Übergabepunkt
3. `AGENTS.md` – verbindlicher Entwicklungs-, Merge- und Freigabevertrag
4. `TODO.md` – Prioritäten, Abnahmekriterien und Entwickler-Übergabecheckliste

Die Entwicklerdokumentation beschreibt ausdrücklich, welche scheinbar „vereinfachbaren“ Stellen Sicherheits- oder Dateninvarianten sind. Codekommentare bleiben dazu bewusst kurz und stehen nur direkt an den kritischen Stellen.

## Neu in 0.5.0

- reproduzierbarer whisper.cpp-Runtimevertrag mit festem Upstream-Tag und Commit
- Tauri `bundle.externalBin` für `binaries/naqya-whisper`
- Sidecar-Ausführung über `tauri-plugin-shell`
- Linux-x86_64-Sidecar wird im CI real gebaut und per SHA-256 geprüft
- gebündelter Sidecar hat Vorrang vor einem externen `whisper-cli`-Fallback
- Runtime-Diagnose unterscheidet Sidecar, Fallback und Nichtverfügbarkeit
- keine generische `main`-PATH-Auflösung für whisper.cpp
- temporäre STT-WAV-Dateien liegen im privaten Tauri-App-Cache
- Sprachmodelle werden blockweise materialisiert, per SHA-256 geprüft und atomar aktiviert
- 16-kHz-Mono-PCM16/WAV und segmentiertes Offline-Live-Diktat bleiben erhalten
- `AGENTS.md` und `TODO.md` steuern Entwicklung, Freigabe und Restarbeiten verbindlich
- `.gitignore` schützt Buildausgaben, lokale Modelle und Sidecar-Artefakte vor versehentlichen Commits
- Text-/Metadatenprüfung erkennt Merge-Konfliktmarker, doppelte JSON-Schlüssel und zentrale Dokumentationsdrift
- professioneller Entwickler-Einstieg über `CONTRIBUTING.md` und `docs/ENTWICKLERDOKUMENTATION.md`
- wenige gezielte `ENTWICKLERHINWEIS`-Kommentare sichern schwer erkennbare Invarianten direkt im Code
- Entwickler-Übergabecheckliste macht offene und erledigte Übergabepunkte direkt abhakbar

## Desktop-Spracherkennung

Die native Runtime-Priorität lautet:

1. Tauri-Sidecar `naqya-whisper`
2. explizit verfügbarer lokaler `whisper-cli`-Fallback (`NAQYA_WHISPER_CLI` beziehungsweise kontrollierte `whisper-cli`-PATH-Erkennung)
3. keine native Transkription

Der Fallback darf den Sidecar nicht still überstimmen. Die tatsächlich verwendete Runtimequelle wird diagnostizierbar gehalten. Ein Sidecar, der gestartet wurde und einen Laufzeitfehler meldet, wird nicht still durch den PATH-Fallback ersetzt.

Ein importiertes Modell wird nicht aus einem beliebigen Dateipfad direkt an whisper.cpp übergeben. NAQYA überträgt es in den eigenen App-Datenbereich, prüft SHA-256 und aktiviert es erst danach atomar.

Der Live-Diktatpfad lautet:

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
- Linux-x86_64-Sidecar-Build im CI
- SHA-256-Prüfung des erzeugten Linux-Sidecars
- Tauri-Sidecar-Konfiguration und Rust-Kompilierungsprüfung
- statische Architektur-, Sicherheits-, Text- und Dokumentationsverträge
- Entwicklerdokumentation und Übergabeverträge werden durch statische/Textintegritätsprüfungen mitgesichert

## Noch nicht als Release abgenommen

- vollständiges Linux-Tauri-Bundle mit nachgewiesen enthaltenem und startbarem Sidecar
- reproduzierbarer Windows-x86_64-Sidecar und Windows-Bundle
- konkrete Release-Artefakt-Nachweise mit Dateigröße, SHA-256 und Buildumgebung
- reale Mikrofon-/Hardwareabnahme unter Linux und Windows
- Langzeitmessungen für CPU, RAM, Latenz und Echtzeitfaktor
- `AudioWorklet` als Ersatz für den derzeitigen `ScriptProcessor`
- native Android-/iPhone-/iPad-Adapter

## Qualitätsprüfung

GitHub Actions prüft derzeit:

- JSON-Struktur und eindeutige JSON-Schlüssel
- Textintegrität und Merge-Konfliktmarker
- Konsistenz zentraler Dokumentationsaussagen
- Vorhandensein und Kernverträge der Entwicklerdokumentation
- JavaScript-Syntax
- reproduzierbaren Linux-Sidecar-Build
- SHA-256 des erzeugten Sidecars
- Rust-Formatierung
- Rust/Tauri-Kompilierung
- statische Architektur- und Sicherheitsverträge
- Shell-Syntax

## Dokumentationsstatus

Aktuelle Referenzen:

- `README.md` – kanonischer Gesamtstand und nächster Entwicklungsblock
- `CONTRIBUTING.md` – kurzer Einstieg für neue Mitentwickler
- `docs/ENTWICKLERDOKUMENTATION.md` – kanonische technische Übergabe, lokale Befehle und Änderungsmatrix
- `AGENTS.md` – verbindlicher Entwicklungs-, Merge- und Freigabevertrag
- `TODO.md` – priorisierte Restarbeiten mit Abnahmekriterien und Übergabecheckliste
- `CHANGELOG.md` – tatsächlich umgesetzte Änderungen je Versionsstufe
- `PROJEKTSTATUS.json` und `VERSION.json` – maschinenlesbarer Status
- `docs/ARCHITEKTUR.md` – aktuelle technische Architektur
- `docs/WHISPER_SIDECAR.md` – aktueller Sidecar-/Supply-Chain-Vertrag

Die Dokumente zu 0.2, 0.3 und 0.4 bleiben als **historische Entwicklungsverträge** erhalten und sind entsprechend gekennzeichnet. Aussagen über den heutigen Runtime-Stand werden daraus nicht abgeleitet.

## Nächster Entwicklungsblock

**0.5.1 – LINUX-BUNDLE-ABNAHME, RELEASE-NACHWEIS & WINDOWS-SIDECAR**

Reihenfolge:

1. die kleine PWA-Produktversionsdrift korrigieren und per Konsistenztest absichern
2. Frontend deterministisch in ein eigenes Desktop-`dist/` stagen und `frontendDist` vom Repository-Stamm lösen
3. vollständiges Linux-Tauri-Bundle bauen und nachweisen, dass der Sidecar enthalten und startbar ist
4. Sidecar-Laufzeitabhängigkeiten im Paketkontext prüfen, nicht nur Executable und SHA-256
5. maschinenlesbaren Release-Nachweis mit Plattform, Upstream-Commit, Dateiname, Dateigröße, SHA-256 und Buildumgebung erzeugen
6. denselben Buildvertrag auf Windows x86_64 übertragen
7. reale Linux-/Windows-Mikrofon- und Hardwareabnahme
8. danach AudioWorklet und Langzeithärtung
