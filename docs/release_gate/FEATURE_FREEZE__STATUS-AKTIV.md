# V0.12.1 – FEATURE FREEZE

Ab dieser Iteration sind **keine neuen Produktfunktionen** zulässig.

Erlaubt sind ausschließlich:
- Test-/Evidence-Harnesses für die sieben offenen Release-Gates,
- Fehlerkorrekturen, die für ein Release-Gate zwingend notwendig sind,
- Dokumentation, Manifeste, Prüfsummen und Release-Status,
- Anpassungen, die nachweislich eine bestehende Regression reparieren.

Jeder neue Feature-Wunsch wandert unverändert in `UPGRADE_POTENZIAL.md` bzw. die Post-V1.0-Roadmap.

## Automatischer Statuswechsel
`NO-GO -> GO -> V1.0 RC` ist nur erlaubt, wenn **alle sieben** Gate-Evidence-Dateien `PASS` melden, keine Gate-Evidence älter als der aktuelle Abschlusslauf ist, der Abschlusslauf aus einem sauberen Git-Arbeitsbaum gestartet wurde und sowohl Git-Commit als auch Git-Source-Tree während des gesamten Abschlusslaufs unverändert bleiben.

## Evidence-Freshness-Vertrag
Der offizielle `RUN_RELEASE_GATE_CLOSURE.sh` setzt vor Gate 01 einen UTC-Startzeitpunkt für den gesamten Abschlusslauf. `evaluate_release_gate.py` akzeptiert ein Gate-`PASS` nur, wenn dessen timezone-aware `timestamp`/`timestamp_utc` mindestens diesem Startzeitpunkt entspricht. Fehlender/ungültiger Freshness-Kontext, fehlender/ungültiger Evidence-Zeitstempel oder Evidence aus einem früheren Lauf wird fail-closed als `STALE_EVIDENCE` behandelt und kann keinen `GO`-Status erzeugen.

## Source-Identity-Vertrag
Der offizielle Abschlusslauf ermittelt vor Gate 01 den exakten Git-`HEAD` und exportiert ihn als `PROVOWARE_RELEASE_GATE_SOURCE_SHA`. Vor einem möglichen `GO` liest der Evaluator den aktuellen Repository-`HEAD` erneut. Nur ein gültiger 40-stelliger hexadezimaler SHA-Gleichstand ist zulässig. Fehlender/ungültiger Start-SHA, nicht lesbarer aktueller SHA oder ein Commit-Wechsel während des Abschlusslaufs erzwingt fail-closed `NO-GO`. Die Closure-Evidence dokumentiert Start- und Auswertungs-SHA sowie den maschinenlesbaren Identitätsgrund.

## Clean-Worktree-Vertrag
Vor Gate 01 muss `require_clean_worktree.py` den Repository-Arbeitsbaum mit `git status --porcelain=v1 --untracked-files=all` als leer bestätigen. Geänderte tracked Dateien, staged Änderungen und nicht ignorierte untracked Dateien blockieren den Abschlusslauf fail-closed, bevor reale Gate-Evidence erzeugt wird. Bewusst ignorierte Laufzeit-/Scratch-Dateien gelten nicht als Release-Quelländerung. Damit kann ein unveränderter `HEAD` nicht mehr lokale, noch nicht commitete Release-Quellen verdecken.

## Source-Tree-Identity-Vertrag
Nach bestandenem Clean-Worktree-Preflight ermittelt der offizielle Abschlusslauf zusätzlich den nativen Git-Tree-Objekt-Hash von `HEAD^{tree}` und exportiert ihn als `PROVOWARE_RELEASE_GATE_SOURCE_TREE_SHA`. Der Evaluator berechnet vor einem möglichen `GO` den aktuellen `HEAD^{tree}` erneut. Nur ein identischer gültiger 40-stelliger hexadezimaler Tree-SHA erlaubt die Freigabe. Fehlender/ungültiger Tree-Kontext, nicht lesbarer aktueller Tree oder ein Tree-Wechsel erzwingen fail-closed `NO-GO`. Die Closure-Evidence speichert Start- und Auswertungs-Tree-SHA sowie den maschinenlesbaren Grund. Der Git-Tree-Hash bindet Pfade, Dateimodi und Blob-Inhalte der getrackten Quellen rekursiv an den geprüften Release-Stand; Build-Artefakt-Hashes und signierte Provenance bleiben separate spätere Release-Härtungen.
