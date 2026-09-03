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

