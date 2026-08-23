# Hardware-Abnahme 0.5.1-E

`hardware/HARDWARE_ACCEPTANCE.schema.json` ist der maschinenlesbare Vertrag für reale Linux-/Windows-Abnahmen. Er ersetzt keine Messung und erzeugt keine Freigabe aus CI-Daten.

## Zweck

Eine Hardware-Abnahme gehört nur dann zum aktuell validierten Softwarestand, wenn `evidence_fingerprint` exakt dem Wert aus `PROJEKTSTATUS.json` entspricht. Dadurch bleiben Linux-/Windows-Paketunterschiede erlaubt, während Software-, whisper.cpp- und Diagnosevertrag identisch gebunden bleiben.

Erfasst werden mindestens Plattform/OS-Version, CPU/RAM, Mikrofon, Paket-SHA, Modell-SHA, geschützter Modellpfad, Sidecar-Nutzung, Mikrofon-/Live-Diktat-/Temp-WAV-Status, Testdauer, Segmentzahl/Segmentverlust, Echtzeitfaktor, Peak-RAM, Diagnosevertrag und beobachtete Fehlercodes.

## Profile

- `smoke`: kurze Funktionsprüfung; keine Langzeitfreigabe.
- `long30`: mindestens 1800 Sekunden reale Laufzeit.
- `long60`: mindestens 3600 Sekunden reale Laufzeit.

Ein `PASS` ist nur zulässig, wenn Paketinstallation und App-Start bestätigt sind, der gebündelte Sidecar tatsächlich verwendet wird, das Modell aus dem geschützten Pfad stammt, Mikrofonaufnahme/Live-Diktat/WAV-Bereinigung funktionieren und kein Segment verloren ging.

## E7 – Geführter Linux-Hardware-Smoke

Der kanonische Realtestpfad ist `tools/run_linux_hardware_smoke.py`. Der Assistent sammelt die vorhandenen E3–E6-Nachweise ein, fragt die sieben real beobachtbaren Pflichtpunkte einzeln ab und erzeugt nur dann `PASS`, wenn wirklich alle Bedingungen erfüllt sind.

Vor dem Realtest kann der Harness ohne Paket, Modell oder Messdateien geprüft werden:

```bash
python3 tools/run_linux_hardware_smoke.py --self-check
```

Erwartetes Ergebnis:

```text
E7 Linux hardware smoke harness: SELF-CHECK OK
```

Der Self-Check ist nur eine Voraussetzungsprüfung. Er ist **keine Hardwarefreigabe**.

## Runtime-Messadapter 0.5.1-E3

Die native Live-STT-Sitzung führt zusätzlich einen datensparsamen Runtime-Metrikvertrag in `audioSessions`. `nativeSttRuntimeMetrics` enthält ausschließlich technische Messwerte: Segmente gesamt/erfolgreich/verloren, erfasste und transkribierte Audiodauer, kumulierte native STT-Zeit sowie RTF Durchschnitt/Maximum. Fehlgeschlagene STT-Segmente werden sofort als verloren gezählt und mit dem Sitzungsstand persistiert. Die Metriken erzeugen selbst kein `PASS`.

Nach einem nativen Offline-Diktat kann die Datei direkt über den Button **„Laufzeit-Messwerte exportieren“** gespeichert werden. Der Export hat das Format `NAQYA-LIVE-STT-RUNTIME` und wird später als `--runtime-metrics` an den E7-Harness übergeben.

## Prozess-Ressourcenmessung 0.5.1-E4

`tools/measure_process_resources.py` misst Peak-RAM sowie CPU-Durchschnitt/-Maximum ohne zusätzliche Python-Pakete. Gemessen wird die gesamte Prozessfamilie des Zielprozesses, damit der von NAQYA gestartete whisper.cpp-Sidecar einbezogen werden kann.

Bereits laufende Anwendung:

```bash
python3 tools/measure_process_resources.py \
  --pid 12345 \
  --output RESOURCE_METRICS.json
```

Testprozess direkt starten und messen:

```bash
python3 tools/measure_process_resources.py \
  --output RESOURCE_METRICS.json \
  --command /pfad/zu/naqya
```

`RESOURCE_METRICS.json` enthält Peak-RAM, CPU Ø/Maximum, Messdauer, Messintervall, Prozesszahl und optional den Exit-Code des gestarteten Prozesses. Audio und Transkripte werden nicht gespeichert.

## Direkter Ressourcenimport 0.5.1-E5

Der Hardware-Collector kann die von E4 erzeugte Datei direkt mit `--resource-metrics` übernehmen. Damit wird Peak-RAM nicht mehr manuell abgeschrieben. Zusätzlich werden SHA-256 der Ressourcenmessung, Messdauer und CPU Ø/Maximum in `HARDWARE_ACCEPTANCE.json` übernommen.

Der Import ist fail-closed: unbekannte Schemaversionen, fehlende Pflichtfelder, nicht-positive Laufzeit/RAM-Werte, inkonsistente CPU-Werte oder ein fehlgeschlagener gestarteter Testprozess werden abgelehnt. `--resource-metrics` und der alte Fallback `--peak-ram-mb` schließen sich gegenseitig aus.

## Direkter Runtime-Import 0.5.1-E6

Der Collector akzeptiert `--runtime-metrics RUNTIME_METRICS.json`. Die Datei muss den E3-Vertrag `nativeSttRuntimeMetrics` enthalten; alternativ ist ein Envelope mit `format: "NAQYA-LIVE-STT-RUNTIME"`, `schemaVersion: 1` und dem Objekt unter `metrics` zulässig.

Aus der Runtime-Datei werden Testdauer, Segmente gesamt/erfolgreich/verloren und RTF Ø/Maximum direkt übernommen. Der Collector prüft zusätzlich Segmentbilanz, Audio-/STT-Zeiten und berechnet den RTF-Durchschnitt erneut aus `sttElapsedMs / transcribedAudioMs`. Stimmen die Werte nicht reproduzierbar zusammen, bricht der Import ab. Die Quelldatei wird per SHA-256 an `HARDWARE_ACCEPTANCE.json` gebunden.

Wenn `--runtime-metrics` verwendet wird, dürfen `--duration-seconds`, `--segments-total`, `--segments-lost`, `--realtime-factor-avg` und `--realtime-factor-max` nicht gleichzeitig angegeben werden. Der alte manuelle Weg bleibt nur als Fallback erhalten.

## Empfohlener realer Smoke-Ablauf

1. Self-Check ausführen.
2. Validiertes Linux-Paket installieren und NAQYA starten.
3. Lokales Modell aus dem geschützten NAQYA-Modellpfad verwenden.
4. Reales Mikrofon auswählen und natives Offline-Live-Diktat durchführen.
5. Über **„Laufzeit-Messwerte exportieren“** die `RUNTIME_METRICS.json` sichern.
6. Parallel oder als separaten Lauf `RESOURCE_METRICS.json` mit `measure_process_resources.py` erzeugen.
7. Erst danach den geführten E7-Harness starten.

Beispiel:

```bash
python3 tools/run_linux_hardware_smoke.py \
  --package /pfad/NAQYA_0.5.0_amd64.deb \
  --model /pfad/ggml-base.bin \
  --microphone "USB Audio Device" \
  --profile smoke \
  --runtime-metrics /pfad/RUNTIME_METRICS.json \
  --resource-metrics /pfad/RESOURCE_METRICS.json \
  --output /pfad/HARDWARE_ACCEPTANCE.json
```

Der Assistent fragt anschließend einzeln nach:

- installiertem Testpaket,
- erfolgreichem NAQYA-Start,
- tatsächlich verwendetem gebündeltem `naqya-whisper`,
- geschütztem Modellpfad,
- funktionierender Mikrofonaufnahme,
- funktionierendem Live-Diktat,
- erfolgreicher Temp-WAV-Bereinigung.

Die sichere Vorgabe jeder Frage ist `NEIN`. Unbestätigte Punkte führen zu `FAIL`. Der Assistent ruft danach automatisch den Hardware-Collector und den Validator auf.

## Manuelle Collector-Nutzung

`tools/collect_hardware_acceptance.py` bleibt als technischer Fallback verfügbar. Für normale E7-Abnahmen soll jedoch der geführte Harness verwendet werden, damit keine Pflichtbestätigung versehentlich fehlt und der Prüfpfad reproduzierbar bleibt.

## Prüfung

Schema-/Vertragsprüfung:

```bash
python3 tests/validate_hardware_acceptance.py --schema-only
```

Harness-Regression:

```bash
python3 tests/linux_hardware_smoke_harness.test.py
```

Collector-Regression:

```bash
python3 tests/hardware_collector.test.py
```

Ressourcenmesser-Regression:

```bash
python3 tests/resource_metrics.test.py
```

Realen Nachweis prüfen:

```bash
python3 tests/validate_hardware_acceptance.py /pfad/HARDWARE_ACCEPTANCE.json
```

Eine Hardwarefreigabe darf erst dokumentiert werden, nachdem ein echter Nachweis aus dem Referenzgerät vorliegt und der Validator ihn akzeptiert. Fehlende reale Messdaten bleiben ausdrücklich offen.
