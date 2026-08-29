# ADR-0001 — Kanonische strukturierte Persistenz: SQLite + Datei-Assets
**Status:** AKZEPTIERT  
**Datum:** 2026-08-28

## Entscheidung
Strukturierte Daten werden in SQLite gespeichert. Große oder originäre Assets (Audio, PDF, Dokumentdateien) bleiben als Dateien im Projektordner und werden per stabiler ID referenziert.

## Gründe
- echte Transaktionen und Rollback
- robuste Indizes und Suche
- plattformübergreifend verfügbar
- weniger Race Conditions als lose JSON-Dateien
- skalierbar für große Memo-/Todo-/Kalenderbestände
- Assets bleiben unabhängig transportierbar

## Sicherheitsregel
SQLite-Metadaten sind die kanonische Quelle für strukturierte Zustände. Ein Suchindex oder Cache darf niemals die einzige Quelle der Wahrheit sein.

## Folge
Backups müssen über die SQLite-Backup-API bzw. konsistente Snapshots erfolgen; blindes Kopieren einer aktiven WAL-Datenbank ist nicht zulässig.
