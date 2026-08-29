# V0.12.1 – FEATURE FREEZE

Ab dieser Iteration sind **keine neuen Produktfunktionen** zulässig.

Erlaubt sind ausschließlich:
- Test-/Evidence-Harnesses für die sieben offenen Release-Gates,
- Fehlerkorrekturen, die für ein Release-Gate zwingend notwendig sind,
- Dokumentation, Manifeste, Prüfsummen und Release-Status,
- Anpassungen, die nachweislich eine bestehende Regression reparieren.

Jeder neue Feature-Wunsch wandert unverändert in `UPGRADE_POTENZIAL.md` bzw. die Post-V1.0-Roadmap.

## Automatischer Statuswechsel
`NO-GO -> GO -> V1.0 RC` ist nur erlaubt, wenn **alle sieben** Gate-Evidence-Dateien `PASS` melden und keine Gate-Evidence älter als der aktuelle Build ist.
