# VISUAL-UX-002 – Formularfeedback & Eingabefehler

Status: **BEWIESEN nach grünem SHA-genauem CI-Lauf**

## Ziel
Pflichtfeld-, Format- und Konfliktfehler werden zusätzlich zur globalen Fehlerkarte direkt am betroffenen Formularbereich verständlich und barrierearm angezeigt.

## Vertrag
- Browser-Validierung (`required`, Typ, Muster, Länge/Bereich) erzeugt einen sichtbaren Inline-Hinweis direkt am Feld.
- Fehlerfelder erhalten `aria-invalid="true"` und einen stabil ergänzten `aria-describedby`-Verweis auf den Inline-Hinweis.
- Der erste fehlerhafte Eingabebereich erhält kontrolliert Fokus; der bestehende gelbe `focus-visible`-Ring bleibt erkennbar.
- Nach Korrektur einer gültigen Eingabe werden Fehlerstatus und ARIA-Verknüpfung wieder entfernt.
- Strukturierte Serverfehler werden über das lokale Ereignis `provoware:api-error` an die Formularschicht weitergegeben; interne App-Fachlogik wird nicht dupliziert.
- Eindeutige Codes werden gezielt zugeordnet: Titelpflicht/-länge, fehlender Termin bei Erinnerung, Terminende vor Start, Datum/Zeit, Kalenderfarbname und Upload-Dateiname.
- `REVISION_CONFLICT` und `ASSET_REVISION_CONFLICT` werden bewusst als Formular-Konflikt dargestellt, nicht fälschlich als einzelner Feldfehler.
- Degraded Mode bleibt ausschließlich Aufgabe von VISUAL-UX-001 und wird nicht als Formularfehler umgedeutet.
- Server- und globale Fehlermeldung bleiben parallel erhalten; Inline-Feedback ersetzt keine Sicherheitsmeldung.

## Barrierefreiheit / Erscheinungsbild
- Symbol + Text + Fehlercode, nicht nur Farbe.
- `role="alert"` für Inline-/Formularhinweise.
- lange Texte und Codes brechen sicher um.
- keine feste Höhe, keine horizontale Scrollpflicht.
- eigener Reflow für XL-Schrift bis 200 % und <=720 px.
- sichtbarer Fokus bleibt gelb und kontrastreich.
- kontrolliertes Dark/Neon-Design ohne Glow-Überladung.

## Wartbarkeit
`app.js`, `styles.css`, Server, Datenmodell und Dashboard-Geometrie bleiben unverändert. Die neue Logik liegt in `form_feedback_ui.js/.css`; VISUAL-UX-001 wird nur um ein strukturiertes lokales Fehlerereignis und den Modul-Import erweitert.

## Scope
Keine neue Produktfunktion. Keine Navigation, kein Drawer/Scrim, keine Dashboard-Neugestaltung und keine Mutation-Semantik.
