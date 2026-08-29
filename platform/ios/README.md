# iOS Runtime V0.12.2

**Status: XCODE_RUNTIME_SOURCE_COMPLETE / BUILD + SIGNING + DEVICE EVIDENCE PENDING.**

Enthalten:
- echtes Xcode-App-Target,
- WKWebView mit gebündelter UI und persistenter Mobile-Runtime,
- AVAudioRecorder-Brücke mit Systemfreigabe,
- UNUserNotificationCenter für Reminder,
- UIActivityViewController für Teilen,
- Datei-Upload über WKWebView-Dateiauswahl,
- iOS Deployment Target 16.0, passend für den späteren iPhone-X/iOS-16.7.x-Gate.

Ein Linux-Runner kann dieses iOS-App-Target weder gegen das iOS SDK linken noch signieren. Der Quellcode ist daher **kein Device-PASS**. Der Release-Gate bleibt bis zu Xcode-Build und realem iPhone-X-Test BLOCKED.

Historischer V0.11-Status: `BUILD_CONCEPT_ONLY` — in V0.12.2 durch ein echtes Xcode-App-Target ersetzt.
