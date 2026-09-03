# LINEAGE-RECOVERY-001

Status: REPOSITORY-SCOPE GESCHLOSSEN / RELEASE NO-GO

Ziel: Die qualifizierte Naqya-Produktlineage wiederherstellen und künftige Rückwärtsentwicklung technisch verhindern.

## Unveränderliche Referenzen
- qualifizierter Lineage-Anker: `c473e0895668ad66826cf710b713127f180cbe8e`
- qualifizierte V0.12.2.5-UI-Quelle: `0ac1343defe443157705364c7a14cee8b10fca61`
- eingefrorener Hardening-Spender: `09836a73885adcdd1400216ad39d3ab2571f6ae7`

## Wiederhergestellter Produktstand
- Produktversion: `0.12.2.5`
- UI-Vertragsversion: `0.12.2.5`
- Acceptance: `PRE-AUTOSAVE-R3 / 0.3.16`
- V0.12.2.2: `13/13 PASS`
- V0.12.2.3: `7/7 PASS`
- V0.12.2.4: `9/9 PASS`
- V0.12.2.5: `14/14 PASS`
- historischer XL-Scrim/Escape-Blocker: durch `XL-SCRIM-001` geschlossen

## SHA-genaue automatisierte Evidence
Der letzte produktcodehaltige Recovery-Stand wurde auf `dcf12e0b3e389815470fb77c52010c402bd30ae7` vollständig grün geprüft.

Der anschließende Evidence-Hardening-Commit `b2e4220ddb95bf91743d6796a93847e3d06e38f9` änderte ausschließlich die drei Recovery-Workflows und band Checkout sowie Gate-Nachweis explizit an den tatsächlichen PR-Head.

Auf exakt `b2e4220ddb95bf91743d6796a93847e3d06e38f9`:
- `quality` #218 / Run `33813891741`: SUCCESS
- `profile-blanco-truthfulness` #59 / Run `33813891689`: SUCCESS
- `product-lineage-guard` #19 / Run `33813891691`: SUCCESS

## Finaler Scope-Audit
Der PR-Diff gegen den qualifizierten Lineage-Anker enthält exakt die erwarteten Recovery-Klassen:
- CI-/Evidence-Gates,
- Produktbaseline, Versionsvertrag, Lineage-Verifier und Recovery-Dokumentation,
- UI-Vertragsanpassung,
- drei synchrone WebAsset-Sätze für Referenz, Android und iOS.

Nicht enthalten:
- keine neue Backend-/Domain-/DB-/Autosave-Funktion,
- kein ungeprüftes Hardening aus PR #104,
- keine Release-Promotion,
- keine künstliche Hochstufung physischer Browser-/Geräte-Gates.

## Regeln
1. Ein neuer Produkt-Head muss vom Lineage-Anker abstammen.
2. V0.12.2.2 bis V0.12.2.5 sind Pflichtverträge und dürfen nie als `SKIP` gelten.
3. Produktversion, UI-Vertragsversion, Acceptance-Track und Git-SHA sind getrennte Identitäten.
4. Der Hardening-Spender wird niemals als Produktbaseline verwendet; Änderungen werden später einzeln auditiert übertragen.
5. Repository-Scope und automatisierte Evidence sind geschlossen; dies ist ausdrücklich keine physische Release-Abnahme.
6. Release bleibt NO-GO, bis reale Browser-/Geräte-/Mikrofon-Gates ausdrücklich abgeschlossen sind.

## Noch offene physische Gates
- Kubuntu/KDE + Chrome: Navigation, Info-/Technik-Drawer, Scrim, Escape, Reflow und 200-%-/XL-Modus.
- Firefox: gleiche Kernpfade und Zoom-/Reflow-Abnahme.
- Mikrofon/Sprachmemo: Permission, Aufnahme, Abbruch, Speichern und Recovery.
- Android: reale Geräte-/WebView-Abnahme.
- iPhone/iOS: reale Geräte-/WebView-Abnahme.

## Reproduzierbarer Vollprojekt-Export
Der Recovery-Zweig enthält `.github/workflows/project-snapshot.yml`. Der Workflow:
- bindet den Checkout an den tatsächlichen PR-Head,
- prüft `git rev-parse HEAD` gegen die erwartete Source-SHA,
- erzeugt das vollständige getrackte Projekt mit `git archive`,
- prüft das ZIP mit `unzip -t`,
- erzeugt eine SHA-256-Prüfsumme,
- veröffentlicht ZIP, Prüfsumme und Snapshot-Metadaten als GitHub-Artifact.

Qualifizierter Export-Vorlauf auf `e6ac013dde221e9766f901851d2c7a709f2da249`:
- `project-snapshot` #2 / Run `33818854695`: SUCCESS
- `product-lineage-guard` #26 / Run `33818854693`: SUCCESS
- `profile-blanco-truthfulness` #62 / Run `33818854782`: SUCCESS
- `quality` #221 / Run `33818854705`: SUCCESS

Finaler Repository-Head `19a5776ed3f16160882bc795dbd86660777c9b07`:
- `project-snapshot` #6 / Run `33819006226`: SUCCESS
- `product-lineage-guard` #30 / Run `33819006293`: SUCCESS
- `profile-blanco-truthfulness` #64 / Run `33819006358`: SUCCESS
- `quality` #223 / Run `33819006239`: SUCCESS
- Vollprojekt-ZIP: 491 Dateien
- ZIP-SHA-256: `90d2641d84975556bc0c05d055bdee96a312b13b31708ceee706e96cdb240c70`

Erst nach dokumentierter physischer Evidence darf der Recovery-PR aus Draft genommen oder gemergt werden.
