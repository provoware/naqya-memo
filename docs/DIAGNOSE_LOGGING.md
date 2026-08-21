# Diagnose, Debugging & Logging – NAQYA 0.5.1-C

## Zweck

NAQYA protokolliert technische Ereignisse **offline und datensparsam**, damit Fehler für Laien verständlich und für Entwickler reproduzierbar bleiben. Der kanonische Maschinenvertrag liegt in `diagnostics/DIAGNOSTICS_CONTRACT.json`; diese Datei erklärt ihn für Menschen.

## Grundprinzip

Jedes Diagnoseereignis beantwortet dieselben Fragen:

- **Was** ist passiert?
- **Wann** ist es passiert?
- **Wo** im Programm ist es passiert?
- **Wie** kam es dazu beziehungsweise welcher Ablauf war aktiv?
- **Ergebnis**: Was ist der aktuelle Zustand?
- **Optionen**: Welche sicheren nächsten Aktionen sind zulässig?

Zusätzlich besitzt jedes Ereignis einen stabilen Fehler-/Ereigniscode, eine eindeutige `event_id`, eine `correlation_id` sowie optional eine `parent_event_id`.

## Codefamilien

| Bereich | Muster | Zweck |
|---|---|---|
| Anwendung | `NAQYA-APP-1xxx` | globale Programmfehler und Benutzeraktionen |
| Daten | `NAQYA-DATA-2xxx` | Datenhaltung und Migrationen |
| Audio | `NAQYA-AUDIO-3xxx` | Aufnahme und Recovery |
| STT | `NAQYA-STT-4xxx` | Live-Diktat und Segmenttranskription |
| Modell | `NAQYA-MODEL-5xxx` | Modellmaterialisierung und Integrität |
| Runtime | `NAQYA-RUNTIME-6xxx` | Tauri-/Sidecar-/Native-Bridge-Ebene |
| Bundle | `NAQYA-BUNDLE-7xxx` | Paket- und Bundleprüfungen |
| Release | `NAQYA-RELEASE-8xxx` | Release-/Evidence-Verträge |

Codes werden **nicht umgedeutet oder wiederverwendet**. Neue Bedeutungen erhalten neue Codes.

## Datenschutzvertrag

Der Diagnosepuffer darf standardmäßig keine Nutzinhalte enthalten. Insbesondere werden nicht gespeichert:

- Audioinhalte oder Base64-Audio
- Transkripte
- Dokument-/Notiztexte
- Binärblobs
- Passwörter, Tokens oder Secrets
- vollständige Benutzerpfade

Bekannte sensible Schlüssel werden durch `[REDACTED]` ersetzt. Vollständige Benutzerpfade werden auf `[pfad]/DATEINAME` reduziert. Freitext wird begrenzt. Der Puffer speichert ausschließlich bereits bereinigte Ereignisse.

## Speicher- und Regressionsverhalten

- maximal **200 Ereignisse** als Ringpuffer
- identische Fehler werden innerhalb von **5 Sekunden** dedupliziert und über `repeat_count` gezählt
- der Diagnosepfad darf selbst keine Produktfunktion zum Absturz bringen; Persistenzfehler werden fail-safe abgefangen
- keine automatische Endlosschleife bei Wiederholungsversuchen
- `retry-once` darf pro Ereignis höchstens **einmal** ausgeführt werden
- unbekannte Dialogaktionen werden nicht ausgeführt

## Laien-Dialog

Bei ausgewählten Fehlern öffnet NAQYA einen Dialog mit:

1. lesbarer Fehlerbeschreibung
2. stabilem NAQYA-Code
3. konkretem Ergebnis/Zustand
4. sicheren Handlungsoptionen
5. technischer Ereignis-ID für Support oder Entwickler

Zugelassene Aktionen kommen ausschließlich aus dem Diagnosevertrag:

- Schließen
- Einstellungen öffnen
- Diagnose als JSON exportieren
- Diagnose als Text exportieren
- einmaliger Wiederholungsversuch, nur wenn die aufrufende Funktion ausdrücklich einen sicheren Callback registriert

Der Diagnosebereich ist zusätzlich über **„🛠 Diagnose & Fehlercodes“** in der Seitenhilfe erreichbar.

## Maschinenlesbarer Export

JSON-Exporte verwenden:

```text
format = NAQYA-DIAGNOSTICS
schema_version = 1
```

Ein Export enthält den gebundenen Diagnosevertrag, Produktmetadaten und die bereinigten Ereignisse. Interne Deduplizierungsschlüssel werden nicht exportiert.

## Bindung an RELEASE_EVIDENCE.json

Der Linux-Release-Nachweis enthält künftig:

- Pfad des Diagnosevertrags
- Vertragsschema
- Ereignisschema
- Formatkennung
- SHA-256 des exakten `DIAGNOSTICS_CONTRACT.json`

Die Runtime lädt denselben Vertrag lokal aus dem gebündelten Frontend und berechnet dessen SHA-256. Dadurch kann ein Diagnoseexport mit demselben Contract-SHA einem konkreten Release-Nachweis zugeordnet werden.

Die Nachweiskette lautet damit:

```text
Git-Commit
  → Desktop-Paket / Paket-SHA
  → Sidecar / Sidecar-SHA
  → Diagnosevertrag / Contract-SHA
  → Runtime-Ereignis / event_id + correlation_id
  → sichere Benutzeraktion / parent_event_id
```

Ein Build-Nachweis enthält naturgemäß noch keine späteren Laufzeit-Ereignis-IDs. Er bindet stattdessen den exakten Vertrag, unter dem diese IDs später entstehen.

## Relevante Dateien

- `diagnostics/DIAGNOSTICS_CONTRACT.json` – kanonischer Maschinenvertrag
- `services/diagnostics.js` – Runtime, Ringpuffer, Redaction, Dialog, Export
- `services/native-bridge.js` – native Fehlercodes
- `services/live-stt.js` – STT-Fehlercodes
- `tools/generate_release_evidence.py` – Release↔Diagnose-Bindung
- `release/RELEASE_EVIDENCE.schema.json` – Release-Evidence-Schema
- `tests/diagnostics_runtime.test.js` – echter Laufzeit-Regressionslauf
- `tests/validate_diagnostics.py` – statischer Vertragscheck

## Änderungspflicht

Bei Änderungen an Codes, Privacy-Regeln, Safe Actions oder Ereignisschema müssen mindestens Diagnosevertrag, Runtime, Tests, diese Dokumentation und – sofern die Bindungsstruktur betroffen ist – Release-Evidence-Schema/Generator gemeinsam angepasst werden.
