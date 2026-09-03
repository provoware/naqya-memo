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

Zusätzlich schützt `tests/release_gate/test_blanco_readonly_state_boundary.py` den späteren `/api/state`-Übergang fail-closed:

- Solange kein explizit neutraler Blanco-State existiert, muss `/api/state` vom allgemeinen Profilguard erfasst bleiben.
- Wird `/api/state` später aus dem Guard ausgenommen, muss ein eigener `_blanco_api_state()`-Vertrag vorhanden und im Dispatcher tatsächlich verwendet werden.
- Dieser neutrale Zustand darf auf oberster Ebene ausschließlich `version`, `profile` und `readiness` liefern.
- `version` muss direkt `APP_VERSION` sein und `profile` muss exakt `None` sein.
- `readiness` ist ebenfalls strikt geschlossen: erlaubt sind ausschließlich `state: "PROFILE_REQUIRED"` und `profile_required: true`.
- Zusätzliche Profilnamen, Pfade, Datenbankangaben, Counts oder sonstige Laufzeitdetails dürfen nicht über `readiness` als Seitenkanal ausgegeben werden.
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

`tests/release_gate/test_blanco_readonly_state_boundary.py` ergänzt jetzt fünf gezielte Prüfungen:

- aktueller Server: `/api/state` bleibt geschützt oder muss bereits den neutralen Vertrag erfüllen,
- Mutation: naive State-Ausnahme mit vollständigem `api_state()` wird abgelehnt,
- Mutation: scheinbar neutraler Helper mit Store-/Profildatenzugriff wird abgelehnt,
- Mutation: zusätzliche Profil-/Pfad-/Laufzeitdetails innerhalb von `readiness` werden abgelehnt,
- Positivvertrag: minimaler datenfreier Zustand mit exakt `version`, `profile: None` und `readiness = {state: PROFILE_REQUIRED, profile_required: true}` wird akzeptiert.

### Evidence-Härtung der synthetischen Testfälle

Workflow Run `33771891046` zeigte einen Testfehler im Read-only-State-Gate: Die drei synthetischen Python-Fixtures enthielten jeweils ein `try:` ohne zugehöriges `except` oder `finally`. Dadurch war der Positivvertrag fälschlich rot; zugleich konnten die beiden Negativtests nur wegen desselben Syntaxfehlers grün erscheinen.

Die Fixtures sind deshalb syntaktisch vollständige Python-Programme. Zusätzlich ruft jeder synthetische Test vor der eigentlichen Sicherheitsbehauptung `_assert_valid_synthetic()` auf. Damit gilt fail-closed: Ein Negativtest darf nicht mehr wegen eines Parserfehlers scheinbar erfolgreich sein, sondern muss tatsächlich an der geprüften Sicherheitsregel scheitern.

Die aktuelle Härtung schließt zusätzlich eine semantische False-Green-Lücke: Die frühere Prüfung begrenzte nur die drei Top-Level-Felder. Ein formal erlaubtes `readiness`-Objekt hätte deshalb zusätzliche sensible Laufzeitdetails transportieren können. Das Gate validiert nun auch dessen exakte innere Struktur und den erwarteten konstanten Zustand.

Beide Release-Gates werden im spezialisierten Workflow `.github/workflows/profile-blanco-truthfulness.yml` direkt mit Python ausgeführt und benötigen keine zusätzliche Testbibliothek.

### Scope des kanonischen Rollup-Containments

Das allgemeine Quality-Workflow ruft `tests/release_gate/test_release_freeze_rollup_containment.py` bei jedem Pull Request und bei Pushes auf `main` auf. Der eigentliche Containment-Vertrag gehört jedoch ausschließlich zum kanonischen Rollup `integration/release-freeze-rollup-20260831 -> main` (PR #97).

Der Test unterscheidet deshalb jetzt explizit zwischen Anwendbarkeit und Prüfung:

- Im kanonischen Rollup-PR bleibt die bestehende Vorfahren-, Allowlist- und Destruktivitätsprüfung vollständig fail-closed aktiv.
- Andere GitHub-Actions-PRs, einschließlich PR #99, werden nicht gegen die Rollup-spezifische Post-Qualification-Allowlist beurteilt und melden sichtbar `NOT_APPLICABLE`.
- `push(main)` meldet ebenfalls `NOT_APPLICABLE`, weil dort kein Rollup-PR-Kontext vorliegt.
- Lokale/direct Aufrufe bleiben absichtlich streng und führen weiterhin die vollständige Containment-Prüfung aus.
- Eingebaute Scope-Regressionen beweisen den kanonischen Positivfall sowie falschen Head, falsche Base, `push(main)` und lokalen Direktlauf.

Damit wird keine Rollup-Allowlist erweitert und keine Produktdatei nachträglich als qualifiziert erklärt. PR #97 behält seine bisherige Sicherheitsgrenze unverändert; andere Produkt-PRs können dagegen ihre tatsächlich relevanten Quality-Gates erreichen.

## Wirkung

Der gefährliche nächste Übergang ist enger abgesichert: Der historische Profilfallback kann später nicht entfernt werden, ohne dass eine reale HTTP-Sicherheitsgrenze vorhanden ist. Zusätzlich kann `/api/state` weder als profilfreier Vollzustandskanal noch über ein formal neutrales, aber inhaltlich überladenes `readiness`-Objekt geöffnet werden.

Die Test-Evidence ist belastbarer: Synthetische Mutationen müssen gültigen Python-Code darstellen und der Minimalvertrag ist jetzt bis auf die verschachtelte Readiness-Struktur geschlossen. Zusätzlich verhindert die CI-Scope-Trennung, dass ein Rollup-spezifisches Gate fachfremde Produkt-PRs blockiert, ohne den kanonischen Rollup selbst zu lockern.

Dieser Slice verändert keinen Produkt-, UI-, Runtime- oder Schema-Code. Er ist ausschließlich eine Release-Sicherheits-, CI-Scope-, Testabdeckungs- und Evidence-Härtung innerhalb des Freeze.

## Release-Grenze

PR #99 bleibt Draft / NO-GO. Der reale Server startet weiterhin nicht wirklich Blanco, weil `app/server.py` nach wie vor ein aktives Profil übernimmt oder `Standardprofil` erzeugt. `/api/state` bleibt bis zur tatsächlichen Implementierung eines minimalen neutralen Zustands ausdrücklich profilgebunden.

## Nächster zulässiger Slice

Erst wenn der allgemeine Quality-Lauf und der spezialisierte Blanco-Workflow auf demselben neuen PR-#99-Head vollständig grün sind, kann `_blanco_api_state()` als nächster einzelner Runtime-Slice implementiert werden. Ohne Profil darf dieser Zustand ausschließlich `APP_VERSION`, `profile: null` und `readiness: {state: "PROFILE_REQUIRED", profile_required: true}` liefern; alle Memo-, Todo-, Kalender-, Settings-, Asset-, Diagnose-, Backup- und Mutationsdaten bleiben weiterhin strikt hinter `_require_profile_context()`. Erst nach grüner Regression dieses Zustands sollte der historische Auto-Profil-Fallback entfernt werden.
