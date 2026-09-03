# Release-Freeze-Vertrag: Profilanzeige „Blanco“ muss wahr sein

## Zweck

Die Oberfläche darf niemals den neutralen Profilzustand **„Blanco“** anzeigen, solange `app/server.py` im Hintergrund automatisch ein vorhandenes aktives Profil auswählt oder ein `Standardprofil` erzeugt.

Dieser Vertrag ist bewusst ein Release-Sicherheits-Gate und keine neue Produktfunktion.

## Aktueller Befund

Der Core-Startvertrag kann bereits `BLANCO` mit `profile_id = null` modellieren. Der reale Referenzserver besitzt jedoch weiterhin einen historischen Fallback auf das erste aktive Profil und erzeugt ohne vorhandenes Profil ein `Standardprofil`.

Eine rein optische Änderung der Profilanzeige auf „Blanco“ wäre deshalb sachlich falsch und könnte Nutzer über den tatsächlich aktiven Datenkontext täuschen.

## Nutzerseitiger Zwischenzustand

Bis der echte Runtime-Blanco-Vertrag umgesetzt ist, zeigt die Tool-Info beim Laden nicht mehr nur ein bedeutungsloses Auslassungszeichen. Das sichtbare Profilelement meldet jetzt **„wird geprüft …“**.

Der Profilstatus ist zugleich als zugänglicher Live-Status (`role="status"`, `aria-live="polite"`, `aria-atomic="true"`) ausgezeichnet. Sobald `/api/state` den tatsächlichen Profilnamen liefert, ersetzt `app.js` den Prüfstatus; unterstützende Technik kann diese Zustandsänderung ohne aggressiven Fokuswechsel ankündigen.

Damit wird bewusst **nicht** vorgetäuscht, dass bereits ein Blanco-Profil aktiv wäre.

## Automatischer Schutz

`tests/release_gate/test_profile_blanco_truthfulness.py` prüft fail-closed:

- Wird `Blanco` direkt am sichtbaren Element `profileName` im HTML gesetzt, darf kein stiller Server-Fallback mehr existieren.
- Wird `Blanco` per JavaScript direkt in `profileName` geschrieben, darf ebenfalls kein stiller Server-Fallback mehr existieren.
- Der initiale Profilstatus muss verständlich als laufende Prüfung erkennbar sein.
- Das Profilelement muss als höflicher, atomarer Live-Status für Screenreader ausgezeichnet bleiben.
- Solange der historische Fallback noch vorhanden ist, darf die Oberfläche keinen neutralen Blanco-Zustand behaupten.

## CI-Durchsetzung

Der Vertrag wird zusätzlich durch `.github/workflows/profile-blanco-truthfulness.yml` bei Pull Requests und Pushes auf `main` automatisch ausgeführt. Der Workflow verwendet ausschließlich fest auf Commit-SHAs gepinnte GitHub Actions, persistiert keine Checkout-Zugangsdaten und führt genau den vorhandenen Truthfulness-Test aus.

Damit ist der Test nicht mehr nur vorhandene lokale Evidence, sondern ein eigenständiges fail-closed CI-Gate gegen spätere UI-/Backend-Drift.

## Freigabebedingung für den späteren Runtime-Blanco-Slice

Erst wenn der Server nachweisbar:

1. ohne ausdrückliche Profilauswahl kein bestehendes Profil aktiviert,
2. ohne ausdrückliche Profilerstellung kein Standardprofil erzeugt,
3. im Blanco-Zustand keine profilgebundenen Lese- oder Schreibzugriffe auf fremde Daten zulässt,
4. `/api/state` den neutralen Zustand konsistent ausgibt,
5. Auswahl oder Neuanlage anschließend eindeutig in genau dieses Profil wechselt,

kann die sichtbare Profilanzeige auf `Blanco` umgestellt und dieser Übergang mit Runtime-/Browser-Evidence qualifiziert werden.

## Release-Status

Bis dieser Runtime-Vertrag vollständig implementiert und getestet ist, bleibt die Profil-Startänderung **Draft / NO-GO**. Der Truthfulness-Test, seine CI-Durchsetzung und die verständliche Ladeanzeige verhindern gefährliche bzw. verwirrende Zwischenzustände; sie ersetzen den Runtime-Blanco-Nachweis nicht.
