# Android Device Acceptance V0.12.2

## Voraussetzungen
- Android SDK 35
- Gradle/Android Studio
- ADB
- genau ein autorisiertes Gerät
- gebautes V0.12.2 APK

## Build
```bash
./platform/android/BUILD_ANDROID.sh
```

## Device Gate
```bash
export PROVOWARE_ANDROID_ACCEPTANCE_APK=/pfad/app-debug.apk
export PROVOWARE_ANDROID_RELEASE_APK=/pfad/app-release-signiert.apk
python3 -S tools/release_gate/gate_06_android_device.py
```

Der Gate-Runner prüft nicht nur Installation. Er startet einen eingebauten Acceptance-Modus und verlangt:
- V0.12.2 APK,
- RECORD_AUDIO,
- POST_NOTIFICATIONS auf Android 13+,
- echte MediaRecorder-Aufnahme,
- echten AlarmManager→BroadcastReceiver-Reminder,
- Memo/Todo/Termin Mobile-Core-Lauf,
- Prozess-Neustart,
- Persistenz von Memo + Audio nach Neustart.

Erst dann wird Gate 06 `PASS`.

## Sicherheitsregel
Der Acceptance-Modus wird nur von einem **debuggable Debug-/Acceptance-Build** akzeptiert. In `MainActivity` wird `provoware_acceptance` nur ausgewertet, wenn `ApplicationInfo.FLAG_DEBUGGABLE` aktiv ist. Das verhindert einen Acceptance-Test-Backdoor im normalen Release.

Das Gate installiert deshalb zuerst das Acceptance-APK für Mikrofon/Reminder/Persistenz-Evidence, deinstalliert es anschließend und installiert danach **separat das signierte, nicht-debuggable Release-APK**. Erst wenn auch das Release startet und Version `0.12.2` meldet, kann Gate 06 PASS werden.
