# Release-Freeze-Vertrag: Blanco benötigt einen expliziten Profil-API-Grenzpunkt

## Befund

`app/server.py` aktiviert aktuell weiterhin automatisch ein vorhandenes aktives Profil oder erzeugt ein `Standardprofil`. Solange dieser historische Fallback existiert, ist der reale Server noch kein echter Blanco-Laufzeitzustand.

Die Sicherheitsserver besitzen inzwischen zentrale fail-closed Profilresolver und ein fehlendes Auth-Profil ist regressionsgesichert. Vor dem späteren Entfernen des Server-Fallbacks ist nun zusätzlich der HTTP-/API-Layer selbst mit einem zentralen Profilkontext-Guard vorbereitet.

Ein weiterer kritischer Übergang betrifft `/api/state`: Dieser Endpunkt ist derzeit noch profilgebunden und durch den Guard geschützt. Beim späteren Blanco-Umbau darf er nicht einfach aus dem Guard ausgenommen werden, weil `api_state()` aktuell Settings, Counts, Kalender-, Asset-, Audio-, Backup- und weitere Laufzeitdaten zusammenführt.

## Umgesetzter Release-Freeze-Schutz

`app/server.py` definiert den stabilen Fehlercode `PROFILE_CONTEXT_REQUIRED` und den zentralen Guard `_require_profile_context()`.

- Ein fehlender, leerer oder ungültiger Profilkontext wird fail-closed abgewiesen.
- Profilgebundene GET-API- und Asset-Dateipfade rufen den Guard vor Datenzugriff auf.
- POST-Mutationen rufen den Guard vor Body-Verarbeitung und Mutation auf.
- Statische UI-Dateien bleiben außerhalb dieses Guards, damit ein späterer echter Blanco-Start grundsätzlich noch eine Profilauswahloberfläche anzeigen kann.
- Der historische Auto-Profil-Fallback bleibt unverändert; dadurch ändert sich das heutige Runtime-Verhalten nicht.
- Die Nutzerfehlermeldung für `PROFILE_CONTEXT_REQUIRED` ist in einfacher Sprache im bestehenden Fehlerkanal hinterlegt.

Zusätzlich schützt jetzt `tests/release_gate/test_blanco_readonly_state_boundary.py` den späteren `/api/state`-Übergang fail-closed:

- Solange kein explizit neutraler Blanco-State existiert, muss `/api/state` vom allgemeinen Profilguard erfasst bleiben.
- Wird `/api/state` später aus dem Guard ausgenommen, muss ein eigener `_blanco_api_state()`-Vertrag vorhanden und im Dispatcher tatsächlich verwendet werden.
- Dieser neutrale Zustand darf auf oberster Ebene ausschließlich `version`, `profile` und `readiness` liefern.
- Der neutrale Helper darf keine profil-/datengebundenen Stores, Services, Assets, Queue-, Memo-, Todo-, Kalender- oder vollständigen `api_state()`-Daten abfragen.
- Ein naives `path != '/api/state'` bei anschließendem Aufruf von `api_state()` wird ausdrücklich als unsicher blockiert.

## Regression / Gate

`tests/release_gate/test_blanco_profile_api_boundary.py` prüft weiterhin fail-closed:

- Der aktuelle reale Server muss den expliziten Guard bereits jetzt tatsächlich enthalten und aus `Handler.do_GET` sowie `Handler.do_POST` aufrufen.
- Wird der Fallback später entfernt, darf kein ungeschützter Blanco-Halbzustand entstehen.
- Ein synthetischer profilfreier Server ohne Guard wird abgelehnt.
- Kommentar-, Docstring- oder String-Scheinmarker werden nicht als Guard anerkannt.
- Ein definierter, aber vom HTTP-Dispatcher unbenutzter Guard wird abgelehnt.
- Ein synthetischer profilfreier Server mit explizit erzwungenem Guard-Vertrag wird akzeptiert.

Das neue `tests/release_gate/test_blanco_readonly_state_boundary.py` ergänzt vier gezielte Prüfungen:

- aktueller Server: `/api/state` bleibt geschützt oder muss bereits den neutralen Vertrag erfüllen,
- Mutation: naive State-Ausnahme mit vollständigem `api_state()` wird abgelehnt,
- Mutation: scheinbar neutraler Helper mit Store-/Profildatenzugriff wird abgelehnt,
- Positivvertrag: minimaler datenfreier Zustand mit exakt `version/profile/readiness` wird akzeptiert.

Beide Release-Gates werden im spezialisierten Workflow `.github/workflows/profile-blanco-truthfulness.yml` direkt mit Python ausgeführt und benötigen keine zusätzliche Testbibliothek.

## Wirkung

Der gefährliche nächste Übergang ist enger abgesichert: Der historische Profilfallback kann später nicht entfernt werden, ohne dass eine reale HTTP-Sicherheitsgrenze vorhanden ist. Zusätzlich kann `/api/state` nicht versehentlich als profilfreier Vollzustandskanal geöffnet werden.

Dieser Slice führt keine neue Produktfunktion und keine Runtime-Verhaltensänderung ein. Er ist ausschließlich eine Release-Sicherheits-, Datenschutz-, Robustheits- und Regressionhärtung innerhalb des Freeze.

## Release-Grenze

PR #99 bleibt Draft / NO-GO. Der reale Server startet weiterhin nicht wirklich Blanco, weil `app/server.py` nach wie vor ein aktives Profil übernimmt oder `Standardprofil` erzeugt. `/api/state` bleibt bis zur tatsächlichen Implementierung eines minimalen neutralen Zustands ausdrücklich profilgebunden.

## Nächster zulässiger Slice

Als nächster einzelner Runtime-Slice kann `_blanco_api_state()` implementiert werden. Ohne Profil darf dieser Zustand ausschließlich Version, `profile: null` und eine minimale Readiness-/Profilauswahl-Aussage liefern; alle Memo-, Todo-, Kalender-, Settings-, Asset-, Diagnose-, Backup- und Mutationsdaten bleiben weiterhin strikt hinter `_require_profile_context()`. Erst nach grüner Regression dieses Zustands sollte der historische Auto-Profil-Fallback entfernt werden.
