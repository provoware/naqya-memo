# Mobile Runtime Architektur – V0.12.2

## Ziel
Die bisherige Android-`BUILD_STRUCTURE_ONLY`- und iOS-`BUILD_CONCEPT_ONLY`-Stufe wird durch echte ausführbare App-Quellen ersetzt. Der Feature-Freeze bleibt aktiv; erlaubt ist ausschließlich Plattform-Parität.

## Gemeinsamer Präsentations-Layer
`ui/reference_web/` bleibt die gemeinsame responsive Oberfläche.

Desktop:
`Web UI → localhost API → Python Domain → Mutation Queue → SQLite/Assets`

Android/iOS:
`Web UI → Mobile API Adapter → IndexedDB Domain Runtime → Native Bridge → OS-Dienste`

## Mobile Domain Runtime
`mobile/mobile_core.js` implementiert die für die aktuelle UI erforderlichen Verträge:
- Memo / Todo / Kalender / Papierkorb,
- Revisionen und Checksummen,
- persistentes Undo/Redo,
- fünf Kalenderfarben + Tagesfärbung,
- Profile mit 4-stelligem PIN,
- PBKDF2-SHA256 PIN-Hash, kein Klartext-PIN,
- erneute PIN-Abfrage pro App-Session,
- profilgetrennte Entities, Assets und Einstellungen,
- IndexedDB-Persistenz,
- Asset-SHA-256, Quota, Dokumentrevisionen,
- Reminder-Verträge,
- Sprachaufnahme über native Bridge,
- Diagnose-Privacy-Vertrag,
- bis zu vier strukturierte Backup-Generationen.

**Wichtig:** PIN ist weiterhin nur Zugangssperre, keine Datenverschlüsselung.

## Native Bridge
Gemeinsame Bridge-Aktionen:
- `platformInfo`
- `shareText`
- `scheduleReminder`
- `cancelReminder`
- `audioStart`
- `audioStop`
- `acceptanceResult`

### Android
- `WebView`
- `MediaRecorder`
- System-Dateiauswahl
- `AlarmManager` + `NotificationManager`
- Share Intent
- Runtime Permissions

### iOS
- `WKWebView`
- `AVAudioRecorder`
- `UNUserNotificationCenter`
- `UIActivityViewController`
- App-Bundle-WebAssets
- Deployment Target iOS 16.0

## Drift-Schutz
Python/SQLite und Mobile/IndexedDB sind zwei Implementierungen desselben fachlichen Vertrags. Deshalb ist `tests/mobile/test_cross_runtime_parity.py` ab V0.12.2 Pflicht-Gate.

## Noch keine Release-Evidence
Quellcode-/Contract-PASS ist kein APK-/iPhone-PASS. Android SDK/ADB sowie macOS/Xcode/physisches iPhone fehlen im aktuellen Runner. Release bleibt NO-GO.
