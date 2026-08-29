# 📱 PLATTFORM-ADAPTER — STATUS: ENTWURF — V0.1

## Adapter
- FileSystemAdapter
- NotificationAdapter
- ShareAdapter
- PermissionsAdapter
- LifecycleAdapter
- ClipboardAdapter
- OpenInEditorAdapter
- AudioCaptureAdapter
- DisplayCapabilityAdapter
- SecureStorageAdapter (nur für appinterne Metadaten/Secrets)
- Power/BatteryPolicyAdapter

## Android
Scoped Storage, Runtime Permissions, Benachrichtigungskanäle, Hintergrundbeschränkungen beachten.

## Linux
Projektordnerfreiheit höher; Standardeditor, Desktop-Notifications, Dateirechte und Mount-Zustände prüfen.

## iOS
Sandbox, Document Picker, Share Sheet, Notification Framework und restriktive Hintergrundausführung berücksichtigen.
Self-Repair darf dort nur innerhalb des App-Sandboxes und erlaubter APIs arbeiten.
