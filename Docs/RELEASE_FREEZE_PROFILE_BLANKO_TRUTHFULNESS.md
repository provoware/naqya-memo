# Release-Freeze-Vertrag: Profilanzeige „Blanco“ muss wahr sein

## Zweck

Die Oberfläche darf niemals den neutralen Profilzustand **„Blanco“** anzeigen, solange `app/server.py` im Hintergrund automatisch ein vorhandenes aktives Profil auswählt oder ein `Standardprofil` erzeugt.

Dieser Vertrag ist bewusst ein Release-Sicherheits-Gate und keine neue Produktfunktion.

## Aktueller Befund

Der Core-Startvertrag kann bereits `BLANCO` mit `profile_id = null` modellieren. Der reale Referenzserver besitzt jedoch weiterhin einen historischen Fallback auf das erste aktive Profil und erzeugt ohne vorhandenes Profil ein `Standardprofil`.

Eine rein optische Änderung der Profilanzeige auf „Blanco“ wäre deshalb sachlich falsch und könnte Nutzer über den tatsächlich aktiven Datenkontext täuschen.

Zusätzlich ist der geschützte Desktop-Start noch an ein konkretes aktives Profil gekoppelt: `app/secure_server.py` verwendet `base.PROFILE_ID` für PIN-Prüfung, Erststart-Härtung und Sicherheitszustand. `app/secure_response_server.py` bindet seinen isolierten Sicherheitszustand ebenfalls an dieses Profil. Ein Entfernen des Server-Fallbacks ohne vorherige Auth-Entkopplung könnte daher den Desktop-Zugriff beschädigen oder einen inkonsistenten Sicherheitszustand erzeugen.

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
- Sobald `app/server.py` keinen impliziten Profilfallback mehr besitzt, muss `app/secure_server.py` bereits von der zwingenden `base.PROFILE_ID`-Kopplung für PIN-/Erststart-Authentifizierung entkoppelt sein. Andernfalls blockiert das Gate den Übergang.

Zusätzlich prüft `tests/security/test_auth_profile_dependency_containment.py` per Python-AST (Syntaxbaum), dass direkte `PROFILE_ID`-Zugriffe in den Desktop-Sicherheitsservern ausschließlich innerhalb der bereits bekannten Auth-Grenzen liegen. Neue direkte Kopplungen an anderer Stelle blockieren fail-closed. Weniger direkte Zugriffe oder eine spätere vollständige Zentralisierung bleiben ausdrücklich zulässig.

Damit ist die Reihenfolge des späteren Runtime-Umbaus technisch abgesichert: **zuerst Auth-Vertrag profiloptional und zentral machen, danach realen Server auf Blanco umstellen**.

## CI-Durchsetzung

Der Vertrag wird zusätzlich durch `.github/workflows/profile-blanco-truthfulness.yml` bei Pull Requests und Pushes auf `main` automatisch ausgeführt. Der Workflow verwendet ausschließlich fest auf Commit-SHAs gepinnte GitHub Actions, persistiert keine Checkout-Zugangsdaten und ruft sowohl den Truthfulness-Test als auch das Auth-Profil-Containment ohne externe Testabhängigkeit direkt mit Python auf.

Wichtig: Die Testdateien besitzen eigene kleine Direct-Runner. Ein direkter Aufruf führt die jeweilige Vertragsprüfung tatsächlich aus, gibt PASS/FAIL bzw. eine Zusammenfassung aus und beendet den Prozess bei einem Fehler mit Exit-Code 1. Damit kann ein grüner Workflow nicht allein dadurch entstehen, dass Testfunktionen nur definiert, aber nie aufgerufen werden.

Damit sind die Tests nicht nur vorhandene lokale Evidence, sondern tatsächlich ausführende, fail-closed CI-Gates gegen spätere UI-/Backend-/Auth-Drift und gegen eine schleichende Ausbreitung der Profilkopplung.

## Freigabebedingung für den späteren Runtime-Blanco-Slice

Erst wenn der Server nachweisbar:

1. ohne ausdrückliche Profilauswahl kein bestehendes Profil aktiviert,
2. ohne ausdrückliche Profilerstellung kein Standardprofil erzeugt,
3. der Desktop-PIN-/Erststart-Schutz auch ohne bereits aktives `PROFILE_ID` einen definierten fail-closed Zustand besitzt,
4. im Blanco-Zustand keine profilgebundenen Lese- oder Schreibzugriffe auf fremde Daten zulässt,
5. `/api/state` den neutralen Zustand konsistent ausgibt,
6. Auswahl oder Neuanlage anschließend eindeutig in genau dieses Profil wechselt,

kann die sichtbare Profilanzeige auf `Blanco` umgestellt und dieser Übergang mit Runtime-/Browser-Evidence qualifiziert werden.

## Release-Status

Bis dieser Runtime-Vertrag vollständig implementiert und getestet ist, bleibt die Profil-Startänderung **Draft / NO-GO**. Der ausführbare Truthfulness-Test, das Profil/Auth-Kopplungs-Gate, das neue Dependency-Containment, ihre CI-Durchsetzung und die verständliche Ladeanzeige verhindern gefährliche bzw. verwirrende Zwischenzustände; sie ersetzen den Runtime-Blanco-Nachweis nicht.
