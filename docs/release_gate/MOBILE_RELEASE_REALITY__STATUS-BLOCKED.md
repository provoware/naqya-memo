# Mobile Release Reality – V0.12.1

## Android
Der aktuelle Repository-Stand enthält eine **BUILD_STRUCTURE_ONLY** Android-Shell. Es existiert im Release kein nachgewiesenes produktfähiges APK. Ein Gerät allein kann das Gate daher nicht schließen. Gate 06 verlangt nun ausdrücklich:
1. gebaute APK-Datei,
2. ADB + genau ein autorisiertes Gerät,
3. Installation,
4. Start der MainActivity,
5. RECORD_AUDIO-Permission,
6. POST_NOTIFICATIONS-Permission auf Android 13+.

Dies ist nur ein Packaging-/Permission-Smoke. Für einen vollständigen mobilen Produkt-Release muss außerdem die echte Memo-/Todo-/Kalender-/Asset-Laufzeit auf Android vorhanden sein.

## iOS
Der aktuelle Stand ist **BUILD_CONCEPT_ONLY**. Ohne macOS/Xcode, signiertes `.app` und reales iPhone X/iOS 16.7.x ist kein Native-PASS zulässig.

## Konsequenz für Feature Freeze
Das sind keine Testlücken allein, sondern teilweise **fehlende native Release-Artefakte**. Wenn V1.0 zwingend Linux + Android + iOS gleichzeitig umfassen soll, kann V0.12.1 nicht allein durch Tests auf GO wechseln. Dann ist eine gezielte Mobile-Runtime-Fertigstellung nötig, obwohl der Feature-Freeze ansonsten bestehen bleibt.
