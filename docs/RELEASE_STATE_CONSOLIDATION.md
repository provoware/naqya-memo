# NAQYA – Release-State-Konsolidierung

Stand: 2026-10-05

## Ziel

Ein einziger, nachvollziehbarer Release-Zustand ohne widersprüchliche README-, TODO-, Versions- oder Gate-Angaben.

## Kanonische Quellen

1. `registry/VERSION.json` – Produktversion und Feature-Freeze.
2. `registry/PROJECT_STATUS.json` – zusammengefasster Projekt- und Freigabestatus.
3. `registry/evidence/v0.12.2/gates/GATE_*.json` – reale Gate-Evidence.
4. `registry/evidence/v0.12.2/MOBILE_RUNTIME_SOURCE_ACCEPTANCE.json` – Mobile-Runtime-Quellabnahme.

README und TODO sind Darstellungen dieses Zustands, nicht eigenständige Wahrheitsquellen.

## Automatisches Konsistenz-Gate

`python -S tools/release_gate/consolidate_release_state.py`

Die Prüfung schlägt fehl bei:

- Versionsdrift zwischen VERSION und PROJECT_STATUS,
- abweichendem Feature-Freeze,
- abweichenden Gate-Zuständen oder Gate-Zählern,
- unzulässigem GO/V1-RC-Status,
- veralteten aktuellen Verweisen auf PR #100 oder PR #102,
- driftendem kanonischem Release-Block in README/TODO,
- doppelten numerischen UP-Kennungen.

Mit `--write` dürfen ausschließlich bereits vorhandene Gate-Evidence, Gate-Zähler und die verwalteten README/TODO-Blöcke synchronisiert werden.

## Harte Evidence-Grenze

Automatische Tests, Quellcode-Prüfungen, Simulationen, Headless-Läufe und statische Verträge dürfen keines der realen Release-Gates auf PASS setzen.

Aktuell ist ausschließlich Gate 05 real bestanden. Gate 01 ist nur PRECHECK_PASS; Gates 02, 03, 04, 06 und 07 bleiben BLOCKED, bis echte Zielsystem-Evidence vorliegt.

## Effiziente Restreihenfolge bis V1.0 RC

1. Gate 01: vollständiger 8-Stunden-Dauertest.
2. Realer Linux-Lauf: Chromium, Firefox und physisches Mikrofon als gebündelte Abnahmesitzung.
3. Android Release-APK bauen und auf echtem Gerät abnehmen.
4. iOS Release-App mit Xcode bauen/signieren und auf iPhone X / iOS 16.7.16 abnehmen.
5. Erst bei 7/7 PASS den kanonischen Evaluator auf GO wechseln lassen und V1.0 RC erzeugen.

## Repository-Schutz

Der Hauptzweig `main` war bei der Konsolidierung nicht als geschützt gemeldet. Vor V1.0 RC soll GitHub so konfiguriert werden, dass Änderungen an `main` nur über Pull Requests mit erfolgreicher `quality`-Prüfung übernommen werden.

Diese Repository-Einstellung ist kein Produktcode und wird nicht durch Release-Evidence ersetzt.


## Freeze-Status

**FROZEN seit 2026-10-05.**

Ausgangsstand: `main@6064adffc9201181d9b9b847056db2274f1d7a17`.

Bis zum Abschluss der sieben realen Release-Gates werden keine weiteren kosmetischen oder optionalen Repository-/CI-Verbesserungen begonnen. Zulässig bleiben nur reale Gate-Evidence, zwingende Gate-Unterstützung, kritische Gate-Blocker-Korrekturen und daraus notwendige Status-Synchronisation.

Der Freeze endet erst bei **7/7 realen Gates PASS** und Freigabe von V1.0 RC durch den kanonischen Evaluator.
