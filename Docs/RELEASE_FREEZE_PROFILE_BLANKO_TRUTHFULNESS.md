# Release-Freeze-Vertrag: Profilanzeige „Blanco“ muss wahr sein

## Zweck

Die Oberfläche darf niemals den neutralen Profilzustand **„Blanco“** anzeigen, solange `app/server.py` im Hintergrund automatisch ein vorhandenes aktives Profil auswählt oder ein `Standardprofil` erzeugt.

Dieser Vertrag ist bewusst ein Release-Sicherheits-Gate und keine neue Produktfunktion.

## Aktueller Befund

Der Core-Startvertrag kann bereits `BLANCO` mit `profile_id = null` modellieren. Der reale Referenzserver besitzt jedoch weiterhin einen historischen Fallback auf das erste aktive Profil und erzeugt ohne vorhandenes Profil ein `Standardprofil`.

Eine rein optische Änderung der Profilanzeige auf „Blanco“ wäre deshalb sachlich falsch und könnte Nutzer über den tatsächlich aktiven Datenkontext täuschen.

Der geschützte Desktop-Start ist weiterhin fachlich an ein konkretes aktives Profil gekoppelt, aber die technische Kopplung ist jetzt in beiden Sicherheitslagen zentralisiert: `app/secure_server.py` darf `base.PROFILE_ID` ausschließlich im fail-closed Resolver `_auth_profile_id()` lesen; `app/secure_response_server.py` darf `secure.base.PROFILE_ID` ausschließlich in `_response_auth_profile_id()` lesen. PIN-Härtung, Revisionsprüfung, Cache-Prüfung und Request-Authentifizierung verwenden danach nur noch den aufgelösten Wert. Fehlt im inneren Auth-Layer eine eindeutige nichtleere Profil-ID, wird nicht geraten: Erststart-Härtung stoppt fail-closed, Revisions-/Cache-Prüfungen liefern keinen gültigen Sicherheitszustand und Request-Authentifizierung wird nicht freigegeben.

Damit ist die vorher verteilte direkte `PROFILE_ID`-Schuld auf zwei klar definierte Übergabepunkte reduziert. Der reale Blanco-Start ist dadurch noch nicht freigegeben: `server.py` erzeugt weiterhin den historischen Profilfallback, und der innere Auth-Layer besitzt für einen echten Start ohne Profil noch keinen vollständig qualifizierten Laufzeitvertrag jenseits des fail-closed Abbruchs.

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
- Sobald `app/server.py` keinen impliziten Profilfallback mehr besitzt, muss `app/secure_server.py` bereits von verstreuten zwingenden `base.PROFILE_ID`-Zugriffen entkoppelt sein. Andernfalls blockiert das Gate den Übergang.

Zusätzlich prüft `tests/security/test_auth_profile_dependency_containment.py` per Python-AST (Syntaxbaum), dass direkte `PROFILE_ID`-Zugriffe in beiden Desktop-Sicherheitsservern ausschließlich innerhalb ihrer zentralen Auth-Grenzen liegen. In `secure_server.py` ist **genau ein** direkter Zugriff erlaubt und verpflichtend: `base.PROFILE_ID` ausschließlich in `_auth_profile_id()`. Im äußeren `secure_response_server.py` gilt analog **genau ein** direkter Zugriff: `secure.base.PROFILE_ID` ausschließlich in `_response_auth_profile_id()`.

Das Containment begrenzt zusätzlich die Anzahl auf jeweils exakt einen direkten Zugriff pro Sicherheitslage. Neue direkte Verwendungen in PIN-, Cache-, Revisions-, Request- oder Response-Code blockieren fail-closed. Die technische Schuld kann damit künftig nur weiter sinken, nicht wieder unbemerkt wachsen.

Das Containment-Gate prüft seinen eigenen Detektor mit absichtlich eingeschleusten Mutationen: Ein synthetischer neuer Zugriff `base.PROFILE_ID` in einem nicht erlaubten Auth-Helfer muss eindeutig als Verstoß erkannt werden; ein zweiter direkter Zugriff selbst innerhalb von `_auth_profile_id()` muss am Mengenlimit scheitern. Eigene Contracts beweisen zusätzlich, dass innerer Auth-Layer und Response-Layer tatsächlich jeweils nur ihren einen Resolver als direkten Profilzugriff besitzen.

Damit ist die Reihenfolge des späteren Runtime-Umbaus technisch abgesichert: **beide Sicherheitslagen zentralisiert → inneren Auth-Vertrag für `profile_id=None` qualifizieren → danach realen Server-Fallback entfernen → Runtime-/Browser-Evidence → erst dann sichtbar Blanco**.

## CI-Durchsetzung

Der Vertrag wird zusätzlich durch `.github/workflows/profile-blanco-truthfulness.yml` bei Pull Requests und Pushes auf `main` automatisch ausgeführt. Der Workflow verwendet ausschließlich fest auf Commit-SHAs gepinnte GitHub Actions, persistiert keine Checkout-Zugangsdaten und ruft sowohl den Truthfulness-Test als auch das Auth-Profil-Containment ohne externe Testabhängigkeit direkt mit Python auf.

Wichtig: Die Testdateien besitzen eigene kleine Direct-Runner. Ein direkter Aufruf führt die jeweilige Vertragsprüfung tatsächlich aus, gibt PASS/FAIL bzw. eine Zusammenfassung aus und beendet den Prozess bei einem Fehler mit Exit-Code 1. Das Auth-Profil-Containment führt dabei die reale Quelltextprüfung, beide Resolver-Contracts sowie beide Mutationstests aus. Damit kann ein grüner Workflow nicht allein dadurch entstehen, dass Testfunktionen nur definiert, aber nie aufgerufen werden, der Detektor eine neue Zugriffsstelle übersieht oder zusätzliche direkte Zugriffe innerhalb eines Resolvers unbemerkt akzeptiert.

Damit sind die Tests nicht nur vorhandene lokale Evidence, sondern tatsächlich ausführende, fail-closed CI-Gates gegen spätere UI-/Backend-/Auth-Drift, gegen eine erneute Ausbreitung der Profilkopplung und gegen einen falsch grünen Containment-Detektor.

## Freigabebedingung für den späteren Runtime-Blanco-Slice

Erst wenn der Server nachweisbar:

1. ohne ausdrückliche Profilauswahl kein bestehendes Profil aktiviert,
2. ohne ausdrückliche Profilerstellung kein Standardprofil erzeugt,
3. der Desktop-PIN-/Erststart-Schutz auch ohne bereits aktives `PROFILE_ID` einen definierten und getesteten fail-closed Laufzeitzustand besitzt,
4. im Blanco-Zustand keine profilgebundenen Lese- oder Schreibzugriffe auf fremde Daten zulässt,
5. `/api/state` den neutralen Zustand konsistent ausgibt,
6. Auswahl oder Neuanlage anschließend eindeutig in genau dieses Profil wechselt,

kann die sichtbare Profilanzeige auf `Blanco` umgestellt und dieser Übergang mit Runtime-/Browser-Evidence qualifiziert werden.

## Release-Status

Bis dieser Runtime-Vertrag vollständig implementiert und getestet ist, bleibt die Profil-Startänderung **Draft / NO-GO**. Der ausführbare Truthfulness-Test, das Profil/Auth-Kopplungs-Gate, die nun in beiden Sicherheitslagen zentralisierten fail-closed Profilgrenzen, das mutationserprobte Dependency-Containment, ihre CI-Durchsetzung und die verständliche Ladeanzeige verhindern gefährliche bzw. verwirrende Zwischenzustände; sie ersetzen den Runtime-Blanco-Nachweis nicht.
