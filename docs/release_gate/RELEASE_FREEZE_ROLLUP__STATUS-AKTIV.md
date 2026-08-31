# Release-Freeze Rollup – Status AKTIV

## Zweck
Dieser Integrationszweig konsolidiert den bereits einzeln gehärteten und geprüften Release-Freeze-Stack in genau einen reviewbaren Pull Request gegen `main`. Es werden dadurch keine neuen Produktfunktionen eingeführt.

## Gebundener Ausgangsstand
- Rollup-Start-Head: `052a396cd7581de1a0a92dbe152c44b9276ea9d3`
- Ausgangsbasis `main`: `de9f25f54bfbcecb008614402a0eb77745dcc1e7`
- Abstand zur Basis beim Rollup-Start: 205 Commits voraus, 0 Commits zurück
- Letzter vollständig erfolgreicher Quality-Nachweis des gebundenden Ausgangsstands: Run #68, Workflow-Run-ID `33360352303`, Ergebnis `success`
- Initialer Rollup-Head: `25b9107d7d07f6a6eb8cc86dce93bbe1852ab973`
- GitHub-Compare-Nachweis: Ausgangsstand ist Merge-Base des initialen Rollup-Heads; `ahead_by=1`, `behind_by=0`; der einzige damalige Delta-Pfad war diese Rollup-Dokumentation.

## Sicherheitsvertrag
1. Der Rollup darf keine Produkt-, UI-, Schema- oder Domainfunktion hinzufügen.
2. Der Integrations-PR muss direkt gegen `main` laufen und einen frischen vollständigen Quality-Lauf erhalten.
3. Bis dieser frische Lauf vollständig erfolgreich ist, bleibt der Rollup Draft und darf nicht gemergt werden.
4. Die vorhandenen gestapelten Draft-PRs werden in diesem Slice nicht geschlossen oder gemergt; dadurch bleibt ein verlustfreier Rückweg erhalten.
5. Erst nach erfolgreicher Rollup-Validierung darf in einem separaten Schritt über Schließen/Archivieren der ersetzten Draft-PR-Kette entschieden werden.
6. Der qualifizierte Ausgangs-Head `052a396cd7581de1a0a92dbe152c44b9276ea9d3` muss ein echter Git-Vorfahre jedes akzeptierten Rollup-Heads bleiben.
7. Nach diesem Ausgangs-Head dürfen im Rollup ausschließlich die explizit freigegebenen Release-Prozessdateien geändert werden. Produktcode, UI, Schema und Domaincode sind fail-closed ausgeschlossen.
8. Der Quality-Checkout muss vollständige Git-Historie bereitstellen (`fetch-depth: 0`), damit der Vorfahrennachweis lokal und ohne zusätzliche API-/Netzwerkabhängigkeit geprüft werden kann.

## Automatischer Nachweis
`tests/release_gate/test_release_freeze_rollup_containment.py` prüft im Quality-Lauf:
- vollständige Git-Historie,
- Existenz des qualifizierten Ausgangs-Heads,
- `git merge-base --is-ancestor` gegen den aktuellen `HEAD`,
- ausschließlich freigegebene Post-Qualification-Pfade,
- keine Lösch-, Rename- oder Copy-Operationen in diesem Delta.

Maschinenlesbare Evidence: `registry/evidence/security/RELEASE_FREEZE_ROLLUP_CONTAINMENT_ACCEPTANCE.json`.

## Wirkung
Der Release-Freeze-Stand erhält einen einzigen kanonischen Integrationspunkt gegen `main`. Zusätzlich ist jetzt maschinell abgesichert, dass der bereits qualifizierte Hardening-Stand im Rollup nicht durch Rebase, Cherry-Pick-Verlust oder nachträgliche Produktänderungen unbemerkt verlassen wird.
