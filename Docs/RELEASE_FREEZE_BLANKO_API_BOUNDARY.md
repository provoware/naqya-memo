# Release-Freeze-Vertrag: Blanco benötigt einen expliziten Profil-API-Grenzpunkt

## Befund

`app/server.py` aktiviert aktuell weiterhin automatisch ein vorhandenes aktives Profil oder erzeugt ein `Standardprofil`. Solange dieser historische Fallback existiert, ist der reale Server noch kein echter Blanco-Laufzeitzustand.

Die Sicherheitsserver besitzen inzwischen zentrale fail-closed Profilresolver und ein fehlendes Auth-Profil ist regressionsgesichert. Vor dem späteren Entfernen des Server-Fallbacks ist nun zusätzlich der HTTP-/API-Layer selbst mit einem zentralen Profilkontext-Guard vorbereitet.

## Umgesetzter Release-Freeze-Schutz

`app/server.py` definiert jetzt den stabilen Fehlercode `PROFILE_CONTEXT_REQUIRED` und den zentralen Guard `_require_profile_context()`.

- Ein fehlender, leerer oder ungültiger Profilkontext wird fail-closed abgewiesen.
- Profilgebundene GET-API- und Asset-Dateipfade rufen den Guard vor Datenzugriff auf.
- POST-Mutationen rufen den Guard vor Body-Verarbeitung und Mutation auf.
- Statische UI-Dateien bleiben außerhalb dieses Guards, damit ein späterer echter Blanco-Start grundsätzlich noch eine Profilauswahloberfläche anzeigen kann.
- Der historische Auto-Profil-Fallback bleibt in diesem Slice absichtlich unverändert; dadurch ändert sich das heutige Runtime-Verhalten nicht.
- Die Nutzerfehlermeldung für `PROFILE_CONTEXT_REQUIRED` ist in einfacher Sprache im bestehenden Fehlerkanal hinterlegt.

## Regression / Gate

`tests/release_gate/test_blanco_profile_api_boundary.py` prüft weiterhin fail-closed:

- Der aktuelle reale Server muss den expliziten Guard bereits jetzt tatsächlich enthalten und aus `Handler.do_GET` sowie `Handler.do_POST` aufrufen.
- Wird der Fallback später entfernt, darf kein ungeschützter Blanco-Halbzustand entstehen.
- Ein synthetischer profilfreier Server ohne Guard wird abgelehnt.
- Kommentar-, Docstring- oder String-Scheinmarker werden nicht als Guard anerkannt.
- Ein definierter, aber vom HTTP-Dispatcher unbenutzter Guard wird abgelehnt.
- Ein synthetischer profilfreier Server mit explizit erzwungenem Guard-Vertrag wird akzeptiert.

## Detektor-Härtung

Das Gate prüft den vorbereiteten Guard über den Python-AST (Syntaxbaum) statt nur über Textmarker. Für einen gültigen Vertrag müssen im ausführbaren Modul tatsächlich

- die Konstante `PROFILE_CONTEXT_REQUIRED = 'PROFILE_CONTEXT_REQUIRED'` definiert sein,
- eine echte Top-Level-Funktion `_require_profile_context` existieren,
- deren Raise-Pfad den stabilen Fehlercode referenzieren und
- sowohl `Handler.do_GET` als auch `Handler.do_POST` den Guard als ausführbaren Funktionsaufruf enthalten.

Syntaxfehler im zu prüfenden Quelltext gelten ebenfalls nicht als gültiger Guard-Vertrag. Das Gate wird im spezialisierten Workflow `.github/workflows/profile-blanco-truthfulness.yml` direkt mit Python ausgeführt und benötigt keine zusätzliche Testbibliothek.

## Wirkung

Der gefährliche nächste Übergang ist jetzt deutlich enger abgesichert: Der historische Profilfallback kann später nicht entfernt werden, ohne dass bereits eine reale zentrale HTTP-Sicherheitsgrenze vorhanden ist. Gleichzeitig bleibt das aktuelle Referenzverhalten erhalten, weil weiterhin automatisch ein Profil bereitgestellt wird.

Dieser Slice führt keine neue Produktfunktion ein. Er ist ausschließlich eine Release-Sicherheits- und Robustheitshärtung.

## Release-Grenze

PR #99 bleibt Draft / NO-GO. Der reale Server startet weiterhin nicht wirklich Blanco, weil `app/server.py` nach wie vor ein aktives Profil übernimmt oder `Standardprofil` erzeugt. Außerdem ist `/api/state` im profilfreien Zustand aktuell noch durch den neuen Guard gesperrt und daher noch nicht als neutraler Blanco-Zustandsendpunkt qualifiziert.

## Nächster zulässiger Slice

Als nächster einzelner Slice sollte `/api/state` in einen ausdrücklich neutralen, profilfreien Read-only-Zustand zerlegt werden: Ohne Profil dürfen nur versions-, readiness- und Profilauswahl-relevante Informationen zurückgegeben werden; sämtliche profilgebundenen Counts, Settings, Kalender-, Memo-, Todo-, Asset- und Mutationspfade müssen weiterhin fail-closed bleiben. Erst danach sollte der historische Auto-Profil-Fallback entfernt werden.
