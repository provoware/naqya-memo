# Android Runtime V0.12.2

**Status: RUNTIME_SOURCE_COMPLETE / NATIVE BUILD + DEVICE EVIDENCE PENDING.**

Die bisherige leere Shell wurde durch eine echte WebView-Laufzeit ersetzt:
- gebündelte responsive UI,
- mobile IndexedDB-Daten-/Undo-/Asset-Schicht,
- nativer Android-JS-Bridge,
- RECORD_AUDIO mit `MediaRecorder`,
- System-Dateiauswahl,
- Share-Sheet,
- lokale Reminder via `AlarmManager` + `NotificationManager`,
- kein Klartext-Netzwerk nötig.

## Release-Gate
Ein APK-Build mit Android SDK 35 und ein reales Gerät bleiben zwingend. Erst dort dürfen `RECORD_AUDIO`, `POST_NOTIFICATIONS`, Lifecycle, Upgrade und Hintergrundverhalten auf PASS gesetzt werden.

Historischer V0.11-Status: `BUILD_STRUCTURE_ONLY` — in V0.12.2 durch die echte Runtime-Quelle ersetzt.

## Build und Device-Acceptance
`BUILD_ANDROID.sh` baut absichtlich zwei Artefakte:
- Debug/Acceptance APK: darf den internen Acceptance-Harness starten.
- signiertes Release APK: `isDebuggable=false`; Acceptance-Intent wird ignoriert.

Für ein echtes Gate:
```bash
export PROVOWARE_ANDROID_KEYSTORE=/pfad/release.keystore
export PROVOWARE_ANDROID_KEY_ALIAS=...
export PROVOWARE_ANDROID_STORE_PASSWORD=...
export PROVOWARE_ANDROID_KEY_PASSWORD=...
./platform/android/BUILD_ANDROID.sh

export PROVOWARE_ANDROID_ACCEPTANCE_APK=/pfad/app-debug.apk
export PROVOWARE_ANDROID_RELEASE_APK=/pfad/app-release.apk
python3 -S tools/release_gate/gate_06_android_device.py
```

**PASS erfordert beides:** reale Acceptance-Evidence auf einem Android-Gerät und danach Installation/Start des signierten nicht-debuggable Release-APKs.
