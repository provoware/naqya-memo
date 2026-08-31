# Release-Freeze Rollup – Status AKTIV

## Zweck
Dieser Integrationszweig konsolidiert den bereits einzeln gehärteten und geprüften Release-Freeze-Stack in genau einen reviewbaren Pull Request gegen `main`. Es werden dadurch keine neuen Produktfunktionen eingeführt.

## Gebundener Ausgangsstand
- Rollup-Start-Head: `052a396cd7581de1a0a92dbe152c44b9276ea9d3`
- Ausgangsbasis `main`: `de9f25f54bfbcecb008614402a0eb77745dcc1e7`
- Abstand zur Basis beim Rollup-Start: 205 Commits voraus, 0 Commits zurück
- Letzter vollständig erfolgreicher Quality-Nachweis des gebundene Ausgangsstands: Run #68, Workflow-Run-ID `33360352303`, Ergebnis `success`
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
- Geprüfter Rollup-Head vor der Dokumentationsaktualisierung: `b6482f59fcb62cf10dd9bf2ffd8d933dad9678bf`.
- GitHub-Compare: `status=ahead`, `ahead_by=6`, `behind_by=0`; Merge-Base ist exakt der PR-#96-Head.
- Quality Run #74 / Workflow-Run-ID `33368589317` auf diesem Rollup-Head: `completed/success`.
- Ergebnis: PR #96 ist vollständig im kanonischen Rollup enthalten und wurde als `superseded by #97` geschlossen.

### PR #95
- PR #95 (`CI: lock Quality trigger and permission trust boundary`) wurde als zweiter Vorgänger einzeln geprüft.
- Geprüfter PR-#95-Head: `6bfd83898b0400f6bb3824259b63755ea57c4ba6`.
- Geprüfter Rollup-Head vor dieser Dokumentationsaktualisierung: `1ba51e2ee5cf48b47b045b69ca33d8cd8b068d78`.
- GitHub-Compare: `status=ahead`, `ahead_by=26`, `behind_by=0`; Merge-Base ist exakt der PR-#95-Head.
- Quality Run #75 / Workflow-Run-ID `33372770532` auf diesem Rollup-Head: `completed/success`.
- Ergebnis: PR #95 ist vollständig im kanonischen Rollup enthalten und wurde als `superseded by #97` geschlossen.

### PR #94
- PR #94 (`CI: block implicit dependency installs and downloads`) wurde als dritter Vorgänger einzeln geprüft.
- Geprüfter PR-#94-Head: `73c52a42603830ecbb4ca5955c2de468a7145e77`.
- Geprüfter Rollup-Head vor dieser Dokumentationsaktualisierung: `be7851d80f26b12fbfe1be04f0ba351cbe5b8843`.
- GitHub-Compare: `status=ahead`, `ahead_by=32`, `behind_by=0`; Merge-Base ist exakt der PR-#94-Head.
- Quality Run #76 / Workflow-Run-ID `33377272682` auf diesem Rollup-Head: `completed/success`.
- Ergebnis: PR #94 ist vollständig im kanonischen Rollup enthalten und wurde als `superseded by #97` geschlossen.

### PR #93
- PR #93 (`CI: disable persistent checkout credentials`) wurde als vierter Vorgänger einzeln geprüft.
- Geprüfter PR-#93-Head: `a4c96829e517c4c1b3b6ab8a252b4e1ddb13e258`.
- Geprüfter Rollup-Head vor dieser Dokumentationsaktualisierung: `643ffcf74302c01eaf14a08e80ea06f35d5a1155`.
- GitHub-Compare: `status=ahead`, `ahead_by=37`, `behind_by=0`; Merge-Base ist exakt der PR-#93-Head.
- Quality Run #77 / Workflow-Run-ID `33381796980` auf diesem Rollup-Head: `completed/success`.
- Ergebnis: PR #93 ist vollständig im kanonischen Rollup enthalten und wurde als `superseded by #97` geschlossen.

### PR #92
- PR #92 (`CI: pin external GitHub Actions to immutable commits`) wurde als fünfter Vorgänger einzeln geprüft.
- Geprüfter PR-#92-Head: `89ee5b130f4916c950727298e12313563391b980`.
- Geprüfter Rollup-Head vor dieser Dokumentationsaktualisierung: `6e22f4bbff31a8acd9c7d761d2577460c2622f40`.
- GitHub-Compare: `status=ahead`, `ahead_by=42`, `behind_by=0`; Merge-Base ist exakt der PR-#92-Head.
- Quality Run #78 / Workflow-Run-ID `33386696227` auf diesem Rollup-Head: `completed/success`.
- Ergebnis: PR #92 ist vollständig im kanonischen Rollup enthalten und wurde als `superseded by #97` geschlossen.

### PR #91
- PR #91 (`Release gate: enforce provenance verifier in official closure path`) wurde als sechster Vorgänger einzeln geprüft.
- Geprüfter PR-#91-Head: `e55b49a16da84fdd80eaf1d788ac9be5b6bfe164`.
- Geprüfter Rollup-Head vor dieser Dokumentationsaktualisierung: `e789f65421f453a8b224c711e3497b7d0700164c`.
- GitHub-Compare: `status=ahead`, `ahead_by=47`, `behind_by=0`; Merge-Base ist exakt der PR-#91-Head.
- Quality Run #79 / Workflow-Run-ID `33391510794` auf diesem Rollup-Head: `completed/success`.
- Ergebnis: PR #91 ist vollständig im kanonischen Rollup enthalten und wurde als `superseded by #97` geschlossen.

### PR #90
- PR #90 (`Release gate: verify persisted closure provenance read-only`) wurde als siebter Vorgänger einzeln geprüft.
- Geprüfter PR-#90-Head: `1731517422b1ddb610a9273bf94e7dca94d625c3`.
- Geprüfter Rollup-Head vor dieser Dokumentationsaktualisierung: `9a7e2f31926b0675c2a460f826b77b7bf680e0fb`.
- GitHub-Compare: `status=ahead`, `ahead_by=53`, `behind_by=0`; Merge-Base ist exakt der PR-#90-Head.
- Quality Run #80 / Workflow-Run-ID `33397153956` auf diesem Rollup-Head: `completed/success`.
- Ergebnis: PR #90 ist vollständig im kanonischen Rollup enthalten und wurde als `superseded by #97` geschlossen.

### PR #89
- PR #89 (`Release gate: bind closure evidence to deterministic provenance fingerprint`) wurde als achter Vorgänger einzeln geprüft.
- Geprüfter PR-#89-Head: `1768ea5c90991ac649e9859f036cf258b83f7c48`.
- Geprüfter Rollup-Head vor dieser Dokumentationsaktualisierung: `2c66bc41cd7153b0b31fe55c46409234f73c1fbc`.
- GitHub-Compare: `status=ahead`, `ahead_by=59`, `behind_by=0`; Merge-Base ist exakt der PR-#89-Head.
- Quality Run #81 / Workflow-Run-ID `33404574385` auf diesem Rollup-Head: `completed/success`.
- Ergebnis: PR #89 ist vollständig im kanonischen Rollup enthalten und darf als `superseded by #97` geschlossen werden. Kein weiterer Vorgänger-PR wird durch diesen Schritt freigegeben oder geschlossen.

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