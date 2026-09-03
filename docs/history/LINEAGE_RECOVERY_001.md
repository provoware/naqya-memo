# LINEAGE-RECOVERY-001

Status: AKTIV / NO-GO

Ziel: Die qualifizierte Naqya-Produktlineage wiederherstellen und künftige Rückwärtsentwicklung technisch verhindern.

## Unveränderliche Referenzen
- qualifizierter Lineage-Anker: `c473e0895668ad66826cf710b713127f180cbe8e`
- qualifizierte V0.12.2.5-UI-Quelle: `0ac1343defe443157705364c7a14cee8b10fca61`
- eingefrorener Hardening-Spender: `09836a73885adcdd1400216ad39d3ab2571f6ae7`

## Regeln
1. Ein neuer Produkt-Head muss vom Lineage-Anker abstammen.
2. V0.12.2.2 bis V0.12.2.5 sind Pflichtverträge und dürfen nie als `SKIP` gelten.
3. Produktversion, UI-Vertragsversion, Acceptance-Track und Git-SHA sind getrennte Identitäten.
4. Der Hardening-Spender wird niemals als Produktbaseline verwendet; Änderungen werden später einzeln auditiert übertragen.
5. V0.12.2.5 wird zunächst exakt auf den historischen 13/14-Stand rekonstruiert. Der bekannte XL-Scrim/Escape-Fehler bleibt bis dahin unverändert.
6. Release bleibt NO-GO, bis reale Browser-/Geräte-Gates ausdrücklich abgeschlossen sind.
