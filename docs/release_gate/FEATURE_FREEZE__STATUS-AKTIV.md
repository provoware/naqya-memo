# V0.12.1 – FEATURE FREEZE

Ab dieser Iteration sind **keine neuen Produktfunktionen** zulässig.

Erlaubt sind ausschließlich:
- Test-/Evidence-Harnesses für die sieben offenen Release-Gates,
- Fehlerkorrekturen, die für ein Release-Gate zwingend notwendig sind,
- Dokumentation, Manifeste, Prüfsummen und Release-Status,
- Anpassungen, die nachweislich eine bestehende Regression reparieren.

Jeder neue Feature-Wunsch wandert unverändert in `UPGRADE_POTENZIAL.md` bzw. die Post-V1.0-Roadmap.

## Automatischer Statuswechsel
`NO-GO -> GO -> V1.0 RC` ist nur erlaubt, wenn **alle sieben** Gate-Evidence-Dateien `PASS` melden, keine Gate-Evidence älter als der aktuelle Abschlusslauf ist und der während des gesamten Abschlusslaufs geprüfte Git-Commit unverändert bleibt.

## Evidence-Freshness-Vertrag
Der offizielle `RUN_RELEASE_GATE_CLOSURE.sh` setzt vor Gate 01 einen UTC-Startzeitpunkt für den gesamten Abschlusslauf. `evaluate_release_gate.py` akzeptiert ein Gate-`PASS` nur, wenn dessen timezone-aware `timestamp`/`timestamp_utc` mindestens diesem Startzeitpunkt entspricht. Fehlender/ungültiger Freshness-Kontext, fehlender/ungültiger Evidence-Zeitstempel oder Evidence aus einem früheren Lauf wird fail-closed als `STALE_EVIDENCE` behandelt und kann keinen `GO`-Status erzeugen.

## Source-Identity-Vertrag
Der offizielle Abschlusslauf ermittelt vor Gate 01 den exakten Git-`HEAD` und exportiert ihn als `PROVOWARE_RELEASE_GATE_SOURCE_SHA`. Vor einem möglichen `GO` liest der Evaluator den aktuellen Repository-`HEAD` erneut. Nur ein exakter 40-stelliger SHA-Gleichstand ist zulässig. Fehlender/ungültiger Start-SHA, nicht lesbarer aktueller SHA oder ein Commit-Wechsel während des Abschlusslaufs erzwingt fail-closed `NO-GO`. Die Closure-Evidence dokumentiert Start- und Auswertungs-SHA sowie den maschinenlesbaren Identitätsgrund.
