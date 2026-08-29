# V0.12.1 – RELEASE-GATE CLOSURE – GO/NO-GO DASHBOARD

**Build:** `0.12.1-RELEASE-GATE-CLOSURE`  
**Feature Freeze:** AKTIV  
**Release-Status:** **NO-GO**  
**V1.0-RC erlaubt:** **NEIN**  
**Echte Release-Gates:** **1/7 PASS**

## Gate-Status

| Gate | Status | Evidence / Bedeutung |
|---|---|---|
| `GATE_01_8H_SOAK` | **PRECHECK_PASS** | 5.02 s Preflight, 414 Operationen, Integrity=ok – voller 8h-Lauf fehlt |
| `GATE_02_CHROMIUM` | **BLOCKED** | Chromium headless timed out in this execution environment |
| `GATE_03_FIREFOX` | **BLOCKED** | Firefox executable is not installed in this runner. |
| `GATE_04_LINUX_MICROPHONE` | **BLOCKED** | No ALSA/Pulse microphone device/socket is exposed to this runner; physical microphone cannot be evidenced. |
| `GATE_05_STORAGE_FAILURE` | **PASS** | Linux-Kernel ENOSPC über /dev/full + echtes read-only EROFS + V0.12 App-Recovery-Matrix |
| `GATE_06_ANDROID_DEVICE` | **BLOCKED** | ADB is not installed in this runner. |
| `GATE_07_IOS_IPHONE_X` | **BLOCKED** | Native iOS build/sign/install requires macOS/Xcode; current runner is not macOS. |

## Release-Regel

Nur `PASS` zählt. `BLOCKED`, `PRECHECK_PASS`, `CONTRACT_ONLY`, `NOT_RUN` und synthetische Evidence schließen kein Release-Gate.

## Wichtiger Befund – Mobile Delivery

Android ist im aktuellen Projekt **BUILD_STRUCTURE_ONLY**; iOS ist **BUILD_CONCEPT_ONLY**. Das bedeutet: Die offenen Mobile-Gates sind nicht nur fehlende Geräte-Tests. Es fehlen noch echte produktfähige native Release-Artefakte. Ein V1.0 für **Linux + Android + iOS** darf daher nicht allein durch das Anschließen von Geräten freigegeben werden.

## Exakte nächste Ausführung

1. Auf dem echten Linux-Zielsystem `./RUN_8H_SOAK_ONLY.sh` vollständig 8 Stunden laufen lassen.
2. Chromium-Gate und Firefox-Gate auf einem uneingeschränkten Browser-Runner ausführen.
3. Linux-Mikrofon-Gate mit realem Aufnahmegerät ausführen.
4. Android: erst echte APK erzeugen, dann `PROVOWARE_ANDROID_APK=/pfad/app.apk python3 -S tools/release_gate/gate_06_android_device.py`.
5. iOS: auf macOS/Xcode signiertes `.app` bereitstellen und physisches iPhone X / iOS 16.7.x testen.
6. Danach `python3 -S tools/release_gate/evaluate_release_gate.py` ausführen. Nur 7/7 erzeugt `GO`.
