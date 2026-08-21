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

## Evidence-Collector

`tools/collect_hardware_acceptance.py` erzeugt den Nachweis aus real gemessenen Werten. Er arbeitet ohne zusätzliche Python-Abhängigkeiten und ermittelt Betriebssystem, x86_64-Architektur, CPU, Gesamtspeicher sowie SHA-256 von Paket und Modell selbst. Evidence-Fingerprint und Diagnosevertrag werden direkt gegen den aktuellen Repository-Stand gebunden.

Der Collector erfindet keine Freigabe: Standardergebnis ist `FAIL`. Für `PASS` müssen alle sicherheitsrelevanten Bestätigungen explizit gesetzt sein und `segments_lost` muss `0` sein.

Beispiel für einen realen Smoke-Test:

```bash
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
  --peak-ram-mb 512 \
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

Die Messwerte `duration-seconds`, `segments-*`, `realtime-factor-*` und `peak-ram-mb` müssen aus dem realen Test stammen. Der Collector misst diese Werte bewusst nicht im Hintergrund und ersetzt damit keinen Endgerätetest.

## Prüfung

Schema-/Vertragsprüfung ohne erfundene Messdaten:

```bash
python3 tests/validate_hardware_acceptance.py --schema-only
```

Collector-Regression:

```bash
python3 tests/hardware_collector.test.py
```

Realen Nachweis prüfen:

```bash
python3 tests/validate_hardware_acceptance.py /pfad/HARDWARE_ACCEPTANCE.json
```

Eine Hardwarefreigabe darf erst dokumentiert werden, nachdem ein echter Nachweis aus dem Referenzgerät vorliegt und der Validator ihn akzeptiert. Fehlende reale Messdaten bleiben ausdrücklich offen.
