# ENTWICKLUNGSITERATION V0.2 — DATENKERN
**Datum:** 2026-08-28  
**Ziel:** Persistenzvertrag von Papier-Spezifikation in ausführbaren Referenzkern überführen.

## Vorangekündigte Patchbereiche
1. `schemas/` — Datenbankschema
2. `core/reference_python/` — ausführbare Contract-Referenz
3. `docs/contracts/` — Mutation/Backup/Projektordner
4. `docs/adr/` — Technologieentscheidungen
5. `docs/failure_matrix/` — nächste Failure-Acceptance
6. README/TODO/CHANGELOG/BRAIN/GPT-Buch/Status — Repo-Synchronisierung

## Grund
Die UI darf erst auf einen Datenkern gesetzt werden, dessen atomare Änderungs-, Konflikt- und Recovery-Regeln messbar sind.

## Wirkung
- klare kanonische Quelle
- weniger Risiko stiller Überschreibungen
- standardisierte Operation-Evidence
- Backup kann konsistent erzeugt und geprüft werden
- V0.3 kann gezielt Crash- und Kill-Fälle injizieren
