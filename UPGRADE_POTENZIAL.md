# 🚀 **UPGRADE_POTENZIAL.md**
## Erweiterungs-, Verbesserungs- und Robustheitspool

| ID | Priorität | Vorschlag | Grund | Wirkung | Status |
|---|---|---|---|---|---|
| UP-001 | P1 | Portables Export-/Import-Bundle mit Manifest | Umzüge zwischen Geräten | hohe Datenportabilität | OFFEN |
| UP-002 | P1 | Konfliktfreier Merge für importierte Daten | doppelte/abweichende IDs | weniger Datenverlust | OFFEN |
| UP-003 | P1 | Profilexport mit optionaler Verschlüsselung | spätere Privatsphäre | sichere Portabilität | PARKEN |
| UP-004 | P1 | Reminder-Health-Check | mobile OS drosseln Hintergrundjobs | höhere Termintreue | OFFEN |
| UP-005 | P2 | „Warum ist das gesperrt?“-Erklärdialog | Laienführung | weniger Fehlbedienung | OFFEN |
| UP-006 | P2 | Recovery-Simulator im Entwicklerbereich | Restore üben ohne Echtdaten | höhere Robustheit | OFFEN |
| UP-007 | P2 | Inhaltsbeziehungen als Graph | Memo↔Todo↔Termin↔Dokument | bessere Organisation | OFFEN |
| UP-008 | P2 | intelligente Duplikaterkennung | doppelte Import-/Memosätze | Datenhygiene | OFFEN |
| UP-009 | P2 | adaptive Informationsdichte | kleine/ große Displays | weniger Scrollen | OFFEN |
| UP-010 | P2 | Diagnosepaket mit Ein-Klick-Selbsttest | Support | schnellere Fehleranalyse | OFFEN |
| UP-011 | P3 | optionaler lokaler Volltextindex | große Datenmengen | schnellere Suche | OFFEN |
| UP-012 | P3 | Offline-Spracherkennung als Plugin | Sprachmemo→Text | Komfort | PARKEN |
| UP-013 | P3 | austauschbare Plugin-Sandbox | Erweiterbarkeit | Schutz des Kerns | OFFEN |
| UP-014 | P3 | Barrierefreiheits-Selbsttest im Tool | wechselnde Themes/Zoom | kontinuierliche A11y | OFFEN |
| UP-015 | P3 | Recovery-Erfolgstatistik | reale Nutzungsqualität | messbarer Self-Repair | OFFEN |

| UP-016 | P1 | SQLite Online Backup während aktiver Session periodisch prüfen | WAL/Crash-Sicherheit | robustere Checkpoints | OFFEN |
| UP-017 | P1 | Content-addressed Asset Store optional | doppelte Audio/PDF-Anhänge | weniger Speicherbedarf | PRÜFEN |
| UP-018 | P2 | inkrementelle Backup-Strategie nach Baseline | große Projekte | weniger Backup-I/O | PRÜFEN |
| UP-019 | P2 | revisionsbasierter Diff-Viewer für Textmemos | Undo/Recovery | verständliche Wiederherstellung | OFFEN |

| UP-020 | P1 | persistentes Command-Journal mit inversen Domainbefehlen | Crash-sicheres Undo | robuste Nutzerkorrektur | V0.4 |
| UP-021 | P1 | plattformnative Failure-Runner | reale OS-Evidence | belastbare Freigabe | OFFEN |
| UP-022 | P2 | Lock-Owner-Diagnose im Tool | blockierte Projekte verständlich machen | bessere Laienführung | OFFEN |
| UP-023 | P2 | Recovery-Dry-Run vor Restore | Risiko transparent machen | sicherere Wiederherstellung | OFFEN |

| UP-024 | P1 | Wiederkehrende Termine | Kalenderausbau | weniger Sonderlogik | OFFEN |
| UP-025 | P1 | Todo-Serien/Teilaufgaben | Workflow | bessere Organisation | OFFEN |
| UP-026 | P2 | Memo↔Todo↔Termin-Verknüpfung | Kontext | weniger Suchaufwand | OFFEN |

| UP-028 | P1 | PIN-Bruteforce-Cooldown optional konfigurierbar | lokale Zugangshürde | weniger triviale Versuche | PRÜFEN |
| UP-029 | P1 | native Reminder-Health-Checks pro Plattform | zuverlässige Erinnerungen | höhere Termintreue | V0.7+ |
| UP-030 | P2 | Capability-Diff zwischen Starts | geänderte Rechte/Geräte erkennen | bessere Selbstdiagnose | OFFEN |
| UP-031 | P2 | Projektordner-Umzug mit Dry-Run | Portabilität | weniger Pfadfehler | OFFEN |
| UP-032 | P2 | Settings-Import/Export mit Schema | Gerätewechsel | komfortable Übernahme | OFFEN |

| UP-028 | P1 | visuelle Regression mit Pixel-/Layout-Toleranzen | UI-Drift | stabilere Releases | V0.7+ |
| UP-029 | P1 | echte Screenreader-Acceptance auf Zielplattformen | A11y | belastbare Freigabe | OFFEN |
| UP-030 | P2 | adaptive Informationsdichte je Displayklasse | weniger Überladung | bessere Nutzbarkeit | OFFEN |
| UP-031 | P2 | Tooltip-Popover mit Kollisionsvermeidung | Hilfe verdeckt keine Controls | bessere Laienführung | OFFEN |

| UP-028 | P1 | echter Browser-E2E Runner Firefox/Chromium | UI-Regressionsschutz | hohe Sicherheit | V0.8 |
| UP-029 | P1 | Edit-Dialoge für Memo/Todo/Termin | vollständiges CRUD | hoher Nutzwert | V0.8 |
| UP-030 | P1 | interaktive Monatskalender-Tagesfärbung | Kernanforderung | direkter Kalenderworkflow | V0.8 |
| UP-031 | P2 | Diagnosepaket mit Privacy-Vorschau vor Share | Support/Datenschutz | sicherere Hilfe | V0.8 |

| UP-032 | P1 | Audio-Geräteauswahl per FFmpeg/PipeWire-Discovery | reales Mikrofon auswählen | weniger Startfehler | V0.12/1.0 |
| UP-033 | P1 | PDF Annotation als separate Sidecar-Datei | PDF nicht destruktiv ändern | sichere Bearbeitung | OFFEN |
| UP-034 | P2 | DOCX formatbewusster Editor-Adapter | Office-Dokumente | verhindert Dateikorruption | PRÜFEN |
| UP-035 | P1 | Android/iOS native CI Runner | Packaging-Evidence | echte Mobile-Freigabe | OFFEN |

| UP-032 | P0 | automatisierter 8h-Nightly-Soak | echte Endurance-Evidence | verhindert schleichende Leaks/Races | OFFEN |
| UP-033 | P0 | Self-hosted Firefox/Chromium UI Runner | Visual/A11y Release-Gate | reproduzierbare Browser-Evidence | OFFEN |
| UP-034 | P0 | Android/iOS Device Farm | native Permission/Reminder/Mic Evidence | schließt Mobile-Gate | OFFEN |
| UP-035 | P1 | Loop-/Mounted-Volume Failure Runner | echte ENOSPC/Read-only Tests | stärkt Storage-Recovery | OFFEN |

| UP-032 | Post-V1 | Device-Farm-Runner Android+iOS | reproduzierbare native Evidence | Release-Automatisierung | FEATURE-FREEZE: PARKEN |
| UP-033 | Post-V1 | Browser-Matrix als CI-Runner | Chromium/Firefox reproduzierbar | A11y/Responsive Sicherheit | FEATURE-FREEZE: PARKEN |
| UP-040 | P0 | gemeinsame maschinenlesbare Domain-Contracts für Python + Mobile-Codegen | verhindert Doppelimplementierungsdrift | höhere Cross-Platform-Sicherheit | OFFEN |
| UP-041 | P0 | native inkrementelle Binär-Asset-Backupgenerationen Android/iOS | schließt Mobile-Recovery-Paritätslücke | V1.0 Datensicherheit | OFFEN |
| UP-042 | P1 | optional verschlüsselter Mobile Vault über Android Keystore / iOS Keychain | echte Vertraulichkeit zusätzlich zum PIN | Datenschutz | SPÄTER |
| UP-043 | P1 | automatischer Android Emulator Gate zusätzlich zum physischen Device Gate | schnellere Regression | physisches Gate bleibt Pflicht | OFFEN |
| UP-044 | P1 | iOS Simulator Contract Gate zusätzlich zum echten iPhone-X-Gate | schnellere Xcode-Regression | Device Gate bleibt Pflicht | OFFEN |

## UP-UI-VISUAL-REAL-GATE – 🟠 HOCH
- **Offen:** V0.12.2.2 auf realem Chromium/Firefox mit 1366×768, 1600×900, 1920×1080 und Mobile-Viewport fotografisch/DOM-basiert abnehmen.
- **Grund:** Build-Runner kann Headless-Chromium aktuell nicht zuverlässig abschließen.
- **Wirkung:** schließt die letzte Lücke zwischen statischem Layoutvertrag und tatsächlich gerendertem Zielsystem.

## UP-UI-REAL-VISUAL-V01223 – 🟠 HOCH
- **Offen:** `RUN_VISUAL_ACCEPTANCE_LINUX.sh` auf dem realen Linux-Rechner ausführen.
- **Umfang:** Dashboard, Memo, Todo, Kalender, Papierkorb, Diagnose, Sprachmemo, Dokument/PDF, Audio, Einstellungen bei Desktop 100/150/200 %, kompakt und Mobile.
- **Nutzen:** beweist tatsächliche Nicht-Überdeckung und Randtreue; statische CSS-Verträge allein reichen dafür nicht.
