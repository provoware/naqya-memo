# iPhone X / iOS 16.7.16 Acceptance V0.12.2

## Voraussetzungen
- macOS
- Xcode
- gültige Signierung
- echtes iPhone X
- iOS 16.7.16 als Standardziel; Abweichung nur nach bewusster Gate-Änderung

## Build
```bash
export PROVOWARE_DEVELOPMENT_TEAM=XXXXXXXXXX
./platform/ios/BUILD_IOS.sh
```

## Device Gate
```bash
export PROVOWARE_IOS_APP=/pfad/OIProvowareIO.app
export PROVOWARE_IOS_DEVICE_ID=<UDID>
export PROVOWARE_IOS_REQUIRED_VERSION=16.7.16
python3 -S tools/release_gate/gate_07_ios_iphone_x.py
```

Der App-Acceptance-Modus prüft:
- WKWebView Mobile Runtime,
- PIN-/Persistenzpfad,
- AVAudioRecorder-Aufnahme,
- UNUserNotificationCenter Reminder,
- Memo/Todo/Termin,
- Persistenz nach Relaunch.

System-Permission-Prompts müssen auf dem Gerät aktiv bestätigt werden. Ohne echten Device-Nachweis bleibt Gate 07 `BLOCKED`.
