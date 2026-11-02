## [RELEASE-GATE-READONLY-PREFLIGHT] – 2026-11-02
- Sicherheitskorrektur: `RUN_GATE_PREFLIGHT.sh` führt keine potenziell destruktiven Browser-/Android-/iOS- und Langzeit-Gates mehr aus.
- Neue Standardbibliotheks-Voraussetzungsprüfung für Gates 01/02/03/04/06/07; Zustände FOUND/BLOCKED statt vorgetäuschter PASS.
- Regression prüft Kanon-Evidence vor/nach Vorprüfung per SHA-256 und verwirft unbekannte Gates; reale Hardware-Abnahmen bleiben ausstehend, NO-GO 1/7.

## [UNRELEASED] – 02.11.2026 · Release-Evidence-Pfadschutz (konsolidierte Integration)
- Sicherheitslücke: Die kanonische Evidence-Prüfung sperrte direkte Dateisymlinks, aber keine umgeleiteten Elternverzeichnisse.
- Fix im separaten Branch: Pfadkomponenten vom Projektwurzelverzeichnis bis zur Evidence-Datei auf Symlinks prüfen; beide Evidence-Leser lehnen umgeleitete Pfade ab.
- Zwei synthetische Regressionen für Gate-Verzeichnis und Mobile-Source-Elternordner; CI-Ergebnis erst nach PR-Lauf verbindlich.
- Keine neuen Abhängigkeiten; keine Änderung realer Evidence, keine Freigabe, 1/7 reale Gates und NO-GO unverändert.

## 2026-11-01 – iOS Gate 07 Konsolen-Nachweisprüfung (Entwurf)
- Kritischer Release-Gate-Fix: Unvollständige `ProvowareAcceptance`-PASS-Meldungen dürfen kein reales iPhone-X-Gate abschließen.
- Pflichtangaben für Aufnahme, Zähler, iOS-Brücke, Integrität und Persistenz; Regressionen für falsches PASS.
- Keine neuen Funktionen, keine realen Device-Gates freigegeben.

## [ANDROID-GATE06-PASS-EVIDENCE-CONTRACT] – 2026-11-01 · konsolidierte Integration
- Kritische Release-Gate-Korrektur: Ein synthetisches JSON mit nur GATE_06_ANDROID_DEVICE und status=PASS wurde zuvor als reales Android-Gate gezaehlt.
- Der gemeinsame Evidence-Vertrag verlangt bei Android-PASS jetzt passende Geraeteidentitaet, Debug-run und verify, Erinnerungsereignis und Release-APK-Version/-Prozess.
- Vier synthetische Regressionstests; keine neuen Abhaengigkeiten, keine reale Hardware-Evidence. Release bleibt 1/7, NO-GO.

## [GATE-04-CAPTURE-EVIDENCE-CONTRACT] – 2026-11-01 · konsolidierte Integration
- Fehler: Der gemeinsame Release-Evaluator akzeptierte für Gate 04 ein nacktes `status=PASS` ohne Aufnahmedaten.
- Schutz: Bei PASS sind mindestens zwei Sekunden Aufnahmedauer, positive Bytes, Asset-ID und SHA-256-Prüfsumme Pflicht; sonst `INVALID_EVIDENCE`.
- Sechs synthetische Regressionstests im vorhandenen Quality-Workflow; keine Hardwareprüfung, keine neuen Abhängigkeiten.
- Release bleibt 1/7 reale Gates PASS, NO-GO. Patch nicht automatisch zusammenführen.

## [GATE-05-PASS-EVIDENCE-CONTRACT] – 2026-11-01 · isolierter konsolidierte Integration
- Kritische Release-Gate-Lücke: Der Evaluator zählte bisher sogar eine leere Gate-05-`PASS`-Datei als echte Speicherfehler-Abnahme.
- Für `PASS` werden jetzt zwei konkrete Kernel-Proben mit passenden Fehlernummern sowie die bestätigte Anwendungs-Recovery-Matrix verlangt. Fehlende/widersprüchliche Felder ergeben `INVALID_EVIDENCE`.
- Vier synthetische Regressionstests ergänzen den bereits im Quality-Workflow laufenden Evidence-Vertrag. Kein neuer physischer Test, keine Änderung an realen Gate-Nachweisen oder Freigaben; 1/7 PASS, NO-GO.

## [FIREFOX-GATE-STALE-PASS-GUARD] – 2026-11-01 · Konfliktaufgelöste Integration
- Gate 03 konnte bei Unterbrechung der Firefox-Erkennung oder Versionsabfrage einen alten `PASS`-Nachweis stehen lassen.
- Die kanonische Gate-Datei wird vor jeder externen Prüfung auf `BLOCKED` gesetzt; drei synthetische Negativ-/Normalfalltests laufen im Qualitätsworkflow.
- Keine reale Firefox-Abnahme; 1/7 reale Gates, NO-GO; keine neuen Abhängigkeiten.

## [CHROMIUM-SCREENSHOT-PRECHECK-ONLY] – 2026-11-01 · Konfliktaufgelöste Integration
- Reproduziert: Ein künstlicher HTTP-Server ohne Memo-Oberfläche und ein Fake-Chromium, das nur eine Bilddatei schreibt, genügten bisher für Gate-02-`PASS`.
- Der reine Bildschirmfoto-Lauf meldet jetzt `PRECHECK_PASS` mit Exit-Code 2; ein echtes Chromium-App-E2E bleibt zwingend erforderlich.
- Drei isolierte Regressionen prüfen alte Nachweise, fehlende und frische Bilder. Keine reale Browserabnahme, Release weiterhin 1/7 und NO-GO.

## [STORAGE-GATE-STALE-PASS-GUARD] – 2026-11-01 · PR-Entwurf
- Gate 05 schrieb die kanonische Evidence erst am Ende; ein Abbruch vor `/dev/full` oder `/sys` ließ einen alten PASS unverändert.
- Beim Start wird jetzt `RUNNING` geschrieben, bevor Kernel- und Recovery-Prüfungen beginnen. Nur ein vollständig abgeschlossener Lauf darf PASS setzen.
- Zwei simulierte Unterbrechungsfälle und die drei vorhandenen Speicherfehler-Vertragstests sind im Qualitätsworkflow eingebunden. Keine neue reale Linux-Abnahme, weiterhin 1/7 reale Gates und NO-GO.

## [READ-ONLY-BACKUP-STATUS] - 2026-11-01
- P1 aus Code-Review vor Merge behoben: Sicherungsstatus darf SQLite-WAL niemals checkpointen oder Journaldateien entfernen.
- Strikt lesende Inspektion mit expliziter Journal-Sperre; aktuelle Hashprüfung vor und nach dem Lesen, Medienhashprüfung erhalten.
- Sicherheitsregression auf 15 Tests erweitert; bestehende 14 Wiederherstellungsprüfungen weiterhin bestanden. Reale Release-Gates unverändert 1/7, NO-GO.

## [RUNTIME-BOUNDARY-AND-SMALL-SCREEN-FIX] - 2026-11-01

## Sicherheits- und Bedienkorrektur - 01.11.2026

- Statische Dateien bleiben nach URL-Dekodierung und Auflösen von Verknüpfungen im Oberflächenordner; GET und HEAD sperren Ausbruchsversuche mit HTTP 403.
- Der Sicherungsstatus zählt nur aktuell geprüfte Generationen. Datenbanksicherungen und vollständige Projektsicherungen werden getrennt bezeichnet; beschädigte Generationen erzeugen eine sichtbare Warnung.
- Kleine Fenster ordnen den Kopfbereich bei hoher Vergrößerung untereinander an. Die Schnellstartleiste überdeckt die Schriftsteuerung nicht mehr.
- Beschriftungen verwenden Übersicht, Aufgaben, Rückgängig, Wiederholen und Farbschema; Android-/iOS-Webdateien sind synchronisiert.
- Prüfung: 15 Sicherheitsfälle, 14 Wiederherstellungsfälle, 5 Persistenzfälle, 20 bestehende Oberflächenverträge und echte Chromium-Memoabläufe bei 800 x 600 / 100, 150, 200 Prozent bestanden.
- Keine reale Kubuntu-/Hardwarefreigabe: kanonische Release-Gates unverändert 1/7, NO-GO. Details: docs/QA_RUNTIME_UI_20261101.md.

## [GATE-EVIDENCE-GUARDS-CONSOLIDATED] – 2026-11-01 · Integrationskandidat
- PR #121: fehlgeschlagenes Löschen von Android-Daten oder Logeinträgen sperrt ein neues Hardware-PASS.
- PR #122: der neue 8h-Test entwertet den alten PASS vor der Initialisierung.
- PR #123: der neue Chromium-Test entwertet den alten PASS vor dem Browserstart.
- PR #124: der neue Mikrofontest entwertet den alten PASS vor Imports/Geräteerkennung.
- Gemeinsamer GitHub-Qualitätsworkflow enthält die zugehörigen isolierten Negativtests. Vor dem abschließenden Integrations-CI und dem Herkunftsabgleich sind Änderungen nicht freigegeben. Echte Release-Gates: 1/7 PASS, NO-GO.

## [ANDROID-GATE-STALE-PASS-GUARD] – 2026-10-31 · PR-Entwurf
- Kritischer Gate-Nachweisfehler: Ein unterbrochener neuer Android-Prüflauf konnte eine alte `PASS`-Datei unverändert stehen lassen.
- `GATE_06_ANDROID_DEVICE.json` wird vor dem ersten ADB-Aufruf auf `BLOCKED` gesetzt; ADB-Geräteauflistung mit Timeout, Betriebssystemfehler oder fehlerhaftem Rückgabewert wird kontrolliert abgewiesen.
- Drei isolierte Regressionstests in `quality.yml`; keine Hardware-Evidence und keine Freigabe. Reale Gates unverändert 1/7 PASS, NO-GO.

## [RELEASE-EVIDENCE-IDENTITY-GUARD] – 2026-10-25 · Entwicklungszweig / Source-CI PASS
- Release-Evaluator nutzte bislang `GATE_XX_*.json` mit lexikographisch letzter Datei; eine zusätzliche Datei konnte kanonische Evidence überdecken.
- Gemeinsamer Evidence-Vertrag für Evaluator und Statuskonsolidierung: exakte Dateinamen, Gate-ID, JSON-Objekt und gültiger Status; ungültige oder symbolisch verknüpfte Dateien werden abgewiesen.
- Achtstündiger Dauertest kann nicht allein durch `status=PASS` aus einem Kurztest hochgestuft werden; 8h-Dauer, FULL_8H, Integrität und fehlerfreier Lauf werden vorausgesetzt.
- Zehn synthetische Regressionstests einschließlich echter Evaluator-Ausführung in isoliertem Testverzeichnis in GitHub-Quality-Gate eingebunden.
- Source-CI auf Code-HEAD 25aef6bb: PASS (Lauf 40148667614); finaler Ergänzungs-HEAD erneut zu prüfen. Reale Release-Gates unverändert 1/7 PASS, NO-GO. Diese Quellprüfung ersetzt keine reale Abnahme.

## [RELEASE-WORKFLOW-PIN-GUARD-FOLLOWUP] – 2026-10-24 · Source-CI PASS
- Sicherheitslücke: `.yaml`-Workflows und externe `uses:`-Zeilen ohne `@ref` entgingen der bisherigen Prüfung.
- Erkennung auf beide Workflow-Endungen erweitert und ungültige/fehlende Referenzen fail-closed abgewiesen.
- Drei zusätzliche Regressionstests (insgesamt acht); GitHub-Qualitätslauf 40083337035 auf Source-HEAD c60f12ffbcb02ac0e9c736233e2c2ef96f1ce555: PASS. Dokumentations-Synchronisation danach separat zu prüfen.
- Release-Gates unverändert 1/7 PASS, NO-GO, kein Merge/Release.

## [RELEASE-WORKFLOW-PIN-GUARD] – 2026-10-24 · Entwicklungszweig / CI PASS
- Sicherheitsrelevante Fehlfunktion in `validate_workflow_pins`: der bisherige Ausdruck erkannte eingerückte `uses:`-Zeilen nicht und konnte veränderliche Actions-Referenzen nicht beanstanden.
- Regulären Ausdruck für eingerückte, Listen- und zitierte Actions-Referenzen korrigiert.
- Fünf Regressionstests ergänzt und verbindlich in `quality.yml` eingebunden.
- GitHub-Qualitätslauf `40036550235` auf Prüf-Head `27f1c9319c7f2830444e084e86f8ce9ec7693071`: **PASS**; keine Änderung an den sieben realen Release-Gates, keine Veröffentlichung.

---

# 🧾 CHANGELOG

## [NAQYA-v0.3.16-PRE-AUTOSAVE-R3-EVIDENCE] – 2026-09-03
### 🟢 Bewiesen
- PR #102 auf Quell-Head `dfa68c478ea3edd4465760e85013196f619e06d1` vollständig ausgeführt.
- Linux, Windows und macOS: realer Prozess-Kill → Recovery → 5.000 Datensätze jeweils PASS.
- Firefox: reale Browserprozess-Kills + IndexedDB-Recovery + 5.000 Einträge PASS.
- Evidence-Merge akzeptierte ausschließlich den exakten r3-Plan und die exakten eingefrorenen Quellen.
- Plan `NAQYA-PRE-AUTOSAVE-ACCEPTANCE-v0.3.16-r3`, Hash `5d2d4a189bf73b4686e9d4608ef29b95f7aae055bb46299700b99f341da5e747`.
- Acceptance-Kit SHA-256 `36add593789e25dc3ea9406371f7fdb6ac473cdd795ab02df26dec09dc108752`.
- Verbindlicher CI-Lauf: `33778124686`.

### 🔒 Statussemantik
- PRE-AUTOSAVE = **PASS** als gate-lokale Voraussetzung.
- Kanonischer Repository-Evaluator: **NO-GO**, Exit-Code `2`, 1/7 reale Release-Gates.
- SAFE AUTOSAVE bleibt deshalb **nicht zur Implementierung freigegeben**.
- Kein Produkt-/UI-Code wurde durch diesen Dokumentationssync verändert.

---

# 🧾 CHANGELOG

## [0.12.2-MOBILE-RUNTIME-COMPLETION] – 2026-08-28 · FINAL RELEASE CONSOLIDATION
### 🟢 Konsolidiert
- Status- und Versionsregistry auf V0.12.2
- Mobile Source Acceptance erneut PASS
- Cross-Runtime-Parität erneut PASS
- vier Mobile-Backupgenerationen inklusive Binär-Assets, SHA-256 und Restore bestätigt
- Android Runtime Source Release-Paket
- iOS Xcode Runtime Source Release-Paket
- aktualisierte Release-/Evidence-Manifeste und SHA-256-Artefaktliste

### 🟡 Bewusst offen
- Android SDK/APK/echtes Gerät
- macOS/Xcode/signierte iOS-App/iPhone X mit iOS 16.7.16
- reale Gates 01–04

### 🔴 Releaseentscheidung
- V1.0 RC bleibt NO-GO bei 1/7 realen Gates.

---

# 🧾 CHANGELOG

## [0.12.2-MOBILE-RUNTIME-COMPLETION] – 2026-08-28
### 📱 Variante 2 / Plattform-Parität
- Android WebView Runtime statt leerer Activity-Shell
- iOS WKWebView App-Target statt Packaging-Konzept
- Mobile API + IndexedDB-Domainruntime
- profilgetrennte Daten + 4-stelliger PBKDF2-PIN
- Native Reminder Schedule/Cancel
- Android MediaRecorder / iOS AVAudioRecorder
- native Share-/Dateiauswahl-Pfade
- Mobile Asset-Hashing, Quota, Dokumentrevisionen
- Device-Acceptance-Modus für Audio/Reminder/Persistenz

### 🧪 Qualität
- Desktop-Regressions-Sanity 78/78 PASS
- Mobile-Core-Contract PASS
- Mobile-Source-Contract 4/4 PASS
- Python↔Mobile Cross-Runtime-Parity PASS
- Kotlin BridgeContract kompiliert
- Swift BridgeContract + iOS Source parse PASS
- Info.plist lint PASS

### 🚦 Release
- Android SDK/ADB in aktuellem Runner nicht vorhanden → Build/Device BLOCKED
- macOS/Xcode nicht vorhanden → iOS Build/Device BLOCKED
- reale Release-Gates weiterhin 1/7 → V1.0 RC NO-GO

---

# 🧾 CHANGELOG

## [0.12.1-RELEASE-GATE-CLOSURE] – 2026-08-28
### 🔒 Feature Freeze
- Neue Features gesperrt.
- 7-Gate Release-Evaluator eingeführt.
- PASS ist die einzige freigabewirksame Evidence.

### 🧪 Gate Closure
- 8h-Soak-Harness mit persistenten Checkpoints; Preflight grün, echter 8h-Lauf offen.
- Chromium real gestartet: Service bereit, Browser in dieser Runner-Umgebung Timeout → BLOCKED.
- Firefox nicht installiert → BLOCKED.
- kein reales `/dev/snd`/Pulse-Aufnahmegerät → Linux-Mikrofon BLOCKED.
- echter Kernel-Storage-Test `/dev/full` → ENOSPC PASS.
- echter read-only Mount `/sys` → EROFS PASS.
- Android: kein ADB/APK → BLOCKED; Buildstruktur ist noch kein Releaseartefakt.
- iOS: Linux-Runner, kein Xcode/signiertes App → BLOCKED.
- Release bleibt 1/7 PASS = NO-GO.

### 🟢 Regression
- V0.12 Kernbasis unverändert 89/89 PASS.
- V0.12.1 gezielte Regression-Sanity 29/29 PASS.

---

# 🧾 CHANGELOG

## [0.12.0-RC-HARDENING] – 2026-08-28
### 🟢 RC Hardening
- Asset Transaction Journal mit Kill-Recovery
- Full Project Checkpoint für SQLite + Assets
- 100k-Datensatz-Stress
- 80-MiB Asset-Stress
- ENOSPC/Permission Failure-Injection
- Korruptions-/Quarantäne-Matrix
- Upgrade-Kompatibilitätsfixture
- Startup-/Memory-/Query-Budgets
- Linux Portable E2E
- SBOM + Release-Gates

### 🚦 Freigabe
- V0.12 Core: **PASS**
- V1.0 RC: **NO-GO**, da native Cross-Platform-/Browser-/Endurance-Evidence offen ist.

---

# 🧾 CHANGELOG

## [0.11.0-NATIVE-MEDIA-PACKAGING] – 2026-08-28
### 🟢 Medien / Dokumente
- Linux FFmpeg Recording Adapter mit Staging
- Audio Asset Commit
- PDF read-only Viewer
- TXT/MD revisionsgesicherter Editor
- Asset-Revisionshistorie
- HTML5-Audio-Wiedergabe

### 📦 Packaging
- Linux Portable TAR.GZ
- Android Gradle-/Manifest-/Kotlin-Struktur
- iOS Info.plist und Packaging-Konzept

### 🧪 V0.11 Abschlussvalidierung
- vollständige Kern-/Medien-/Dokument-/Packaging-Regression: **43/43 PASS**
- Linux Portable frisch entpackt und `/api/health`: **PASS**
- PDF/Text-Service-E2E: **PASS**

### ⚠️ Evidence-Grenzen
- kein physisches Mikrofon als getestet behauptet
- kein Android APK gebaut
- kein iOS/Xcode Build möglich in Linux

---

# 🧾 CHANGELOG

## [0.10.0-CALENDAR-REMINDER-PLATFORM] – 2026-08-28
### 🟢 Kalender
- Tages-, Wochen-, Monats- und Jahresansicht

### 🟢 Reminder
- Fälligkeitserkennung
- plattformspezifische Deduplication-Evidence

### 🧪 Plattform/A11y
- Linux native Capability Probe
- Android/iOS Contract Evidence
- Chromium: BLOCKED
- Firefox: BLOCKED

---

# 🧾 CHANGELOG

## [0.9.0-ASSET-SAFETY] – 2026-08-28
### 🟢 Asset-Sicherheit
- Audio/Dokument AssetManager
- Temp/Commit mit fsync
- SHA-256 Manifeste
- Quota
- Quarantäne
- Asset Backup Verify
- PlaylistService
- UI-/API-Grundbindung

---

# 🧾 CHANGELOG

## [0.8.0-INTERACTION-CALENDAR-ACCEPTANCE] – 2026-08-28
### 🟢 Interaktion
- Memo/Todo/Termin bearbeiten
- revisionsgesicherte Edits
- Papierkorb-Wiederherstellung
- echter Monatskalender
- persistente Tagesfärbung
- editierbare 5er-Farblegende

### 🛡️ Diagnose
- Privacy-Vorschau vor Berichtserzeugung
- lokale TXT-Ausgabe erst nach Bestätigung
- Memo-Inhalte, PIN und Tokens standardmäßig ausgeschlossen

### 🧪 QA
- Core-/Service-Regression: 58/58 PASS
- Chromium: BLOCKED durch Laufzeit-Administratorregel
- Firefox: BLOCKED, Engine in dieser Umgebung nicht installiert

---

# 🧾 CHANGELOG

## [0.7.0-SERVICE-UI-BINDING] – 2026-08-28
- UI-Service-Bridge via localhost HTTP
- Memo/Todo/Kalender angebunden
- Quick-Note TXT + Öffnen + Teilen
- nächste 10 Live-Daten
- Undo/Redo und Papierkorb-Flows
- Linux Reminder/Share/Open Adapter
- API-E2E + UI-Contract-Tests

---
# 🧾 CHANGELOG

## [0.6.0-PRESENTATION-SHELL] – 2026-08-28
### 🟢 Presentation
- responsive Shell als frameworkfreie Referenz
- Header-Dashboard, Navigation, Quickbar, Workspace, Sidepanel, Footer
- Mobile Drawer und Safe-Area-Unterstützung
- 4 Theme-Tokens
- persistente Theme-/Font-Präferenz im Referenzbrowser
- Bereichszoom
- Accessibility-Grundlagen
- keine Fachlogik im UI
- statische Acceptance grün; Chromium-Screenshot-Evidence im Container blockiert und bewusst nicht als bestanden behauptet

---
# 🧾 **CHANGELOG**

## [0.5.0-STARTUP-PROFILE-CAPABILITY] – 2026-08-28
### 🟢 Hinzugefügt
- Daten-Schema V2 + Migration V1→V2
- ProfileService
- PBKDF2-SHA256 PIN-Hashing
- PIN-Zugriffsprotokoll
- persistente Settings
- ProjectFolderService
- GuidedFirstStart State Machine
- Capability-/Permission-Adapter Linux/Android/iOS
- versionierte ausgelagerte deutsche Texte
- V0.5 Acceptance Suite

### 🛡️ Schutz
- externe Pfadbestätigung nicht deaktivierbar
- Projektordner mit Schreibprobe und Mindest-Speicherprüfung
- keine falsche native Android/iOS-Evidence
- PIN ausdrücklich nicht als Verschlüsselung dargestellt

---
# 🧾 CHANGELOG

## [0.4.0-DOMAINMODULE] – 2026-08-28
- MemoService
- TodoService
- CalendarService
- persistentes Undo/Redo-Journal
- Domain Validation Contract
- kombinierte Regression Persistence + Recovery + Domain

---

# 🧾 **CHANGELOG**

## [0.3.0-RECOVERY-ACCEPTANCE] – 2026-08-28
### 🟢 Recovery Gate
- Single-Writer Mutation Queue
- Projektinstanz-Lock mit stale-PID-Erkennung
- echter Restore in frischen Projektordner
- Restore-Hash- und SQLite-Integrity-Nachweis
- Undo/Redo-Referenzsemantik
- Subprozess-Kill vor BEGIN
- Subprozess-Kill nach BEGIN
- Subprozess-Kill nach Write/vor Commit
- Subprozess-Kill nach Commit
- DB-lock Acceptance
- Entity-Checksum-Manipulation erkannt
- beschädigtes Backup abgelehnt
- Failure-Code-Klassifikation für Disk-full/Permission denied
- Read-only Preflight

### 🟡 Plattformabhängig offen
- native Linux/Android/iOS Failure-Injection mit echten Berechtigungs-/Speicherzuständen

---
# 🧾 **CHANGELOG**

## [0.2.0-DATENKERN] – 2026-08-28
### 🟢 Implementiert
- SQLite-Kernschema V1
- Profile und generische versionierte Entities
- UUIDv4-Identitäten
- Optimistic Concurrency über `expected_revision`
- SHA-256 Payload-Prüfsummen
- Operation Journal
- Soft Delete als Papierkorb-Grundzustand
- atomare Datei-Schreibfunktion
- SQLite WAL + `synchronous=FULL`
- konsistente Backup-Erstellung über SQLite Backup API
- Backup-Manifest + SHA-256 + Integrity-Verifikation
- fünf ausführbare Acceptance-Tests

### 🧭 Architekturentscheidungen
- ADR-0001 SQLite + Datei-Assets
- ADR-0002 IDs/Revisionen/Konflikte
- ADR-0003 Referenzkern ohne UI-Stack-Lock-in

### 🟡 Offen für V0.3
- echte Prozess-Kill-Matrix
- vollständiger Restore in frischen Projektordner
- Mutation Queue/Locking
- Undo/Redo-Journal
- Disk-full/Read-only/Permission-Failure-Injection

---
# 🧾 **CHANGELOG**
## OI - PROVOWARE - IO

### [0.1.0-ARCHITEKTUR] – 2026-08-28
#### 🟢 Hinzugefügt
- vollständige V0.1 Architektur-Spezifikation
- Sicherheits- und Datenverträge
- Datenmodell
- Plattformadapter-Konzept
- Gate-State-Machine
- strukturierte Entwicklungsdokumentation
- AGENTS.md mit Trigger-Unteragenten
- BRAIN.md
- GPT_TAGE_UND_WISSENSBUCH.md
- UPGRADE_POTENZIAL.md
- Manifeste und Status-Registry
- P0–P3 Roadmap

#### 🛡️ Sicherheitsverbesserungen
- atomare Mutation als verbindliches Ziel
- Backup-Restore-Beweis
- Debug-Privacy-Filter
- Mehrfachinstanzschutz
- Kill-/Crash-Testmatrix
- klare PIN≠Verschlüsselung-Regel

## [0.12.2.1-STARTUP-PORT-GUARD] – 2026-08-28
### 🛠️ Startup-Hotfix
- Linux-Launcher prüft Port vor Backend-Initialisierung.
- gleiche Version + gleicher Projektordner wird wiederverwendet.
- fremde/stale Belegung wird niemals automatisch beendet.
- sicherer Ersatzport 8766–8795 wird automatisch gesucht.
- Direktstart des Servers gibt bei `EADDRINUSE` verständlichen Hinweis aus.
- API-/Health-Version wird aus `registry/VERSION.json` statt aus veralteter Hardcodierung gelesen.

- Startup-Hotfix verwendet `python3 -S`, damit fremde `sitecustomize`-/Site-Pakete den Klick-&-Start nicht verzögern oder verfälschen.

## [0.12.2.2-RELEASE-UI-CONSISTENCY] – 2026-08-28
### 🟢 Release-UI-Härtung
- sichtbare Versionen kommen ausschließlich aus `registry/VERSION.json` über `/api/state`
- alte UI-Version `0.8.0` und statische V0.12/V0.12.2-Anzeigen entfernt
- Backup-Kachel behauptet ohne Generationen nicht mehr `Recovery aktiv`
- Statuskacheln verwenden kurze, vollständig lesbare Werte
- Bereichszoom auf 80–200 % erweitert und mit responsiven Layout-Tiers gekoppelt
- Schnellleiste verhindert vertikalen Scrollbar-Fehler
- Sprachmemo-Rohdaten standardmäßig in `Technische Details` eingeklappt
- Desktop-Dateiauswahl über sicheren gestreamten Upload; manueller Pfad nur noch Profi-Option

## [0.12.2.3-UI-SIMPLIFICATION-INPUT-GUIDANCE] – 2026-08-28
### 🧩 Vereinfachung
- sichtbare Versionsinformation auf `TOOL-INFO` beschränkt
- Statuskacheln 4→3 und Dashboardkarten 6→4
- doppelte Darstellungs-/Workspace-Hinweise entfernt
- Einstellungen auf Hilfemodus reduziert

### ⌨️ Eingabeführung
- neutrale Silber-/Graphitfarbe statt Markenfarben
- optionale Beispiele/Vorgaben für Titel, Text, Tags, Beschreibung, Zeiten, Reminder, Priorität, Farben, Dateien, Pfade und Hilfemodus
- Hinweise sind optional und verändern keine Daten automatisch

### 📐 Layout
- linke Schnellnavigation neu proportioniert
- horizontale Navigationsoverflows unterbunden
- 80–200-%-Zoom mit adaptiver Neuordnung
- All-Views-Visual-Acceptance-Runner für Ziel-Linux ergänzt

### 🧪 Evidence
- gezielte Regression 57/57 PASS
- Browser-Visual-PASS im aktuellen Build-Runner nicht behauptet

