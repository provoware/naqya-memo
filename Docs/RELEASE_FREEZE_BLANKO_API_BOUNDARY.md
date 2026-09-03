# Release-Freeze-Vertrag: Blanco benötigt einen expliziten Profil-API-Grenzpunkt

## Befund

`app/server.py` aktiviert aktuell weiterhin automatisch ein vorhandenes aktives Profil oder erzeugt ein `Standardprofil`. Solange dieser historische Fallback existiert, ist der reale Server noch kein echter Blanco-Laufzeitzustand.

Die Sicherheitsserver besitzen inzwischen zentrale fail-closed Profilresolver und ein fehlendes Auth-Profil ist regressionsgesichert. Der nächste gefährliche Übergang wäre deshalb das Entfernen des Server-Fallbacks, bevor der HTTP-/API-Layer selbst profilgebundene Datenzugriffe zentral sperren kann.

## Release-Freeze-Schutz

`tests/release_gate/test_blanco_profile_api_boundary.py` verhindert genau diesen Halb-Umbau:

- Solange der historische Profilfallback vorhanden ist, bleibt das aktuelle Runtime-Verhalten unverändert.
- Wird der Fallback später entfernt, muss `app/server.py` vorher einen expliziten zentralen Guard `_require_profile_context` besitzen.
- Der Guard muss einen stabilen fail-closed Fehlercode `PROFILE_CONTEXT_REQUIRED` definieren.
- Ein synthetischer profilfreier Server ohne diesen Guard muss vom Detektor sicher als Verstoß erkannt werden.
- Ein synthetischer profilfreier Server mit explizitem Guard-Vertrag muss als vorbereitete sichere Struktur erkannt werden.

## Detektor-Härtung

Das Gate prüft den vorbereiteten Guard jetzt über den Python-AST (Syntaxbaum) statt nur über Textmarker. Für einen gültigen Vertrag müssen im ausführbaren Modul tatsächlich

- die Konstante `PROFILE_CONTEXT_REQUIRED = 'PROFILE_CONTEXT_REQUIRED'` definiert sein,
- eine echte Top-Level-Funktion `_require_profile_context` existieren und
- deren Raise-Pfad den stabilen Fehlercode referenzieren.

Kommentare, Docstrings oder sonstige inerte Stringliterale mit denselben Begriffen reichen ausdrücklich nicht aus. Ein eigener Mutationstest `test_detector_rejects_marker_only_false_green` schleust genau diesen Scheinvertrag ein und muss ihn fail-closed ablehnen. Syntaxfehler im zu prüfenden Quelltext gelten ebenfalls nicht als gültiger Guard-Vertrag.

Das Gate wird im spezialisierten Workflow `.github/workflows/profile-blanco-truthfulness.yml` bei Pull Requests und Pushes auf `main` direkt mit Python ausgeführt. Es benötigt keine zusätzliche Testbibliothek und beendet den CI-Schritt bei einem Verstoß mit Exit-Code 1.

## Wirkung

Der spätere Runtime-Blanco-Umbau kann damit nicht mehr versehentlich nur den Profilfallback entfernen und anschließend ungeschützte Memo-, Todo-, Kalender-, Asset- oder andere profilgebundene Pfade offenlassen. Zusätzlich kann ein Kommentar oder toter String den vorbereitenden Sicherheitsvertrag nicht mehr fälschlich als vorhanden erscheinen lassen. Der tatsächliche HTTP-Guard ist damit noch nicht implementiert; seine Existenz ist aber jetzt eine strukturell geprüfte Vorbedingung für den Übergang.

## Release-Grenze

Dieser Slice führt keine neue Produktfunktion ein und ändert kein Runtime-Verhalten. PR #99 bleibt Draft / NO-GO, bis der reale Server den vollständigen profilfreien Laufzeitzustand einschließlich zentralem API-Guard, neutralem `/api/state`, eindeutiger Profilauswahl und Runtime-/Browser-Evidence nachweist.

## Nächster zulässiger Slice

Als nächster einzelner Runtime-Slice darf `_require_profile_context` verhaltensneutral in `app/server.py` eingeführt und vor profilgebundene API-/Asset-Zugriffe gesetzt werden. Erst danach darf der historische Auto-Profil-Fallback entfernt werden.
