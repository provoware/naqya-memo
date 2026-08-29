# Mobile-Paritätsmatrix V0.12.2

| Fachbereich | Desktop | Android/iOS Runtime Source | Status |
|---|---|---|---|
| Memo | SQLite Domain | IndexedDB Domain | 🟢 Parity-Test |
| Todo | SQLite Domain | IndexedDB Domain | 🟢 Parity-Test |
| Kalender | SQLite Domain | IndexedDB Domain | 🟢 Parity-Test |
| Revision | ja | ja | 🟢 |
| Undo/Redo | persistent | persistent | 🟢 |
| Papierkorb | ja | ja | 🟢 |
| Profile | Backend | Mobile PIN-Gate | 🟢 Source |
| 4-stelliger PIN | PBKDF2 | PBKDF2-SHA256 | 🟢 Source |
| Theme/Schrift/Hilfe | persistent | profilbezogen persistent | 🟢 Source |
| Reminder | Linux Adapter | Android/iOS Native Bridge | 🟢 Source / 🟡 Device offen |
| Sprachmemo | FFmpeg Linux | MediaRecorder / AVAudioRecorder | 🟢 Source / 🟡 Device offen |
| PDF/TXT/MD | AssetManager | IndexedDB Blob + Viewer/Editor | 🟢 Source |
| Assets | SHA-256 | SHA-256 | 🟢 |
| Share | xdg-email/Share | Intent / ActivityViewController | 🟢 Source |
| Diagnose-Privacy | ja | ja | 🟢 |
| Strukturierte 4er-Backups | ja | bis 4 Generationen | 🟢 strukturiert |
| Binär-Asset-Redundanz über 4 Generationen | Datei-Backup | 4 vollständige Binärkopien pro Profil, SHA-256-validiert, Restore getestet | 🟢 SOURCE/CONTRACT PASS |
| APK Build | – | Android SDK nötig | 🟡 BLOCKED |
| iOS Build/Signing | – | Xcode/macOS nötig | 🟡 BLOCKED |
| echtes Android Gerät | – | Gate 06 | 🟡 BLOCKED |
| iPhone X / iOS 16.7.16 | – | Gate 07 | 🟡 BLOCKED |

## P0 vor V1.0 Multi-Platform GO
1. Android APK bauen und Gate 06 durchlaufen.
2. Xcode-Build/signiertes `.app` erzeugen und Gate 07 auf echtem iPhone X / iOS 16.7.16 durchlaufen.
3. Binär-Asset-Backupstrategie ist source-/contract-seitig geschlossen; echte Geräte-Quota-/Storage-Evidence bleibt Teil von Gate 06/07.
