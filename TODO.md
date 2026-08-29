# ✅ **TODO – OI - PROVOWARE - IO**
## **Priorisierte Entwicklungsroadmap**

> Legende: 🔴 P0 kritisch · 🟠 P1 sehr wichtig · 🟡 P2 wichtig · 🔵 P3 Ausbau  
> Regel: Ein Punkt ist erst **[x]**, wenn Implementierung **und Evidence** vorhanden sind.

---

## 🔴 **P0 – Fundament / Schutz / Datenintegrität**

- [x] V0.1 Anforderungen konsolidieren
- [x] V0.1 Architekturgrenzen festlegen
- [x] V0.1 Plattformadapter definieren
- [x] V0.1 Datenmodell entwerfen
- [x] V0.1 Gate-State-Machine definieren
- [x] V0.1 Entwicklungsdokumentation definieren
- [x] V0.1 Manifeststruktur definieren
- [x] V0.2 kanonische IDs und Schema-Versionierung implementieren
- [x] V0.2 atomare Datei-Schreibschicht implementieren
- [x] V0.3 zentrale Mutation Queue implementieren und Reihenfolge beweisen
- [x] V0.3 Mehrfachinstanz-/Lock-Schutz implementieren
- [x] V0.2 Prüfsummen für kritische Daten integrieren
- [ ] V0.2 4-Generationen-Rotation vollständig implementieren (Snapshot + Verify-Grundlage ist fertig)
- [x] V0.2 Backup separat öffnen + Integrity-Check automatisieren
- [x] V0.3 vollständigen Restore in frischen Projektordner + Inhaltsvergleich beweisen
- [x] V0.2 Soft-Delete/Papierkorb-Datenzustand implementieren
- [x] V0.3 Undo/Redo-Semantik implementieren und beweisen
- [ ] V0.4 Undo/Redo-Journal persistent an Domainmutationen anbinden
- [x] V0.3 Crash-/Transaction-Kill-Matrix aufbauen und Kernphasen beweisen
- [x] V0.3 Disk-full/Permission-denied klassifizieren + Read-only Preflight beweisen
- [ ] Plattform-Gate: echte OS-native Disk-full/Read-only/Permission-Injection auf Linux/Android/iOS
- [ ] V0.2 Import-/Export-Paket mit Version und Integritätsmanifest definieren
- [ ] V0.2 Privacy-Filter für Debugpakete implementieren
- [ ] V0.2 PIN-Hinweis und PIN-Recovery-Konzept implementieren
- [ ] V0.2 Zeit-/Zeitzonen-/DST-Verträge festlegen

## 🟠 **P1 – Produktkern**

- [ ] Textmemo CRUD
- [ ] feste Titel-Textdatei im Projektordner mit Append über Enter/Button
- [ ] Sprung zur Textdatei / Standardeditor-Adapter
- [ ] Sprachmemo-Aufnahme + sichere Dateiverwaltung
- [ ] Todo + Termin + Erinnerung + Archiv
- [ ] Kalender Tag/Woche/Monat/Jahr
- [ ] 5 editierbare Kalenderfarben + Legende
- [ ] persistente Tagfärbung in Monatsansicht
- [ ] nächste 10 Aufgaben/Termine im Header-Dashboard
- [ ] globale Suche + Filter + Tags + Favoriten
- [ ] unterminierte Notizen
- [ ] PDF-/Dokumentenbetrachter
- [ ] kontrollierter Dokumenteditor
- [ ] Textdokument erstellen + PDF exportieren
- [ ] Audio-Player + persistente Playlist
- [ ] Zitatverwaltung + 10-Minuten-Rotation
- [ ] Profile + PIN
- [ ] Einstellungen persistent
- [ ] 4 Themes
- [ ] Schriftgrößen + Bereichszoom
- [ ] 3 Hilfs-/Konfigurationsmodi

## 🟡 **P2 – Laienführung / Qualität / Accessibility**

- [ ] Guided First Start
- [ ] Berechtigungs-Preflight
- [ ] Projektordner prüfen/erstellen/reparieren
- [ ] System-/Display-/Capability-Scan
- [ ] automatische Adapterauswahl
- [ ] kontrastgesicherte UI-Tokens
- [ ] Tooltips außerhalb von Bedienelementen
- [ ] leere Zustände mit nächster Aktion
- [ ] Accessibility-Gate
- [ ] Keyboard-/Touch-/Maus-Matrix
- [ ] Screenreader-Beschriftungen
- [ ] Responsive-Acceptance-Matrix
- [ ] 200-%-Zoom-Tests
- [ ] Performance-Budgets
- [ ] 1k/10k/100k Datensatz-Stresstest
- [ ] Belohnungssystem mit echten Statistiken
- [ ] Level-/Fleiß-Punkte + ironische Level-Sprüche

## 🔵 **P3 – Entwickler-, Diagnose- und Ausbauplattform**

- [ ] versteckbarer Entwicklerbereich
- [ ] Diagnose-Center
- [ ] detaillierter Crash-/Exit-Bericht als TXT im Standardeditor
- [ ] Lösungshinweise im Bericht
- [ ] Self-Repair-Regelwerk
- [ ] BRAIN-Einlesung + Konsolidierung
- [ ] Regression Registry
- [ ] Golden-Screenshot-/Layout-Regression
- [ ] Testdaten-Generator
- [ ] reproduzierbarer Release Builder
- [ ] SBOM + Lizenzbericht
- [ ] Release-Prüfsummen
- [ ] Autoformatter/Linter
- [ ] Dokumentations-Drift-Gate
- [ ] Manifest-Drift-Gate
- [ ] File-Status-Registry-Gate
- [ ] plattformspezifische Reminder-Acceptance
- [ ] später optional echte Profilverschlüsselung

---

## 📌 **Definition of Done**

Ein TODO darf nur abgehakt werden, wenn:

- [ ] Code/Artefakt vorhanden
- [ ] PRE- und POST-Bedingungen geprüft
- [ ] Fehlerpfad geprüft
- [ ] automatischer Regressionstest vorhanden
- [ ] Evidence referenziert
- [ ] README/TODO/CHANGELOG/PROJECT_STATUS synchronisiert
- [ ] Auswirkungen auf Datenschutz, Recovery und Accessibility geprüft


## 🟢 V0.4 Domain Gate
- [x] Memo CRUD Domainkern
- [x] Todo Domainkern mit Termin-/Reminder-Regeln
- [x] Kalender-Datenkern
- [x] exakt fünf editierbare Kalenderfarben
- [x] persistente Tagesfärbung
- [x] nächste-10-Aggregation
- [x] persistentes Undo/Redo an Domainmutationen
- [ ] UI Tag/Woche/Monat/Jahr
- [ ] UI Header-Darstellung nächste 10


---
## 🟢 V0.5 – ABGESCHLOSSEN
- [x] Schema V2 und Migration V1→V2
- [x] Profile anlegen
- [x] 4-stelligen PIN validieren und gesalzen hashen
- [x] PIN prüfen und Zugriffsversuche protokollieren
- [x] PIN-Wechsel nur nach aktuellem PIN
- [x] persistente 4 Themes
- [x] persistente Schrift-Skalierung 80–200 %
- [x] persistenter Hilfemodus 1/2/3
- [x] externe Pfadbestätigung als nicht abschaltbare Schutzregel
- [x] Projektordner prüfen/erstellen + Schreibprobe + Speicherprüfung
- [x] Guided First Start State Machine
- [x] Start-Checkpoint im Projektordner
- [x] Capability-/Permission-Verträge Linux/Android/iOS
- [x] deutsche UI-/Hilfetexte als versionierte JSON-Ressource
- [x] kombinierte Regression V0.1–V0.5

## 🔵 V0.6 – NÄCHSTER SCHRITT
- [ ] responsive Presentation Shell
- [ ] Header-Dashboard
- [ ] Menü-/Schnellstartleiste
- [ ] Footer mit Tool/Debug/Log-Status
- [ ] leere Arbeitsfläche
- [ ] linke/rechte adaptive Bereiche bzw. Drawer für Mobile
- [ ] Theme-Tokens und Kontrast-Gate
- [ ] Schrift-/Bereichszoom darstellen
- [ ] noch keine direkte Fachlogik in Views


## 🟢 V0.6 – Presentation Shell
- [x] responsives Dashboard-Grundgerüst
- [x] Header-Dashboard
- [x] Hauptmenü
- [x] Schnellstartleiste
- [x] leerer modularer Arbeitsbereich
- [x] Kontext-/Infoleiste
- [x] kleiner Debug-/Logging-Footer
- [x] Mobile Drawer
- [x] Desktop-/Kompakt-/Mobil-Breakpoints
- [x] 4 Theme-Tokens
- [x] Kontrast-Acceptance
- [x] Schrift 80–200 %
- [x] Bereichszoom 80–150 %
- [x] Reduced-Motion/Fokus/Skip-Link
- [x] UI enthält keine Domain-/SQLite-Schreiblogik
- [ ] Browser-Runner: Desktop/Mobil/Kompakt Screenshot-Evidence (Container-Browser hier blockiert)
- [x] statische Desktop/Mobil/Kompakt Responsive-Contracts
- [ ] V0.7 Memo-Service anbinden
- [ ] V0.7 Todo-Service anbinden
- [ ] V0.7 Kalender-Service anbinden
- [ ] V0.7 Reminder-/Share-/Standardeditor-Adapter in UI-Flows


## 🟢 V0.7 SERVICE-UI-BINDING
- [x] lokaler Application API Service
- [x] Memo-UI anbinden
- [x] Todo-UI anbinden
- [x] Kalender-UI anbinden
- [x] Header-Schnelleingabe in feste TXT
- [x] nächste 10 echte Todo-/Termin-Daten
- [x] Papierkorb-Fluss
- [x] Undo/Redo-Fluss
- [x] Linux Standardeditor-/Öffnen-Adapter
- [x] Linux Share-Adapter ohne Auto-Versand
- [x] Linux Reminder-Referenzadapter
- [ ] V0.8 Memo/Todo/Termin Edit-UI
- [ ] V0.8 Monatskalender Tag-Klick-Färbung
- [ ] V0.8 echte Browser-E2E Firefox + Chromium
- [ ] V0.8 Debug-/Diagnosepaket mit Privacy-Vorschau

## 🟢 V0.8 – abgeschlossen
- [x] Memo bearbeiten
- [x] Todo bearbeiten
- [x] Termin bearbeiten
- [x] echter Monatskalender
- [x] Tag per Klick persistent einfärben
- [x] fünf Kalenderfarben/Titel editierbar
- [x] Papierkorb-Wiederherstellung
- [x] persistentes Undo/Redo weitergeführt
- [x] Diagnose-Privacy-Vorschau
- [x] lokale Diagnose-TXT nur nach Bestätigung
- [x] Browser-Acceptance-Skript für 390/768/1366/1920
- [ ] Chromium Visual Gate auf uneingeschränktem lokalen Runner wiederholen
- [ ] Firefox-E2E auf Runner mit installierter Firefox-Engine

## 🔵 Nächster Slice V0.9
- [ ] Sprachmemo-Aufnahmeadapter
- [ ] Audio-Asset-Manifest + Recovery
- [ ] PDF-/Dokumentenbetrachter
- [ ] sichere Dokumentbearbeitung
- [ ] persistente Audio-Playlist
- [ ] Asset-Quota/Storage-Dashboard

## 🟢 V0.9 – Asset Safety
- [x] Audio-Asset-Manifest
- [x] Dokument-Asset-Manifest
- [x] sichere Temp→Commit-Pipeline
- [x] SHA-256 Asset-Prüfung
- [x] Asset-Quota
- [x] beschädigte Asset-Quarantäne
- [x] Asset-Backup mit Hash-Nachprüfung
- [x] persistente Playlist-Grundlage
- [x] UI-Grundbindung für Audio/Dokumente
- [ ] Native Sprachaufnahme Android/Linux/iOS Capability Gate
- [ ] eingebetteter PDF-/Dokumentenviewer
- [ ] kontrollierter Dokumenteditor

## 🔵 V0.10
- [ ] Tagesansicht
- [ ] Wochenansicht
- [ ] Jahresansicht
- [ ] echte Reminder-Acceptance
- [ ] Accessibility Browser Gate
- [ ] Linux/Android/iOS Evidence

## 🟢 V0.10 – Kalender / Reminder / Plattform
- [x] Tagesansicht
- [x] Wochenansicht
- [x] Monatsansicht
- [x] Jahresansicht
- [x] Reminder-Fälligkeit
- [x] Reminder-Dedup
- [x] Linux Capability Runtime Probe
- [x] Android Capability Contract
- [x] iOS Capability Contract
- [x] Accessibility Browser Gate automatisiert
- [ ] Chromium Visual/A11y Evidence
- [ ] Firefox Visual/A11y Evidence
- [ ] Android echte Device-Evidence
- [ ] iOS echte Device-Evidence

## 🔵 V0.11
- [ ] native Sprachaufnahme
- [ ] echter PDF-/Dokumentenviewer
- [ ] kontrollierter Dokumenteditor
- [ ] Linux-Paket/portable Start
- [ ] Android Packaging
- [ ] iOS Packaging-Konzept und Build-Gate

## 🟢 V0.11 – Native Media & Packaging
- [x] Linux Audio-Aufnahmestaging
- [x] Audio Temp→Commit über AssetManager
- [x] synthetische FFmpeg-Aufnahme-Acceptance
- [ ] reales Mikrofon auf Ziel-Linux-System nachweisen
- [x] PDF read-only Viewer-Endpunkt
- [x] TXT/MD revisionsgesicherter Editor
- [x] Asset-Revisionshistorie
- [x] HTML5-Audioplayer
- [x] Linux Portable TAR.GZ
- [ ] Linux Portable Health-Start
- [x] Android Buildstruktur + Permission Manifest
- [ ] Android SDK-Build + Device Acceptance
- [x] iOS Info.plist + Packaging-/Permission-Konzept
- [ ] Xcode-Build + iPhone-X/iOS-16.7.x Acceptance

## 🔴 V0.12 Release Candidate Hardening
- [ ] vollständige Failure-Matrix erneut gegen RC
- [ ] 100k-Datensatz-/Performance-Test
- [ ] große Asset-/Quota-/Backup-Stresstests
- [ ] Restore aus vollständigem Releaseprojekt
- [ ] Cross-Platform Acceptance Matrix
- [ ] Release Manifest + SBOM + Prüfsummen
- [ ] GO/NO-GO Gate

## 🟢 V0.12 – RC HARDENING KERN
- [x] vollständige Kern-Regression 89/89
- [x] 100.000-Datensatz-Stresstest
- [x] 40 große Audio/PDF-Assets / ca. 80 MiB
- [x] Disk-full Failure-Injection
- [x] Permission-denied Failure-Injection
- [x] Asset-Kill an vier Commit-Phasen
- [x] beschädigtes DB-Backup ablehnen
- [x] beschädigtes Asset quarantänisieren
- [x] vollständiger DB+Asset-Restore in frischen Projektordner
- [x] V0.10-kompatibles Schema-v2-Upgrade-Fixture
- [x] Startup-/Memory-/Query-Budgets
- [x] Linux Portable E2E
- [x] SBOM
- [x] Release-/Evidence-Manifeste
- [x] GO/NO-GO Dashboard

## 🔴 Pflicht vor V1.0 RC
- [ ] 8h+ Langzeit-/Endurance-Test
- [ ] Chromium Visual/A11y auf uneingeschränktem Runner
- [ ] Firefox Visual/A11y
- [ ] Android natives Build + reales Gerät
- [ ] iOS Xcode Build + reales iPhone X / iOS 16.7.x
- [ ] physische Mikrofonaufnahme auf Zielsystem
- [ ] native Disk-full-/Read-only-Tests auf Zielsystemen


## 🔒 V0.12.1 – RELEASE-GATE CLOSURE
- [x] Feature Freeze technisch/dokumentarisch aktivieren
- [x] automatischen 7/7-GO-Evaluator erstellen
- [x] 8h-Soak-Runner + Preflight erzeugen
- [x] Soak-Preflight: 5,02 s / 414 Operationen / Integrity OK
- [ ] **Gate 01:** vollständiger 8h-Soak
- [ ] **Gate 02:** Chromium echtes App-E2E
- [ ] **Gate 03:** Firefox echtes App-E2E
- [ ] **Gate 04:** Linux physische Mikrofonaufnahme
- [x] **Gate 05:** echter Linux Storage-Failure: ENOSPC + EROFS + App-Recovery
- [ ] **Gate 06:** Android echtes APK + Gerät
- [ ] **Gate 07:** signiertes iOS-App + iPhone X / iOS 16.7.x
- [x] 29/29 Regression-Sanity auf V0.12.1
- [ ] V1.0 RC erst nach 7/7 PASS

### Blocker mit Architekturwirkung
- [x] Historischer Blocker `BUILD_STRUCTURE_ONLY` in V0.12.2 beseitigt: echte Android-Runtime-Quelle vorhanden; APK/Device-Evidence bleibt offen.
- [x] Historischer Blocker `BUILD_CONCEPT_ONLY` in V0.12.2 beseitigt: echtes Xcode-App-Target vorhanden; Build/Signing/Device-Evidence bleibt offen.


## 📱 V0.12.2 – MOBILE RUNTIME COMPLETION · Variante 2
- [x] Feature-Freeze-Ausnahme strikt auf Plattform-Parität begrenzen
- [x] gemeinsame UI in Android/iOS Bundle synchronisieren
- [x] Mobile API Adapter statt localhost-Python-Abhängigkeit
- [x] persistente IndexedDB-Domainruntime
- [x] Memo/Todo/Kalender/Papierkorb/Undo/Redo mobil
- [x] profilgetrennte Mobile-Daten
- [x] Profilwahl und Profilerstellung
- [x] 4-stelliger PIN mit PBKDF2-SHA256 + Salt
- [x] erneute PIN-Abfrage pro App-Session
- [x] fünf Kalenderfarben + Tagesfärbung mobil
- [x] Reminder Scheduling/Cancel Native Bridge
- [x] Android MediaRecorder Bridge
- [x] iOS AVAudioRecorder Bridge
- [x] Android Share Intent + Dateiauswahl
- [x] iOS Activity Share + WKWebView-Dateiauswahl
- [x] mobile Asset-SHA-256 + Quota + TXT/MD Revisionen
- [x] Mobile Diagnose-Privacy
- [x] bis zu vier strukturierte Mobile-Backupgenerationen
- [x] Cross-Runtime-Parity-Test Python ↔ Mobile
- [x] Android Device-Acceptance-Harness für Mikrofon/Reminder/Persistenz
- [x] iPhone Device-Acceptance-Harness für Mikrofon/Reminder/Persistenz
- [x] Android Buildskript
- [x] iOS Xcode-Projekt + Buildskript
- [x] Desktop Regression nach Mobile-Port: 78/78
- [ ] Android SDK Release-APK bauen
- [ ] Gate 06 auf echtem Android-Gerät PASS
- [ ] Xcode Release-App bauen und signieren
- [ ] Gate 07 auf echtem iPhone X / iOS 16.7.16 PASS
- [x] vierfache Binär-Asset-Backupstrategie auf Mobile final abgenommen: 4 Generationen + SHA-256 + Restore
- [ ] übrige Release-Gates 01–04 schließen
- [ ] V1.0 RC ausschließlich nach 7/7 realen Gates + Mobile-Backup-Abnahme

## 🟢 V0.12.2 – Release-Konsolidierung
- [x] Statusregistry auf V0.12.2 synchronisiert
- [x] Versionsregistry auf V0.12.2 synchronisiert
- [x] Mobile Source Acceptance erneut grün
- [x] Cross-Runtime-Parität erneut grün
- [x] vier vollständige Mobile-Backupgenerationen mit Binär-Assets geprüft
- [x] Android Runtime Source ZIP erzeugt
- [x] iOS Xcode Source ZIP erzeugt
- [x] Release-Manifeste aktualisiert
- [x] SHA-256-Artefaktmanifest erzeugt
- [ ] Android APK auf echtem Android-SDK bauen
- [ ] Android-Gerät Acceptance Gate 06
- [ ] iOS .app auf macOS/Xcode bauen und signieren
- [ ] iPhone X / iOS 16.7.16 Acceptance Gate 07
- [ ] Gate 01 echter 8h-Soak
- [ ] Gate 02 Chromium auf uneingeschränktem Runner
- [ ] Gate 03 Firefox
- [ ] Gate 04 physisches Linux-Mikrofon

## 🟢 V0.12.2.1 – Startup-Port-Hotfix
- [x] Portkollision vor Serverstart erkennen
- [x] keine fremden Prozesse automatisch beenden
- [x] freien Ersatzport automatisch wählen
- [x] strikten Portmodus anbieten
- [x] Startup-Evidence schreiben
- [x] API-Version aus kanonischer Versionsregistry lesen
- [x] Collision-Smoke gegen tatsächlich belegten Socket

## 🟢 V0.12.2.2 – Release UI Consistency
- [x] alle sichtbaren Versionsfelder an eine kanonische Quelle binden
- [x] `0.8.0`-Drift entfernen
- [x] Statuskacheln vollständig lesbar machen
- [x] Backupstatus aus realem Zustand ableiten
- [x] Quickbar vertikale Scrollbar verhindern
- [x] Bereichszoom 80–200 % responsiv staffeln
- [x] Sprachmemo-Technikdaten einklappen
- [x] Desktop-Dateiauswahl als Primärworkflow
- [x] manuellen Dateipfad auf Profi-Fallback reduzieren
- [ ] reale Screenshot-Acceptance auf Linux-Zielrechner nach Einspielen des Hotfix

## 🟢 V0.12.2.2 – Entwicklungs-info UI
- [x] Kontrastfarbe in Eingabefeldern
- [x] Größen und Lesbarkeit der linken Schnellnavigation optimiert
- [x] Darstellungseinstellungen oben ins Dashboard verschoben
- [x] Darstellungseinstellungen visuell hervorgehoben
- [x] Theme und Schrift profilpersistent angebunden
- [x] Arbeitsbereich-Zoom 80–200 % mit Layout-Tiers
- [x] horizontales Überlaufen im Arbeitsbereich hart verhindert
- [x] Grid-/Flex-Kinder gegen Randüberlauf gehärtet
- [x] Kalender-/Formular-/Listenansichten für hohe Zoomstufen angepasst
- [x] Android-/iOS-WebAssets auf finalen UI-Stand synchronisiert
- [ ] reale Chromium-/Firefox-Screenshotmatrix auf Zielrechner

## 🟢 V0.12.2.3 – UI Simplification & Input Guidance
- [x] Eingabefelder auf neutrale Nicht-Markenfarbe umgestellt
- [x] sichtbaren Fokuszustand neutral und kontrastreich gestaltet
- [x] optionale Beispiele/Vorgaben für alle benutzbaren Eingabefeld-Kategorien
- [x] Datum-/Zeit-/Select-/Checkbox-Felder mit sichtbaren optionalen Hilfen
- [x] Versionsinformation auf genau eine sichtbare Stelle reduziert
- [x] Statuskacheln von vier auf drei reduziert
- [x] Dashboard von sechs auf vier Hauptkarten reduziert
- [x] Einstellungen auf Hilfemodus vereinfacht
- [x] linke Schnellnavigation ohne horizontale Mini-Scrollbar
- [x] Navigation für große Schriftstufen proportional verbreitert
- [x] Darstellungseinstellungen oben im Dashboard belassen und kompakter hervorgehoben
- [x] Grid/Flex/Listen/Kalender gegen Randüberlauf gehärtet
- [x] Zoom 80–200 % mit Neuordnung statt bloßer Skalierung
- [x] Android-/iOS-WebAssets synchronisiert
- [x] realer All-Views-Visual-Runner erstellt
- [ ] `RUN_VISUAL_ACCEPTANCE_LINUX.sh` auf realem Linux-Zielrechner ausführen

## 🟢 V0.12.2.4 – Release UX + GitHub Control Plane
- [x] Remote-Full-Tree als Backupzustand auditiert
- [x] PR #55 Merge erkannt; V0.12.2.3-Main vor V0.12.2.4 erneut separat gesichert
- [x] Navigation mit stabiler Icon-/Label-Hierarchie
- [x] kontextspezifische Modulhinweise
- [x] Feldhilfen abhängig vom Hilfemodus entdichtet
- [x] Footer-Komplexität reduziert
- [x] Primär-/Sekundär-/Gefahr-Aktionen deutlicher getrennt
- [x] 44px Touch-/Fokusvertrag
- [x] prefers-reduced-motion
- [x] `.gitignore`, `.gitattributes`, `.editorconfig`
- [x] Source-Contract GitHub Actions Workflow
- [x] CONTRIBUTING + LAIENANLEITUNG
- [x] historische 0.5.1-E7-Evidence referenziert
- [ ] reale Visual-Acceptance auf Linux nach V0.12.2.4
- [ ] PR für V0.12.2.4 erst nach lokalem Regression-Gate erzeugen
- [ ] Branch Protection/Required Checks erst nach grünem Workflow aktivieren

## 🟢 GitHub Post-PR55 Safety Correction
- [x] PR #55 Merge auf `a05ea824…` erkannt
- [x] vollständigen V0.12.2.3-main als `backup/pre-v0.12.2.4-20260829` eingefroren
- [x] V0.12.2.4-Review-Branch auf `a05ea824…` ausgerichtet
- [x] V0.12.2.4-Syncvertrag auf neuen Main-SHA korrigiert
- [ ] V0.12.2.4 Review-Branch erst nach lokalem Gate pushen
