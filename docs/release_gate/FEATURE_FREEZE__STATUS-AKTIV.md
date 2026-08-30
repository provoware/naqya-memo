# V0.12.1 – FEATURE FREEZE

Ab dieser Iteration sind **keine neuen Produktfunktionen** zulässig.

Erlaubt sind ausschließlich:
- Test-/Evidence-Harnesses für die sieben offenen Release-Gates,
- Fehlerkorrekturen, die für ein Release-Gate zwingend notwendig sind,
- Dokumentation, Manifeste, Prüfsummen und Release-Status,
- Anpassungen, die nachweislich eine bestehende Regression reparieren.

Jeder neue Feature-Wunsch wandert unverändert in `UPGRADE_POTENZIAL.md` bzw. die Post-V1.0-Roadmap.

## Automatischer Statuswechsel
`NO-GO -> GO -> V1.0 RC` ist nur erlaubt, wenn **alle sieben kanonisch benannten Gate-Evidence-Dateien** `PASS` melden, pro Gate-Nummer keine konkurrierende JSON-Evidence existiert, keine Gate-Evidence älter als der aktuelle Abschlusslauf ist, der Abschlusslauf aus einem sauberen Git-Arbeitsbaum gestartet wurde, Git-Commit, Git-Source-Tree und mobiles Release-Manifest während des gesamten Abschlusslaufs unverändert bleiben, die im mobilen Release-Manifest deklarierten Source-Artefakte byte- und SHA-256-genau verifiziert sind und die resultierende Closure-Evidence einen gültigen deterministischen Provenance-Record über Commit, Source-Tree, Manifest und beide Pflichtartefakte enthält.

## Canonical-Evidence-Binding-Vertrag
Jedes reale Release-Gate ist genau an seinen kanonischen Dateinamen gebunden: `GATE_01_8H_SOAK.json`, `GATE_02_CHROMIUM.json`, `GATE_03_FIREFOX.json`, `GATE_04_LINUX_MICROPHONE.json`, `GATE_05_STORAGE_FAILURE.json`, `GATE_06_ANDROID_DEVICE.json` und `GATE_07_IOS_IPHONE_X.json`. `evaluate_release_gate.py` darf keine wildcard-basierte Ersatzdatei als Gate-Evidence auswählen. Fehlt die kanonische Datei, wird das Gate als `INVALID_EVIDENCE_BINDING` mit `CANONICAL_GATE_EVIDENCE_MISSING` behandelt. Existiert zusätzlich eine weitere `GATE_<Nr>_*.json`, wird die Gate-Nummer wegen Mehrdeutigkeit mit `AMBIGUOUS_GATE_EVIDENCE_FILES` fail-closed blockiert. Damit kann weder eine falsch benannte noch eine lexikographisch spätere Zusatzdatei die für das Release festgelegte Evidence überschatten.

## Evidence-Freshness-Vertrag
Der offizielle `RUN_RELEASE_GATE_CLOSURE.sh` setzt vor Gate 01 einen UTC-Startzeitpunkt für den gesamten Abschlusslauf. `evaluate_release_gate.py` akzeptiert ein Gate-`PASS` nur, wenn dessen timezone-aware `timestamp`/`timestamp_utc` mindestens diesem Startzeitpunkt entspricht. Fehlender/ungültiger Freshness-Kontext, fehlender/ungültiger Evidence-Zeitstempel oder Evidence aus einem früheren Lauf wird fail-closed als `STALE_EVIDENCE` behandelt und kann keinen `GO`-Status erzeugen.

## Source-Identity-Vertrag
Der offizielle Abschlusslauf ermittelt vor Gate 01 den exakten Git-`HEAD` und exportiert ihn als `PROVOWARE_RELEASE_GATE_SOURCE_SHA`. Vor einem möglichen `GO` liest der Evaluator den aktuellen Repository-`HEAD` erneut. Nur ein gültiger 40-stelliger hexadezimaler SHA-Gleichstand ist zulässig. Fehlender/ungültiger Start-SHA, nicht lesbarer aktueller SHA oder ein Commit-Wechsel während des Abschlusslaufs erzwingt fail-closed `NO-GO`. Die Closure-Evidence dokumentiert Start- und Auswertungs-SHA sowie den maschinenlesbaren Identitätsgrund.

## Clean-Worktree-Vertrag
Vor Gate 01 muss `require_clean_worktree.py` den Repository-Arbeitsbaum mit `git status --porcelain=v1 --untracked-files=all` als leer bestätigen. Geänderte tracked Dateien, staged Änderungen und nicht ignorierte untracked Dateien blockieren den Abschlusslauf fail-closed, bevor reale Gate-Evidence erzeugt wird. Bewusst ignorierte Laufzeit-/Scratch-Dateien gelten nicht als Release-Quelländerung. Damit kann ein unveränderter `HEAD` nicht mehr lokale, noch nicht commitete Release-Quellen verdecken.

## Source-Tree-Identity-Vertrag
Nach bestandenem Clean-Worktree-Preflight ermittelt der offizielle Abschlusslauf zusätzlich den nativen Git-Tree-Objekt-Hash von `HEAD^{tree}` und exportiert ihn als `PROVOWARE_RELEASE_GATE_SOURCE_TREE_SHA`. Der Evaluator berechnet vor einem möglichen `GO` den aktuellen `HEAD^{tree}` erneut. Nur ein identischer gültiger 40-stelliger hexadezimaler Tree-SHA erlaubt die Freigabe. Fehlender/ungültiger Tree-Kontext, nicht lesbarer aktueller Tree oder ein Tree-Wechsel erzwingen fail-closed `NO-GO`. Die Closure-Evidence speichert Start- und Auswertungs-Tree-SHA sowie den maschinenlesbaren Grund. Der Git-Tree-Hash bindet Pfade, Dateimodi und Blob-Inhalte der getrackten Quellen rekursiv an den geprüften Release-Stand.

## Release-Manifest-Identity-Vertrag
Nach bestandenem Clean-Worktree-Preflight und vor Gate 01 ermittelt der offizielle Abschlusslauf zusätzlich den SHA-256 von `docs/release/MOBILE_RUNTIME_RELEASE_MANIFEST.json` und exportiert ihn als `PROVOWARE_RELEASE_GATE_MANIFEST_SHA256`. Symlink oder fehlendes Manifest blockieren den Start fail-closed. Vor einem möglichen `GO` wird der Manifest-SHA-256 erneut berechnet. Fehlender/ungültiger Start-Hash, nicht lesbarer aktueller Manifestzustand oder eine Änderung während des Abschlusslaufs erzwingen `NO-GO`. Die Closure-Evidence speichert Start- und Auswertungs-Hash sowie den maschinenlesbaren Identitätsgrund. Damit kann auch eine nach dem Start entstandene uncommitted Manifeständerung nicht mit bereits laufender Gate-Evidence releasewirksam werden.

## Release-Artefakt-Integritätsvertrag
Vor einem möglichen `GO` liest `evaluate_release_gate.py` die bereits in `docs/release/MOBILE_RUNTIME_RELEASE_MANIFEST.json` deklarierten Android- und iOS-Source-Artefakte. Akzeptiert werden ausschließlich lokale reguläre Dateien im festgelegten `dist/v0.12.2`-Ordner mit sicherem Basename. Für jedes Artefakt müssen die tatsächliche Bytezahl und der tatsächliche SHA-256 exakt den committed Manifestwerten entsprechen. Fehlendes/ungültiges Manifest, unsicherer Pfad, Symlink, fehlende/unlesbare Datei, Größenabweichung oder SHA-256-Abweichung blockieren `GO` fail-closed. Der Vertrag erzeugt keine neuen APK-/IPA-Artefakte und behauptet keine native Gerätefreigabe; er bindet ausschließlich die bereits definierten mobilen Runtime-Source-ZIPs an den Release-Entscheid.

## Release-Closure-Provenance-Vertrag
Nach der normalen Release-Gate-Auswertung erzeugt `attest_release_closure.py` aus genau vier bereits geprüften Identitätsklassen einen kanonisch serialisierten Provenance-Payload: Git-Commit-SHA, Git-Source-Tree-SHA, SHA-256 des mobilen Release-Manifests sowie tatsächlicher SHA-256 und Bytezahl der Pflichtartefakte `android` und `ios`. Die Serialisierung verwendet feste Feldnamen, feste Plattformreihenfolge und sortierte JSON-Schlüssel; daraus wird ein SHA-256 als kompakter `release_provenance.sha256` in `RELEASE_GATE_CLOSURE.json` geschrieben. Fehlende oder formal ungültige Source-/Tree-/Manifest-Identität, fehlende Pflichtartefakte, doppelte/unerwartete Plattformen, ungültige Hashes/Größen oder ein Artefaktstatus ungleich `PASS` erzeugen fail-closed `release_provenance.status=FAIL`. Der offizielle Abschlusslauf wertet sowohl den normalen Evaluator als auch die Provenance-Attestierung aus und kann nur bei beiden Exitcode 0 erfolgreich enden. Dieser Record ist ein deterministischer Integritätsfingerabdruck, aber bewusst noch keine digitale Signatur und kein Nachweis eines vertrauenswürdigen externen Erzeugers.

## Release-Closure-Provenance-Verifikationsvertrag
`verify_release_closure_provenance.py` prüft eine bereits persistierte `RELEASE_GATE_CLOSURE.json` ausschließlich lesend. Der Prüfer rekonstruiert den erwarteten `provoware.release-provenance.v1`-Payload erneut aus den autoritativen Closure-Feldern für Commit, Source-Tree, Manifest und Android-/iOS-Artefakte, vergleicht ihn vollständig mit dem gespeicherten Payload und berechnet anschließend den erwarteten SHA-256 neu. Fehlende Provenance, Status ungleich `PASS`, Schemaabweichung, veränderte gebundene Closure-Fakten, Payload-Abweichung oder SHA-256-Abweichung werden fail-closed abgewiesen. Der Verifier verändert die Evidence-Datei nicht und dient damit als unabhängiger späterer Integritätscheck; er ist weiterhin keine digitale Signatur und kein Vertrauensnachweis für den Erzeuger.
