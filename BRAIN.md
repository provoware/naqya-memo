# 🧠 BRAIN.md
## Persistentes technisches Erfahrungs- und Fehlerwissen

> Nur belastbare Erkenntnisse speichern. Einträge erhalten Zeit, Kategorie, Ursache, Regel, Regression und Status.

### Schema
`[Zeit] [ID] [Kategorie] [Status]`
- Beobachtung:
- Ursache:
- Lösung:
- Vorbeugeregel:
- Regressionstest:
- Betroffene Komponenten:
- Gültig seit/bis:
- Evidence:

---

[2026-08-28] [BRAIN-0001] [ARCHITEKTUR] [AKTIV]
- Beobachtung: Android, Linux und iOS besitzen stark unterschiedliche Rechte- und Hintergrundmodelle.
- Ursache: Plattformrestriktionen.
- Lösung: Gemeinsamer Kern plus Plattformadapter.
- Vorbeugeregel: Keine plattformspezifische API direkt im Domain-Kern.
- Regressionstest: Import-/Architektur-Layer-Gate.
- Betroffene Komponenten: Plattform, Reminder, Files, Sharing.
- Evidence: V0.1 Architektur.

[2026-08-28] [BRAIN-0002] [DATENSICHERHEIT] [AKTIV]
- Beobachtung: Backup-Erstellung beweist keine Wiederherstellbarkeit.
- Lösung: Jeder Backupmechanismus benötigt Restore-Acceptance.
- Vorbeugeregel: Kein grüner Backupstatus ohne Restore-Test.
- Regressionstest: Backup → Korruption simulieren → Restore → Hashvergleich.
- Evidence: V0.1 Sicherheitsvertrag.

[2026-08-28] [BRAIN-0003] [PRIVACY] [AKTIV]
- Beobachtung: Debugpakete können personenbezogene Inhalte enthalten.
- Lösung: Filter + Vorschau + explizite Versandfreigabe.
- Vorbeugeregel: Default deny für Memo-Inhalt, PIN, Tokens und fremde Pfade.
- Evidence: V0.1 Sicherheitsvertrag.

[2026-08-28] [BRAIN-0004] [PERSISTENZ] [AKTIV]
- Beobachtung: Lose JSON-Dateien würden Konflikt-, Such- und Transaktionslogik unnötig verteilen.
- Lösung: SQLite als kanonischer strukturierter Store; große Assets bleiben Dateien.
- Vorbeugeregel: Kein Modul schreibt strukturierte Produktdaten außerhalb des Repository-Layers.
- Regressionstest: Persistence Contract Suite.
- Evidence: V0.2 ADR-0001.

[2026-08-28] [BRAIN-0005] [KONKURRENZ] [AKTIV]
- Beobachtung: Stilles Überschreiben ist bei parallelen Bearbeitungen gefährlich.
- Lösung: Revision + expected_revision.
- Vorbeugeregel: Bearbeitungs-Use-Cases müssen bekannte Revision mitsenden.
- Regressionstest: REVISION_CONFLICT test.
- Evidence: V0.2 Test Suite.

[2026-08-28] [BRAIN-0006] [BACKUP] [AKTIV]
- Beobachtung: Aktive SQLite-WAL-Dateien dürfen nicht blind kopiert werden.
- Lösung: SQLite Backup API für konsistente Snapshots.
- Vorbeugeregel: Keine naive DB-Dateikopie als grünes Backup.
- Evidence: V0.2 Backup Contract.

[2026-08-28] [BRAIN-0007] [RECOVERY] [AKTIV]
- Beobachtung: Crashs vor COMMIT dürfen keinen Teilzustand hinterlassen.
- Lösung: SQLite-Transaktionen + echte Subprozess-Kill-Acceptance.
- Regressionstest: kill_worker Phasen before_begin/after_begin/after_write_before_commit/after_commit.
- Evidence: V0.3 RECOVERY_ACCEPTANCE_EVIDENCE.

[2026-08-28] [BRAIN-0008] [LOCKING] [AKTIV]
- Beobachtung: Mehrfachinstanzen können denselben Projektordner beschädigen.
- Lösung: exklusiver Projekt-Lock + Single-Writer Queue.
- Regressionstest: second owner rejected.
- Evidence: V0.3.

[2026-08-28] [BRAIN-0009] [FAILURE-INJECTION] [AKTIV]
- Beobachtung: Root-/Container-Umgebungen verfälschen Permission- und Read-only-Tests.
- Lösung: V0.3 prüft deterministische Klassifikation; echte OS-native Injektion wird pro Zielplattform gefahren.
- Vorbeugeregel: keine falsche grüne Plattformbehauptung aus Containerrechten ableiten.

[2026-08-28] [BRAIN-0010] [DOMAIN] [AKTIV]
- Regel: Fachlogik bleibt UI-unabhängig; UI schreibt nie direkt Store.
- Evidence: V0.4 Domain Suite.

[2026-08-28] [BRAIN-0011] [UNDO] [AKTIV]
- Regel: reversible Domainmutation erzeugt persistente Inverse.
- Evidence: V0.4.

[2026-08-28] [BRAIN-0012] [THREADING] [AKTIV]
- Beobachtung: Mutation Queue läuft in Worker-Thread; Standard-SQLite-Connection blockiert Threadwechsel.
- Lösung: Reference-Core Connection mit check_same_thread=False; Single-Writer Queue bleibt alleiniger Mutationspfad.
- Vorbeugeregel: kein paralleler Direktwrite außerhalb Queue.
- Regression: kombinierte V0.2/V0.3/V0.4 Suite.

[2026-08-28] [BRAIN-0012] [PROFILE] [AKTIV]
- Beobachtung: Ein 4-stelliger PIN ist leicht erratbar und darf nicht mit Datenverschlüsselung verwechselt werden.
- Lösung: gesalzener PBKDF2-Hash + klare Produktkennzeichnung „Zugangsbarriere, keine Verschlüsselung“.
- Regressionstest: V0.5 PIN Suite.

[2026-08-28] [BRAIN-0013] [STARTUP] [AKTIV]
- Beobachtung: Betriebssystemname allein beweist keine nutzbare Fähigkeit.
- Lösung: Capability-/Permission-Snapshot pro Start.
- Vorbeugeregel: UI darf Features nur nach Adapterstatus freigeben.

[2026-08-28] [BRAIN-0014] [PORTABILITAET] [AKTIV]
- Beobachtung: sichere Autoreparatur darf keine Rechte umgehen oder externe Pfade still verändern.
- Lösung: Self-Repair nur für kontrollierte lokale Projektstrukturen; alles andere verlangt Nutzeraktion.

[2026-08-28] [BRAIN-0012] [PRESENTATION] [AKTIV]
- Beobachtung: Frühe UI-Service-Kopplung würde Domainlogik duplizieren.
- Lösung: V0.6 Shell bleibt vollständig servicefrei; Schreibbuttons sind wirkungslos/deaktiviert.
- Vorbeugeregel: Presentation importiert keine SQLite-/Domainklassen.
- Regressionstest: `test_no_domain_imports`.
- Evidence: V0.6 Shell Acceptance.

[2026-08-28] [BRAIN-0013] [RESPONSIVE] [AKTIV]
- Beobachtung: Desktop-Sidebars passen nicht sinnvoll auf Smartphones.
- Lösung: Navigation wird Drawer, Kontextpanel wird ausgeblendet/kontextuell nachgelagert.
- Vorbeugeregel: Kernaktionen bleiben ohne horizontalen Seiten-Scroll erreichbar.

[2026-08-28] [BRAIN-0012] [UI-BINDING] [AKTIV]
- Beobachtung: Eine per file:// geöffnete HTML-Shell kann Python-Domainservices nicht sicher erreichen.
- Lösung: lokaler Loopback-Service und Startlauncher.
- Vorbeugeregel: Produktionsnahe UI nie als isolierte HTML-Datei testen, wenn Fachservices benötigt werden.
- Evidence: V0.7 API-E2E.

[2026-08-28] [BRAIN-0013] [SHARING] [AKTIV]
- Beobachtung: Automatischer Mailversand wäre unnötig riskant.
- Lösung: Share-Adapter öffnet Mailclient; Nutzer bestätigt Versand.

[2026-08-28] [BRAIN-0016] [ASSET] [AKTIV]
- Erkenntnis: Große Binärdaten dürfen nicht wie JSON/SQLite-Payload behandelt werden.
- Lösung: Datei-Assets + ID + Manifest + SHA-256.
- Regel: kein finaler Asset-Pfad vor erfolgreichem Temp-/Hash-Schritt.

[2026-08-28] [BRAIN-0017] [QUARANTAENE] [AKTIV]
- Erkenntnis: Beschädigte Assets dürfen den Projektstart nicht blockieren.
- Lösung: erkennen, isolieren, nicht löschen.
- Wirkung: Datenkern bleibt verfügbar.

[2026-08-28] [BRAIN-0018] [QUOTA] [AKTIV]
- Erkenntnis: Audio/PDF kann Backupvolumen unkontrolliert aufblasen.
- Lösung: explizite Asset-Quota und sichtbare Storage-Metrik.

[2026-08-28] [BRAIN-0022] [API-KOMPATIBILITAET] [AKTIV]
- Fehlerbild: Neue Plattform-Probes dürfen bestehende PlatformAdapter-/Factory-Exporte nicht ersetzen.
- Ursache: Paket-__init__ wurde zuerst zu aggressiv überschrieben.
- Reparatur: CapabilityReport, PermissionReport, Adapter und get_platform_adapter erhalten; Probe-API nur ergänzt.
- Regression: vollständige V0.10 Kern-Suite 35/35 PASS.
- Wirkung: Erweiterungen bleiben rückwärtskompatibel.

[2026-08-28] [BRAIN-0023] [AUDIO] [AKTIV]
- Erkenntnis: Erfolgreiche FFmpeg-Signalerzeugung beweist Pipeline, nicht Mikrofonhardware.
- Regel: Aufnahme-Commit-Evidence und Hardware-Capture-Evidence getrennt führen.

[2026-08-28] [BRAIN-0024] [DOKUMENTE] [AKTIV]
- Erkenntnis: Formatunabhängiges Bearbeiten von PDF/DOCX wäre datenriskant.
- Lösung: PDF/DOCX read-only; interner Editor zunächst nur TXT/MD.
- Regel: Formatbewusster Editor vor Schreibfreigabe.

[2026-08-28] [BRAIN-0025] [REVISIONEN] [AKTIV]
- Erkenntnis: Asset-Dateien benötigen eigene Revisionen zusätzlich zum SQLite-Domainjournal.
- Lösung: Snapshot + expected_revision + SHA-256 vor jedem Text-Asset-Edit.

[2026-08-28] [BRAIN-0026] [PACKAGING] [AKTIV]
- Erkenntnis: Buildstruktur ist kein natives Release.
- Regel: Android/iOS erst mit Toolchain- und Device-Evidence auf PASS setzen.

[2026-08-28] [BRAIN-0027] [V0.11-ABSCHLUSS] [AKTIV]
- Befund: Erstes V0.11-Service-E2E deckte fehlende Asset-/Playlist-/Reminder-Initialisierung im Server auf.
- Reparatur: Services explizit nach CoreStore/Queue initialisiert und Linux-Portable neu gebaut.
- Beweis: vollständige Regression 43/43 PASS; Portable frisch entpackt und Health-Endpunkt grün.
- Regel: Service-Abhängigkeiten künftig durch Startup-Smoke in jeder Packaging-Iteration beweisen.

[2026-08-28] [BRAIN-0023] [ASSET-TRANSAKTION] [AKTIV]
- Erkenntnis: Atomarer Datei-Rename allein reicht nicht; Kill zwischen Datei-Commit und Manifest erzeugt sonst Orphans.
- Lösung: Asset-Transaktionsjournal mit Recovery-State-Machine.
- Regression: vier echte Kill-Phasen.

[2026-08-28] [BRAIN-0024] [RELEASE-GATE] [AKTIV]
- Erkenntnis: 89/89 grüne Kern-Tests bedeuten nicht automatisch Produktionsreife.
- Regel: Browser, Mobile, Endurance und Hardware brauchen eigene native Evidence.

[2026-08-28] [BRAIN-0025] [PERFORMANCE] [AKTIV]
- Erkenntnis: 100k-Test bleibt innerhalb der V0.12 Budgets; konkrete Messwerte werden als Evidence gespeichert, nicht als universelles Geräteversprechen.

[2026-08-28] [BRAIN-0023] [RELEASE-GATE] [AKTIV]
- Regel: Nur Evidence-Status PASS darf ein Release-Gate schließen. PRECHECK/BLOCKED/CONTRACT_ONLY zählen nicht.
- Umsetzung: 7/7-GO-Evaluator ist alleinige Freigabequelle.

[2026-08-28] [BRAIN-0024] [STORAGE-NATIVE] [AKTIV]
- Native Linux-Signale erfolgreich bewiesen: /dev/full liefert ENOSPC (28), /sys liefert EROFS (30).
- Zusammen mit der V0.12 Recovery-Matrix ist Storage-Failure Gate 05 geschlossen.

[2026-08-28] [BRAIN-0025] [MOBILE-RELEASE] [AKTIV]
- Kritischer Befund: Android BUILD_STRUCTURE_ONLY und iOS BUILD_CONCEPT_ONLY sind keine testbaren Produkt-Releases.
- Konsequenz: Für ein plattformübergreifendes V1.0 reicht Device-Evidence allein nicht; echte mobile Release-Artefakte sind Voraussetzung.

[2026-08-28] [BRAIN-0028] [MOBILE-RUNTIME] [AKTIV]
- Entscheidung: Variante 2 = Multi-Platform V1.0, keine Linux-only-Abkürzung.
- Lösung: Android/iOS erhalten echte Produktlaufzeitquellen statt Packaging-Platzhalter.
- Regel: Feature-Freeze darf nur für Plattform-Parität geöffnet werden.

[2026-08-28] [BRAIN-0029] [CROSS-RUNTIME-DRIFT] [AKTIV]
- Risiko: Python/SQLite und Mobile/IndexedDB sind zwei Implementierungen desselben Fachvertrags.
- Schutz: `test_cross_runtime_parity.py` ist Pflicht-Gate bei jeder Änderung an gemeinsamem Fachverhalten.
- Wirkung: Revisions-, Memo-, Todo-, Kalender- und Farblogik können nicht unbemerkt auseinanderlaufen.

[2026-08-28] [BRAIN-0030] [MOBILE-PIN] [AKTIV]
- Regel: Ein persistierter "unlocked" Zustand ist unzulässig.
- Umsetzung: PBKDF2-SHA256 + Salt; bei jedem nativen App-Prozess ist eine neue PIN-Prüfung nötig.
- Klarstellung: PIN ist keine Verschlüsselung.

[2026-08-28] [BRAIN-0031] [DEVICE-EVIDENCE] [AKTIV]
- Erkenntnis: Build-Erfolg allein beweist weder Mikrofon noch Reminder noch Lifecycle-Persistenz.
- Lösung: eingebauter `run`/`verify` Device-Acceptance-Modus mit echter Audioaufnahme, Alarm/Notification und Relaunch-Persistenz.
- Release-Regel: Gate 06/07 bleibt BLOCKED ohne physisches Gerät.

[2026-08-28] [BRAIN-0032] [MOBILE-BACKUP] [P0-OFFEN]
- Risiko: vier strukturierte IndexedDB-Backups sind noch keine vier vollständigen Binär-Asset-Kopien.
- Regel: Dieser Unterschied muss vor Multi-Platform V1.0 entweder technisch geschlossen oder im Releasevertrag bewusst neu definiert werden.

[2026-08-28] [BRAIN-0023] [MOBILE-BACKUP] [BEWIESEN]
- Vier vollständige mobile Backupgenerationen einschließlich Binär-Assets.
- SHA-256-Prüfung und Restore im Mobile-Core-Test bewiesen.
- Geräte-Storage-Quota bleibt Teil echter Android/iOS-Acceptance.

[2026-08-28] [BRAIN-0024] [RELEASE-PACKAGING] [AKTIV]
- Source-Paket, nativer Build und Geräte-Evidence sind getrennte Freigabestufen.
- V1.0-Promotion ausschließlich über den 7/7-Release-Evaluator.

[2026-08-28] [BRAIN-0025] [STARTUP-PORT] [BEWIESEN]
- Realer Linux-Start zeigte `Errno 98: Address already in use`.
- Ursache: Launcher startete Server blind auf festem Port 8765.
- Regel: Portprüfung muss VOR Backend-/DB-Initialisierung erfolgen.
- Fremde Prozesse werden niemals automatisch beendet.
- Gleiche gesunde Appinstanz darf wiederverwendet werden; sonst wird ein freier Ersatzport gewählt.
- Die gewählte Entscheidung wird unter `runtime/startup/LAST_START_PORT.json` protokolliert.

[2026-08-28] [BRAIN-0026] [VERSION-SSOT] [BEWIESEN]
- Reale Linux-Screenshots zeigten gleichzeitig 0.8.0, V0.12 und V0.12.2.
- Regel: Keine sichtbare Versionsnummer darf im UI hardcodiert werden.
- Quelle: registry/VERSION.json → server APP_VERSION → /api/state → UI-Bindings.

[2026-08-28] [BRAIN-0027] [STATUS-WAHRHEIT] [BEWIESEN]
- Statisches `Recovery aktiv` ist ohne vorhandene Backupgeneration irreführend.
- Regel: Release-Statuskacheln zeigen nur messbaren Zustand.

[2026-08-28] [BRAIN-0028] [DESKTOP-DATEIWAHL] [BEWIESEN]
- Manueller `/home/...`-Pfad ist kein laiengerechter Primärworkflow.
- Lösung: Browser-Dateiauswahl → gestreamtes Temp-Upload → AssetManager → Hash/Commit.
- Manueller Pfad bleibt ausschließlich als Profi-Fallback erhalten.

[2026-08-28] [BRAIN-0029] [VISUAL-PROPORTIONS] [BEWIESEN]
- Entwicklungs-Evidence aus realen Linux-Screenshots: Navigation, Status- und Zoomflächen müssen bei 100–200 % ihre Containergrenzen respektieren.
- Umsetzung: minmax(0,1fr), min-width:0, overflow-wrap, adaptive Zoom-Tiers und responsive Topbar-Platzierung.
- Regel: Vergrößerung ordnet Module neu; sie darf nicht bloß Inhalt über den Rand skalieren.

[2026-08-28] [BRAIN-0030] [INPUT-CONTRAST] [BEWIESEN]
- Eingabefelder erhalten eine eigenständige warme Kontrastfarbe (#ff9a4a), helle Placeholder und deutlich sichtbaren Fokus.
- Wirkung: Eingabebereiche bleiben gegenüber Neon-Türkis/Lila/Gelb visuell eindeutig.

[2026-08-28] [BRAIN-0031] [DISPLAY-CONTROLS] [BEWIESEN]
- Theme, Schrift und Arbeitsbereich-Zoom sind globale Bedienhilfen und gehören in den dauerhaft sichtbaren Dashboard-Kopf.
- Profilpersistenz wird für Theme und Schrift über SettingsService genutzt; Bereichszoom bleibt lokale Darstellungspräferenz.

[2026-08-28] [BRAIN-0032] [UI-KOMPLEXITAET] [BEWIESEN]
- Wiederholte Versions-, Status- und Darstellungsinformationen erhöhen kognitive Last ohne Mehrwert.
- Regel: dieselbe globale Information nur dort zeigen, wo sie für die Entscheidung gebraucht wird.
- V0.12.2.3: eine sichtbare Version, drei Statuskacheln, vier Dashboardkarten.

[2026-08-28] [BRAIN-0033] [INPUT-GUIDANCE] [BEWIESEN]
- Leere Felder benötigen Beispiele, aber Beispiele dürfen niemals Nutzerdaten vortäuschen.
- Lösung: Placeholder/Hinweise als optionale Vorgaben; keine automatische Übernahme außer ausdrücklich sichtbaren Defaults.
- Datum/Select/Checkbox erhalten Hilfetext, weil native Placeholder dort unzuverlässig oder unmöglich sind.

[2026-08-28] [BRAIN-0034] [INPUT-FARBE] [BEWIESEN]
- Eingabefelder dürfen nicht mit Marken-/Statusfarben konkurrieren.
- V0.12.2.3 verwendet neutrales Silber/Graphit (#b7c1cc / #f4f7fb) und reserviert Türkis/Lila/Gelb für Marke, Orientierung und Status.

[2026-08-28] [BRAIN-0035] [ZOOM-LAYOUT] [AKTIV]
- Bis 200 % darf Vergrößerung nicht durch Überdecken erkauft werden.
- Priorität: Neuordnung → Zusatzinfo ausblenden → Scrollen innerhalb des Inhaltsbereichs; niemals primäre Bedienung überdecken.
