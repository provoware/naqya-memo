# VISUAL-UX-003 – Mutationsstatus & Doppelklick-Prävention

Status: **BEWIESEN nach grünem SHA-genauem CI-Lauf**

## Ziel
Laufende lokale Schreiboperationen werden für den Nutzer eindeutig sichtbar und gegen versehentliche Doppel-POSTs abgesichert.

## Vertrag
- ausschließlich lokale `/api/`-Requests mit Methode `POST` werden erfasst; GET/Assets/externe Ziele bleiben unverändert
- der auslösende Button wird während des Requests temporär deaktiviert
- der zugehörige Formularbereich bzw. Button erhält `aria-busy=true`
- der Trigger erhält zusätzlich `aria-disabled=true`
- sichtbare Klartextzustände wie `Wird gespeichert …` und `Wird importiert …` ersetzen während der Mutation die normale Beschriftung
- identische gleichzeitige POSTs werden anhand Methode + lokalem Pfad/Query + Body-Descriptor dedupliziert
- bei Deduplizierung wird die bereits laufende Serverantwort geklont; es entsteht kein zweiter Server-Write
- JSON-, URLSearchParams-, FormData-, Blob/File-, ArrayBuffer- und Typed-Array-Bodies erhalten stabile Descriptoren
- Erfolg **und** Fehler räumen `disabled`, `aria-disabled`, `aria-busy`, Busy-Klasse und Originalbeschriftung garantiert wieder auf
- ursprünglich bereits deaktivierte/ARIA-markierte Zustände werden beim Restore respektiert
- Binary-Uploads sind über Name, Größe, Änderungszeit und MIME-Typ im Dedupe-Schlüssel unterscheidbar

## Darstellung
- Busy-Zustand ist durch Text + Cursor + dezente Spinnerform sichtbar und nicht nur farbcodiert
- bestehendes Dark-/Neon-System wird nur dezent ergänzt
- `prefers-reduced-motion` schaltet die Rotation ab
- keine neue Dashboard-Geometrie

## Scope
Keine Änderung an `app.js`, `styles.css`, Server, Datenmodell oder Mutation-Semantik. Nur klientenseitiger Laufzeitstatus und Schutz gegen versehentlich parallel identische Requests.

## Regression
- `tests/ui_consistency/test_visual_mutation_status.py`
- `tests/ui_consistency/test_visual_mutation_status_runtime.mjs`
