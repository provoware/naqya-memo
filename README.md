# PROVOWARE – NAQYA Memo Tool 2026

## 🧷 Safe Backup State – V0.12.2.3

> **Snapshot-Branch:** `sync/v0.12.2.3-safe-state-20260829`  
> **Vorheriger GitHub-Main gesichert:** `backup/pre-v0.12.2.3-20260829`  
> **Vor-Sync-Main-Commit:** `334dd2923fc01a633946137d71fdbebae34364da`  
> **Lokaler vollständiger Projekt-Snapshot:** `OI_PROVOWARE_IO_Multi_Memo_Modul_Tool_2026_V0.12.2.3_UI_SIMPLIFICATION_INPUT_GUIDANCE.zip`  
> **Snapshot-SHA-256:** `1797354a69ec768122b83fbf8de515bf9d904e681b0fb2fd64d490cf0fec21e7`  
> **Projektversion:** `0.12.2.3-UI-SIMPLIFICATION-INPUT-GUIDANCE`  
> **Release-Status:** 🔴 `NO-GO` · **1/7 reale Gates**  
> **Main verändert:** **NEIN**

### Sicherheitsvertrag

Dieser Branch dokumentiert den aktuellen V0.12.2.3-Safe-State. Der zuvor vorhandene GitHub-Stand wurde **vor jeder weiteren Synchronisierung** unverändert auf `backup/pre-v0.12.2.3-20260829` gesichert. `main` wird erst dann ersetzt oder zusammengeführt, wenn der neue Projektstand vollständig und nachvollziehbar im Repository vorhanden und geprüft ist.

**Wichtig:** Der lokale V0.12.2.3-Stand unterscheidet sich architektonisch deutlich vom bisherigen GitHub-Main 0.5.1-E7. Deshalb erfolgt kein blindes Force-Update.

### Wiederherstellung

- Alter GitHub-Zustand: Branch `backup/pre-v0.12.2.3-20260829`
- Aktueller vollständiger lokaler Snapshot: oben genanntes ZIP + SHA-256
- Maschinenlesbarer Status: `registry/GITHUB_BACKUP_STATUS.json`
- Snapshot-Manifest: `registry/SAFE_SNAPSHOT_MANIFEST.json`

### Aktueller V0.12.2.3-Stand

- UI Simplification & Input Guidance
- Eingabefelder in neutralem Silber/Graphit statt Hauptfarben
- optionale Feldvorgaben/Hilfen
- genau eine sichtbare Versionsstelle
- vereinfachte Status-/Dashboardstruktur
- optimierte linke Schnellnavigation
- Darstellung oben im Dashboard
- 80–200 % Schrift und Arbeitsbereich-Zoom mit adaptiver Neuordnung
- gezielte Regression: **57/57 PASS**
- Android-/iOS-WebAssets synchronisiert
- Browser-Visual-Gate auf realem Linux-Zielrechner weiterhin offen

### Nächster Safe-Sync-Schritt

1. vollständigen V0.12.2.3-Quellbaum auf diesem Snapshot-Branch spiegeln,
2. Dateimanifest und Hashes gegen den lokalen Snapshot prüfen,
3. Branch-Diff gegen den alten Main auditieren,
4. erst danach kontrolliert entscheiden, ob `main` auf den neuen Stand wechselt.

---

## Historischer GitHub-Stand vor V0.12.2.3

Der vorherige `main`-Stand bleibt unverändert im Backup-Branch `backup/pre-v0.12.2.3-20260829` erhalten. Er basierte auf NAQYA 0.5.1-E7 mit Tauri/PWA/Whisper-Architektur und realer Hardware-Evidence-Roadmap. Diese Historie wird durch die V0.12.2.3-Synchronisierung nicht gelöscht.
