# Naqya PRE-AUTOSAVE Cloud Acceptance v0.3.16

Dieser Ordner ist ein eingefrorener, eigenstaendiger Acceptance-Testbestand fuer
`Provoware Naqya Memo Tool 2026 v0.3.16`.

Er enthaelt nur die fuer das Cross-Platform-Gate benoetigten, SHA-256-gebundenen
Quellen. Die Produktbasis im Repository wird dadurch nicht ersetzt oder veraendert.

Gate:
- Linux Host: Journal-/Write-/Index-Kill + Recovery + 5.000 Memos
- Windows Host: dieselben Tests
- macOS Host: dieselben Tests
- Firefox: echter Headless-Firefox mit Kill/Recovery + 5.000 IndexedDB-Eintraegen
- Merge: nur Evidenz mit identischer Plan-ID, Plan-SHA und identischen Source-SHAs

V0.4.0 SAFE AUTOSAVE darf nur bei `PASS` des zusammengefuehrten Evidence-Manifests
fachlich freigegeben werden.
