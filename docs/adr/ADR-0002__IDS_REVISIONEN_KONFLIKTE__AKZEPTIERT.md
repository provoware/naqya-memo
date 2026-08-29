# ADR-0002 — IDs, Revisionen und Konflikterkennung
**Status:** AKZEPTIERT

- Identität: UUIDv4.
- Sortierung: separate UTC-Zeitstempel; IDs tragen keine Semantik.
- Jede Änderung erhöht `revision`.
- Schreiboperationen können `expected_revision` verlangen.
- Abweichung ergibt `REVISION_CONFLICT`; niemals still überschreiben.
- Importkonflikte werden später über expliziten Merge-/Duplizieren-/Überspringen-Dialog gelöst.
