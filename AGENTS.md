# AGENTS.md – NAQYA Entwicklungsvertrag

## Zweck
Diese Datei ist die verbindliche Arbeitsanweisung für alle künftigen Änderungen an NAQYA. Sie wird bei jeder relevanten technischen, sicherheits-, Build-, CI-, Release- oder Architekturänderung mitgeprüft.

## Grundregeln
- Änderungen klein, nachvollziehbar und rückrollbar umsetzen.
- Kein Merge nach `main`, solange der exakte PR-Head nicht vollständig grün validiert ist.
- Stabilität, Wartbarkeit, Sicherheit, Reproduzierbarkeit und nachvollziehbare Evidence haben Vorrang vor Funktionsmenge.
- Keine stillen Fallbacks, ungeprüften Runtime-Downloads oder ungebundenen kritischen Artefakte.
- Build-, Cache-, Modell- und temporäre Artefakte gehören nicht ins Repository.

## Repository- und Merge-Pflicht je Iteration
Vor Beginn und nach Abschluss jeder Iteration werden real geprüft:
- aktueller `main`-Commit
- Arbeitszweig und Head-SHA
- zugehöriger Pull Request einschließlich Draft-/Mergezustand
- CI für den exakten Head-SHA
- offene Review-Threads
- veraltete Parallel-PRs oder widersprüchliche Stände
- nach Merge der resultierende `main`

Wenn Repository, PR, CI oder Dokumentation nicht synchron sind, wird zuerst diese Drift beseitigt.

## Merge-Konflikt- und Textintegritätsregeln
- Konflikte niemals durch blindes Aneinanderhängen beider Varianten lösen.
- Doppelte JSON-Schlüssel und Merge-Marker sind verboten.
- README, TODO und Projektstatus dürfen keine konkurrierenden Stände enthalten.
- Nach Merge muss der resultierende `main` erneut geprüft werden.

## Code- und Entwicklerdokumentationsregeln
- `CONTRIBUTING.md` ist der kurze Einstieg.
- `docs/ENTWICKLERDOKUMENTATION.md` ist die kanonische technische Übergabe.
- Codekommentare erklären nur schwer erkennbare Gründe und Invarianten; bevorzugter Marker: `ENTWICKLERHINWEIS`.
- Produktversion und `DB_VERSION` bleiben getrennte Verträge.
- README, TODO, CHANGELOG, `PROJEKTSTATUS.json`, Entwicklerdokumentation und relevante Tests werden bei jeder Iteration auf Aktualisierungsbedarf geprüft.

## Diagnose-, Logging- und Evidence-Regeln
- `diagnostics/DIAGNOSTICS_CONTRACT.json` ist der kanonische Maschinenvertrag.
- Fehlercodes werden niemals umgedeutet oder wiederverwendet; neue Bedeutung benötigt einen neuen Code.
- Runtime-Diagnosen speichern standardmäßig keine Audio-, Transkript-, Dokument-/Notiz-, Secret-, Token- oder vollständigen Benutzerpfaddaten.
- Der Ringpuffer enthält höchstens 200 bereits bereinigte Ereignisse.
- Identische Wiederholungen werden im definierten Zeitfenster dedupliziert und über `repeat_count` gezählt.
- `retry-once` ist maximal einmal pro Ereignis zulässig; keine automatische Retry-Endlosschleife.
- Diagnosefehler dürfen Produktfunktionen nicht zum Absturz bringen.
- `RELEASE_EVIDENCE.json` bindet den exakten Diagnosevertrag über SHA-256.

### Plattformübergreifende Diagnoseinvariante
Für 0.5.1-C/D gilt verbindlich:
- Diagnose-Contract-SHA-256: `fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425`
- Schema-Version: `1`
- Ereignisschema-Version: `1`
- Format: `NAQYA-DIAGNOSTICS`
- Linux und Windows verwenden bytegenau denselben `diagnostics/DIAGNOSTICS_CONTRACT.json`.
- Plattformports dürfen Adapter, Paketierung und Runtimeintegration erweitern, aber den Diagnosevertrag nicht still verändern.
- `NAQYA-STT-4002` bedeutet auf allen Plattformen unverändert „Live-STT-Segment konnte nicht transkribiert werden“.
- Eine legitime spätere Vertragsänderung benötigt einen eigenen expliziten Diagnosevertrags-Meilenstein, neue Evidence und bewusst aktualisierte Regressionstests; sie darf nicht als Nebenwirkung eines Plattformports erfolgen.
- `tests/validate_platform_diagnostics.py` ist die harte CI-Sperre gegen stille Contract-Drift.

## Qualitätsgate
Vor Merge sind je nach Änderungsumfang mindestens zu prüfen:
1. JSON-Struktur und Duplicate Keys
2. Text-/Merge-Integrität
3. JavaScript-Syntax
4. Diagnose-Laufzeitregression
5. `tests/validate_platform_diagnostics.py`
6. deterministisches Desktop-Staging
7. Rust-Formatierung und `cargo check`
8. statische Projektverträge
9. Sidecar-Build und Integrität
10. vollständiger Bundle-Test, sobald Bundlefähigkeit Ziel ist
11. reale Hardwareabnahme nur dann als erledigt markieren, wenn sie tatsächlich erfolgt ist

Fehlgeschlagene Gates werden ursachenbezogen korrigiert; fachfremde Umbauten werden nicht in denselben Fix gemischt.

## Sidecar- und Runtime-Regeln
- whisper.cpp bleibt auf Upstream `v1.9.2`, Commit `306c88f4d1286aec1bf96e544632897886af5501` gepinnt.
- Tauri bindet den Sidecar über `externalBin`.
- Gebündelter Sidecar hat Vorrang vor kontrolliertem externem Fallback.
- Ein gestarteter, aber fehlerhafter Sidecar darf nicht still durch PATH-Fallback ersetzt werden.
- Die tatsächlich verwendete Runtimequelle ist diagnostizierbar.
- Linux und Windows sind getrennte Bundle-/Hardware-Abnahmeziele, verwenden aber denselben Diagnosevertrag.

## Versions- und Freigaberegeln
- `main` enthält nur validierte Stände.
- Größere Schritte laufen über einen eigenen Zweig und Pull Request.
- PR bleibt Draft, solange die relevante Prüfung nicht vollständig grün ist.
- Merge bevorzugt als Squash mit erwarteter Head-SHA.
- Eine Iteration gilt erst als abgeschlossen, wenn Repository-, CI-, PR- und Dokumentationsstand übereinstimmen.

## Aktueller validierter Stand
**0.5.1-C – Diagnose, Logging & Evidence-Bindung**

Validiert auf Head `0388cda77c6696017c5b00cb795f5758af2d5e22`:
- Qualitätsprüfung #268 erfolgreich
- Linux-Bundle-Nachweis #14 erfolgreich
- fail-safe Diagnosemodul
- stabiler Fehlercode- und Ereignisvertrag
- Privacy-Redaction
- begrenzter Ringpuffer und Deduplizierung
- JSON-/TXT-Export und Safe Actions
- Release-Evidence-Bindung an Contract-SHA `fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425`

## Nächster Entwicklungsblock
**0.5.1-D – Windows-Bundle mit identischem Diagnosevertrag**

Reihenfolge:
1. Windows-x86_64-Sidecar aus demselben gepinnten Upstream bauen
2. Tauri-konformen `.exe`-Sidecar bundeln
3. Paket/Sidecar per SHA-256 nachweisen
4. Sidecar aus dem Paketkontext starten
5. Windows Release Evidence erzeugen
6. denselben Diagnose-Contract-SHA und dasselbe Ereignisschema nachweisen
7. erst danach Hardware-/Mikrofonabnahme fortsetzen
