# Release-Freeze Rollup – Status AKTIV

## Zweck
Dieser Integrationszweig konsolidiert den bereits einzeln gehärteten und geprüften Release-Freeze-Stack in genau einen reviewbaren Pull Request gegen `main`. Es werden dadurch keine neuen Produktfunktionen eingeführt.

## Gebundener Ausgangsstand
- Rollup-Start-Head: `052a396cd7581de1a0a92dbe152c44b9276ea9d3`
- Ausgangsbasis `main`: `de9f25f54bfbcecb008614402a0eb77745dcc1e7`
- Abstand zur Basis beim Rollup-Start: 205 Commits voraus, 0 Commits zurück
- Letzter vollständig erfolgreicher Quality-Nachweis des gebundenen Ausgangsstands: Run #68, Workflow-Run-ID `33360352303`, Ergebnis `success`
- Initialer Rollup-Head: `25b9107d7d07f6a6eb8cc86dce93bbe1852ab973`
- GitHub-Compare-Nachweis: Ausgangsstand ist Merge-Base des initialen Rollup-Heads; `ahead_by=1`, `behind_by=0`; der einzige damalige Delta-Pfad war diese Rollup-Dokumentation.

## Sicherheitsvertrag
1. Der Rollup darf keine Produkt-, UI-, Schema- oder Domainfunktion hinzufügen.
2. Der Integrations-PR muss direkt gegen `main` laufen und einen frischen vollständigen Quality-Lauf erhalten.
3. Bis dieser frische Lauf vollständig erfolgreich ist, bleibt der Rollup Draft und darf nicht gemergt werden.
4. Vorgänger-Draft-PRs dürfen nur einzeln und erst nach einem expliziten Git-Containment-Nachweis gegen den aktuellen Rollup geschlossen werden.
5. Für jeden geschlossenen Vorgänger muss gelten: dessen Head ist Merge-Base/Vorfahre des Rollup-Heads und `behind_by=0`; bei Divergenz bleibt der Vorgänger offen.
6. Der qualifizierte Ausgangs-Head `052a396cd7581de1a0a92dbe152c44b9276ea9d3` muss ein echter Git-Vorfahre jedes akzeptierten Rollup-Heads bleiben.
7. Nach diesem Ausgangs-Head dürfen im Rollup ausschließlich die explizit freigegebenen Release-Prozessdateien geändert werden. Produktcode, UI, Schema und Domaincode sind fail-closed ausgeschlossen.
8. Der Quality-Checkout muss vollständige Git-Historie bereitstellen (`fetch-depth: 0`), damit der Vorfahrennachweis lokal und ohne zusätzliche API-/Netzwerkabhängigkeit geprüft werden kann.

## Kontrollierte Vorgänger-Konsolidierung
### PR #96
- PR #96 (`CI: block direct network clients in Quality test sources`) wurde als erster Vorgänger geprüft.
- Geprüfter PR-#96-Head: `052a396cd7581de1a0a92dbe152c44b9276ea9d3`.
- Geprüfter Rollup-Head vor der Dokumentationsaktualisierung: `b6482f59d2fb021a2f98f685de87f6cd054d49c3`.
- GitHub-Compare: `status=ahead`, `ahead_by=6`, `behind_by=0`; Merge-Base ist exakt der PR-#96-Head.
- Quality Run #74 / Workflow-Run-ID `33368589317` auf diesem Rollup-Head: `completed/success`.
- Ergebnis: PR #96 ist vollständig im kanonischen Rollup enthalten und wurde als `superseded by #97` geschlossen.

### PR #95
- PR #95 (`CI: lock Quality trigger and permission trust boundary`) wurde als zweiter Vorgänger einzeln geprüft.
- Geprüfter PR-#95-Head: `6bfd83898b0400f6bb3824259b63755ea57c4ba6`.
- Geprüfter Rollup-Head vor dieser Dokumentationsaktualisierung: `1ba51e2ee5cf48b47b045b69ca33d8cd8b068d78`.
- GitHub-Compare: `status=ahead`, `ahead_by=26`, `behind_by=0`; Merge-Base ist exakt der PR-#95-Head.
- Quality Run #75 / Workflow-Run-ID `33372770532` auf diesem Rollup-Head: `completed/success`.
- Ergebnis: PR #95 ist vollständig im kanonischen Rollup enthalten und darf als `superseded by #97` geschlossen werden. Kein weiterer Vorgänger-PR wird durch diesen Schritt freigegeben oder geschlossen.

## Automatischer Nachweis
`tests/release_gate/test_release_freeze_rollup_containment.py` prüft im Quality-Lauf:
- vollständige Git-Historie,
- Existenz des qualifizierten Ausgangs-Heads,
- `git merge-base --is-ancestor` gegen den aktuellen `HEAD`,
- ausschließlich freigegebene Post-Qualification-Pfade,
- keine Lösch-, Rename- oder Copy-Operationen in diesem Delta.

Maschinenlesbare Evidence: `registry/evidence/security/RELEASE_FREEZE_ROLLUP_CONTAINMENT_ACCEPTANCE.json`.

## Wirkung
Der Release-Freeze-Stand erhält einen einzigen kanonischen Integrationspunkt gegen `main`. Zusätzlich ist maschinell abgesichert, dass der bereits qualifizierte Hardening-Stand im Rollup nicht durch Rebase, Cherry-Pick-Verlust oder nachträgliche Produktänderungen unbemerkt verlassen wird. Die Vorgänger-Kette wird ausschließlich schrittweise und nur mit explizitem Git-Containment-Nachweis reduziert.
