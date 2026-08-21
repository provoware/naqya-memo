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

## Runtime-Messadapter 0.5.1-E3

Die native Live-STT-Sitzung führt zusätzlich einen datensparsamen Runtime-Metrikvertrag in `audioSessions`. `nativeSttRuntimeMetrics` enthält ausschließlich technische Messwerte: Segmente gesamt/erfolgreich/verloren, erfasste und transkribierte Audiodauer, kumulierte native STT-Zeit sowie RTF Durchschnitt/Maximum. Fehlgeschlagene STT-Segmente werden sofort als verloren gezählt und mit dem Sitzungsstand persistiert. Die Metriken erzeugen selbst kein `PASS`.

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

Der Hardware-Collector kann die von E4 erzeugte Datei jetzt direkt mit `--resource-metrics` übernehmen. Damit wird Peak-RAM nicht mehr manuell abgeschrieben. Zusätzlich werden SHA-256 der Ressourcenmessung, Messdauer und CPU Ø/Maximum in `HARDWARE_ACCEPTANCE.json` übernommen.

Der Import ist fail-closed: unbekannte Schemaversionen, fehlende Pflichtfelder, nicht-positive Laufzeit/RAM-Werte, inkonsistente CPU-Werte oder ein fehlgeschlagener gestarteter Testprozess werden abgelehnt. `--resource-metrics` und der alte Fallback `--peak-ram-mb` schließen sich gegenseitig aus.

Empfohlener realer Smoke-Ablauf:

```bash
python3 tools/measure_process_resources.py \
  --output RESOURCE_METRICS.json \
  --command /pfad/zu/naqya

python3 tools/collect_hardware_acceptance.py \
  --package /pfad/NAQYA_0.5.0_amd64.deb \
  --model /pfad/ggml-base.bin \
  --microphone "USB Audio Device" \
  --profile smoke \
  --duration-seconds 120 \
  --segments-total 30 \
  --segments-lost 0 \
  --realtime-factor-avg 0.41 \
  --realtime-factor-max 0.63 \
  --resource-metrics RESOURCE_METRICS.json \
  --installed \
  --application-started \
  --bundled-sidecar-used \
  --protected-model-path-used \
  --microphone-capture-ok \
  --live-dictation-ok \
  --temp-wav-cleanup-ok \
  --result PASS \
  --output HARDWARE_ACCEPTANCE.json
```

Der Collector bleibt bewusst fail-closed: Standardergebnis ist `FAIL`. Für `PASS` müssen alle realen Bestätigungen explizit gesetzt sein und `segments_lost` muss `0` sein. Segmentzahl/-verlust und RTF stammen seit E3 aus `nativeSttRuntimeMetrics`; Peak-RAM und CPU können seit E5 ohne manuelle Übertragung aus E4 importiert werden.

## Prüfung

Schema-/Vertragsprüfung:

```bash
python3 tests/validate_hardware_acceptance.py --schema-only
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
