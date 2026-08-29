# 🧠 **AGENTS.md – Entwicklungs- und Agentenregeln**
## OI - PROVOWARE - IO

### 1. Oberste Regel
Datenerhalt, Reproduzierbarkeit und klare Nutzerführung sind wichtiger als Feature-Geschwindigkeit.

### 2. Patch-Disziplin
Vor jedem nichttrivialen Patch:
1. Ziel
2. exakte betroffene Dateien/Codepositionen
3. Grund
4. erwartete Wirkung
5. Risiko
6. benötigte Tests
7. Rollbackweg

Erst danach patchen. Kleine, lokal begrenzte Änderungen bevorzugen.

### 3. Jede Mutation erhält einen Contract
`PRE → ACTION → POST → EVIDENCE → COMMIT`
Bei Fehler:
`FAIL → ROLLBACK/RECOVERY → VERIFY → REPORT`

### 4. Agentenbereiche
- **ARCHITEKTUR** – Modulgrenzen, ADRs, Kopplung
- **DATENSICHERHEIT** – Persistence, Backup, Restore, Kill-Tests
- **PLATTFORM** – Android/Linux/iOS Adapter
- **UX_A11Y** – Laienführung, Responsive, Kontrast, Touch, Screenreader
- **QA_REGRESSION** – Tests, Evidence, Regression Registry
- **DOCS_RELEASE** – README, TODO, CHANGELOG, Status, Manifeste, Releases
- **SELFREPAIR_DIAGNOSE** – BRAIN, Fehlerklassen, Reparaturregeln
- **PERFORMANCE** – Budgets, Stress, Speicher, Startzeit

### 5. Triggerpunkte für Unteragenten
Unteragent wird aktiv bei:
- Änderung an Persistenz/Backup → DATENSICHERHEIT
- Plattform-API/Berechtigung → PLATTFORM
- Layout/Bedienlogik → UX_A11Y
- Fix eines echten Fehlers → QA_REGRESSION + BRAIN
- Release/Version → DOCS_RELEASE
- Startfehler/Recovery → SELFREPAIR_DIAGNOSE
- große Datenmenge/Timing → PERFORMANCE

### 6. Dokumentationspflicht
Bei relevanter Änderung mindestens aktualisieren:
`CHANGELOG.md`, `TODO.md`, `README.md`, `registry/PROJECT_STATUS.json`.
Bei Erkenntnis/Fehler zusätzlich `BRAIN.md`.
Bei neuer Idee `UPGRADE_POTENZIAL.md`.

### 7. Kein Status ohne Evidence
Statusfolge:
`ENTWURF → IMPLEMENTIERT → GEPRÜFT → BEWIESEN → FREIGEGEBEN`

### 8. Keine riskanten Automatismen
Keine externe Datei löschen, überschreiben, versenden, ausführen oder verändern, ohne klare Berechtigung und geeigneten Schutzpfad.

### 9. Codekommentare
Kommentare erklären **warum**, Schutzbedingungen, Datenverträge und ungewöhnliche Randfälle. Keine Kommentarflut für offensichtlichen Code.

### 10. Abschluss jeder Iteration
Ausgeben und in Statusdateien pflegen:
Toolname · Projekt · Version · Volumen · Besonderheiten · Fortschritt % · erledigt/offen · Tests · Risiken · nächster Schritt · übernächster Schritt.

## 11. V0.12 Release-Candidate-Regel
Ab V0.12 gilt Feature-Freeze für große neue Funktionen. Änderungen dürfen nur Release-Gates schließen, Fehler beheben, Robustheit/Accessibility/Portabilität verbessern oder Evidence erzeugen. `V1.0 RC` darf nur gesetzt werden, wenn `registry/evidence/v0.12/GO_NO_GO.json` den Zustand `GO` trägt.


## 🔒 V0.12.1 RELEASE-GATE FEATURE FREEZE
- Keine neuen Features bis V1.0-RC-GO.
- Änderungen nur zur Gate-Schließung, Regression-Reparatur, Evidence oder Release-Dokumentation.
- `GO` nur aus `tools/release_gate/evaluate_release_gate.py`, wenn 7/7 Evidence = PASS.
- BLOCKED, PRECHECK_PASS und CONTRACT_ONLY sind **kein PASS**.

## 🔒 V0.12.2 – FEATURE-FREEZE-AUSNAHME: MOBILE PARITY ONLY

Bis V1.0 RC gilt weiterhin Feature Freeze. Einzige Ausnahme ist die vom Projekt ausdrücklich gewählte **Variante 2: vollständige Android-/iOS-Plattformparität**.

### Erlaubte Änderungen
- bestehende Fachverträge auf Android/iOS portieren,
- Native Bridges, Permissions, Reminder, Mikrofon, Share, Dateiauswahl,
- Android-/Xcode-Buildstruktur,
- Device-Acceptance und Cross-Runtime-Parity-Tests,
- reine Release-/Recovery-Korrekturen.

### Verbotene Änderungen
- neue Fachfunktionen,
- neue Produktmodule,
- kosmetisches Redesign ohne Release-Blocker,
- Lockerung bestehender Daten-/Recovery-Gates.

### Pflicht-Gates bei Mobile-Code
1. `RUN_MOBILE_RUNTIME_ACCEPTANCE.sh`
2. `tests/mobile/test_cross_runtime_parity.py`
3. Desktop-Regressions-Sanity
4. Release-Evaluator bleibt NO-GO, solange Android/iOS keine echte Device-Evidence besitzen.

### Native PASS-Regel
`RUNTIME_SOURCE_COMPLETE`, `Swift parse`, `Kotlin compile` oder `BUILD READY` sind **kein** Device-PASS. Gate 06/07 dürfen ausschließlich mit realem gebauten Artefakt und physischem Gerät `PASS` werden.

## V0.12.2 RELEASE CONSOLIDATION RULE
- Feature-Freeze bleibt aktiv.
- Source-Acceptance darf native Build-/Device-Evidence niemals ersetzen.
- `evaluate_release_gate.py` ist die alleinige GO/NO-GO-Quelle.
- Bis V1.0 RC nur Fehlerbehebung, Plattformparität, Evidence und Packaging.

## RELEASE UI VISUAL CONTRACT
- Globale Darstellungseinstellungen gehören in den dauerhaft sichtbaren Dashboard-Kopf.
- Keine sichtbare Version darf hardcodiert werden.
- Eingabefelder müssen sich durch eine separate Kontrastfarbe vom Hintergrund unterscheiden.
- Bei Schrift-/Bereichszoom bis 200 % müssen Grid-/Flex-Kinder `min-width:0` respektieren und sich neu anordnen.
- Kein UI-Element darf einen anderen primären Bedienknopf überdecken.
- Browser-Screenshot-Evidence ist ein separates reales Gate und darf durch CSS-/Stringtests nicht ersetzt werden.

## UI SIMPLIFICATION CONTRACT
- Versionsinformation ist genau einmal sichtbar; kanonische Quelle bleibt `registry/VERSION.json`.
- Benutzbare Eingabefelder besitzen hilfreiche, optionale Beispiele oder Vorgaben.
- Placeholder/Hinweise dürfen keine Daten automatisch speichern.
- Eingabefeldfarbe darf nicht mit den primären Markenfarben Türkis/Lila/Gelb identisch sein.
- Bei 80–200 % Zoom muss Layout neu ordnen, bevor horizontaler Überlauf akzeptiert wird.
- Linke Navigation darf keine horizontale Scrollleiste benötigen.
- Redundante UI-Information wird entfernt statt an eine andere Stelle verschoben.

## REAL VIEWPORT CONTRACT
- Jede relevante UI-Härtung muss mindestens 1366×768, 1600×900, 1920×1080, 150 %, 200 % und Mobile berücksichtigen.
- Navigation darf Labels nicht buchstabenweise umbrechen oder abschneiden; bei Platzmangel einklappen.
- 200 % ist als eigener High-Magnification-Modus zu behandeln.
- Zusatzinfo und technische Details dürfen den primären Arbeitsbereich nicht dauerhaft überdecken.
- Offline-Geometrie-Screenshots sind Evidence für Layout, aber kein Ersatz für echtes Loopback-/Browser-E2E.
- Nach Änderungen an Navigation/Drawer/Layout immer Theme-, Schrift- und Zoombedienung regressionsprüfen.
