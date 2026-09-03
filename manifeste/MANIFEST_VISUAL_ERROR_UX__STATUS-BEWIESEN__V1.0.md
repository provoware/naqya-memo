# VISUAL-UX-001 – Status- und Fehlerdarstellung

Status: **BEWIESEN nach grünem SHA-genauem CI-Lauf**

## Ziel
Die bereits vorhandenen strukturierten Fehlerdaten (`code`, `recovery_hint`, `degraded_mode`) werden vollständig und barrierearm bis in die Weboberfläche transportiert.

## Vertrag
- Erfolgsbestätigungen dürfen weiterhin kurz als Toast erscheinen.
- Fehler werden in einer persistenten Status-/Fehlerkomponente innerhalb des Arbeitsbereichs angezeigt.
- Die Komponente verwendet `role="alert"`, `aria-live="assertive"`, `aria-atomic="true"` sowie eindeutige Label-/Description-Beziehungen.
- Fehlerzustände werden nicht nur über Farbe vermittelt: sichtbares Symbol, Klartextstatus, Meldung, Lösung und Fehlercode sind Pflicht.
- `recovery_hint` wird als prominente **Lösung** angezeigt.
- `code` bleibt sichtbar, aber visuell sekundär.
- `degraded_mode` wird als **SICHERER NUR-LESE-MODUS** mit ⛔-Symbol dargestellt und darf nicht wie ein normaler Hinweis weggeklickt werden.
- `/api/health` stellt nach einem Seiten-Reload den serverseitigen `mutation_mode` wieder sichtbar her.
- Die DATEN-Statusanzeige wechselt im Degraded Mode zusätzlich auf den Text `Nur Lesen`.
- Serverfehler dürfen nicht mehr auf `e.message` reduziert werden; `code`, `recovery_hint` und `degraded_mode` bleiben erhalten.

## Barrierefreiheit und Zoom
- sichtbarer Tastaturfokus am Schließen-Button; bestehender globaler Fokusvertrag bleibt erhalten
- `overflow-wrap:anywhere` verhindert horizontales Abschneiden langer Fehlercodes/Hinweise
- bei Schriftstufe XL (bis 200 %) ordnet sich die Komponente zweispaltig neu; der Schließen-Button erhält eine eigene Zeile
- unter 720 px wird derselbe Reflow angewandt; keine feste Höhe und kein horizontaler Zwangsüberlauf
- Reduced-Motion-Vertrag bleibt erhalten

## Scope
Keine Dashboard-Neugestaltung, keine Navigation, kein Drawer/Scrim, keine Datenmodell- oder Server-Mutationsänderung. Nur Fehlertransport und Status-/Fehlerdarstellung.
