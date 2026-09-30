# Mitentwickeln – OI / PROVOWARE / IO

## Grundregel

Der aktuelle Stand befindet sich im Release-Freeze. Änderungen sind nur zulässig, wenn sie
Bugfix, Plattform-Parität, Evidence, Packaging, Accessibility, UX-Härtung oder Repository-
Sicherheit betreffen.

## Vor jeder Änderung

1. `registry/VERSION.json` und `registry/PROJECT_STATUS.json` lesen.
2. Keine realen Release-Gates ohne reale Hardware-/Browser-Evidence auf PASS setzen.
3. Kritische Datenänderungen müssen Recovery/Undo/Validierung respektieren.
4. Keine Secrets, Tokens, Schlüssel oder lokale Laufzeitdaten committen.

## Mindestprüfungen

```bash
python3 -S tests/ui_consistency/test_v01222_static_ui_consistency.py
python3 -S tests/ui_consistency/test_v01223_simplification_guidance.py
python3 -S tests/ui_consistency/test_v01224_ux_control_plane.py
PYTHONPATH=core/reference_python python3 -S tests/startup/test_startup_port_guard.py
PYTHONPATH=core/reference_python python3 -S tests/mobile/test_mobile_sources.py
```

## Merge-Regel

Ein großer Architekturwechsel wird nicht direkt auf `main` geschrieben. Erst:
Backup-Branch → Review-Branch → automatisierte Checks → Evidence → kontrollierter Merge.

`NO-GO / 1 von 7` bleibt bestehen, solange die realen Release-Gates nicht tatsächlich
auf Zielsystemen bestanden wurden.
