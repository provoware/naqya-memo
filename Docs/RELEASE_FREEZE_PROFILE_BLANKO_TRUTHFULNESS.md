# Release-Freeze-Vertrag: Profilanzeige „Blanco“ muss wahr sein

## Zweck

Die Oberfläche darf niemals den neutralen Profilzustand **„Blanco“** anzeigen, solange `app/server.py` im Hintergrund automatisch ein vorhandenes aktives Profil auswählt oder ein `Standardprofil` erzeugt.

Dieser Vertrag ist bewusst ein Release-Sicherheits-Gate und keine neue Produktfunktion.

## Aktueller Befund

Der Core-Startvertrag kann bereits `BLANCO` mit `profile_id = null` modellieren. Der reale Referenzserver besitzt jedoch weiterhin einen historischen Fallback auf das erste aktive Profil und erzeugt ohne vorhandenes Profil ein `Standardprofil`.

Eine rein optische Änderung der Profilanzeige auf „Blanco“ wäre deshalb sachlich falsch und könnte Nutzer über den tatsächlich aktiven Datenkontext täuschen.

## Automatischer Schutz

`tests/release_gate/test_profile_blanco_truthfulness.py` prüft fail-closed:

- Wird `Blanco` direkt am sichtbaren Element `profileName` im HTML gesetzt, darf kein stiller Server-Fallback mehr existieren.
- Wird `Blanco` per JavaScript direkt in `profileName` geschrieben, darf ebenfalls kein stiller Server-Fallback mehr existieren.
- Solange der historische Fallback noch vorhanden ist, muss die Oberfläche auf eine wahrheitsgemäße neutrale/noch nicht aufgelöste Anzeige beschränkt bleiben.

## Freigabebedingung für den späteren Runtime-Blanco-Slice

Erst wenn der Server nachweisbar:

1. ohne ausdrückliche Profilauswahl kein bestehendes Profil aktiviert,
2. ohne ausdrückliche Profilerstellung kein Standardprofil erzeugt,
3. im Blanco-Zustand keine profilgebundenen Lese- oder Schreibzugriffe auf fremde Daten zulässt,
4. `/api/state` den neutralen Zustand konsistent ausgibt,
5. Auswahl oder Neuanlage anschließend eindeutig in genau dieses Profil wechselt,

kann die sichtbare Profilanzeige auf `Blanco` umgestellt und dieser Übergang mit Runtime-/Browser-Evidence qualifiziert werden.

## Release-Status

Bis dieser Runtime-Vertrag vollständig implementiert und getestet ist, bleibt die Profil-Startänderung **Draft / NO-GO**. Der neue Truthfulness-Test verhindert lediglich einen gefährlichen Zwischenzustand; er ersetzt den Runtime-Blanco-Nachweis nicht.
