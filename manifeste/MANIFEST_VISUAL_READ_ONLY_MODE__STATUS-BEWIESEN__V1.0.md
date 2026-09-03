# MANIFEST · VISUAL-UX-004 · ECHTER NUR-LESE-BEDIENMODUS

**Status:** STATUS-BEWIESEN  
**Version:** 1.0  
**Scope:** ausschließlich UI-/Client-Fehlerprävention nach serverseitigem Degraded Mode.

## Zweck

Wenn ERROR-UX den Server vorsorglich in `DEGRADED` versetzt, darf die Oberfläche keine weiteren Schreibaktionen mehr anstoßen. Lesen, Navigation, Anzeigen und nicht persistente Zoom-Bedienung bleiben verfügbar.

## Vertrag

1. `provoware:mutation-mode` überträgt READY/DEGRADED aus der zentralen Error-UI.
2. `read_only_ui.js` deaktiviert bekannte mutierende Bedienelemente sichtbar und barrierearm.
3. Gesperrte Elemente erhalten `disabled`, `aria-disabled=true` und einen verständlichen Grund.
4. Dynamisch nachgeladene Ansichten werden per `MutationObserver` ebenfalls gesperrt.
5. Navigation, Anzeige-/Lesefunktionen und Zoom werden nicht in die Mutationsselektoren aufgenommen.
6. `mutation_status_ui.js` blockiert als zweite Schutzgrenze jeden lokalen `POST` im Browser, solange `data-mutation-mode=degraded`.
7. Blockierte POSTs erreichen `previousFetch` und damit den Server nicht.
8. Der Client antwortet konsistent mit HTTP 503 / `MUTATION_DEGRADED_MODE`.
9. Nach READY bzw. sauberem Neustart werden ursprüngliche Disabled-/ARIA-/Title-Zustände vollständig restauriert.
10. Bestehende Produktlogik in `app.js`, Server, Datenmodell und Dashboard-Geometrie bleiben unverändert.

## Evidence

- Source-Vertrag: `tests/ui_consistency/test_visual_read_only_mode.py`
- Runtime-Vertrag: `tests/ui_consistency/test_visual_read_only_mode_runtime.mjs`
- Quality-Gate: `Visual read-only mode contract`
- Reale Browser-/Geräte-Endabnahme bleibt ein separates physisches Gate.
