# STT-Providervertrag

NAQYA verwendet einen gemeinsamen, plattformneutralen STT-Vertrag. `services/stt-core.js` ist die kanonische JavaScript-Schicht zwischen Audio-/Diktatlogik und der jeweiligen lokalen Laufzeit.

## Vertrag

- Format: `NAQYA-STT-PROVIDER`
- Schema: `1`
- Ergebnis-Schema: `1`
- gemeinsamer nativer Engine-Kern: `whisper.cpp`
- kein Cloud-Fallback

## Adapter

| Adapter | Plattform | Transport | Stand |
| --- | --- | --- | --- |
| `browser-on-device` | Browser/PWA | lokale Web-Speech-API | implementiert, feature-detect |
| `desktop-whisper-cpp` | Linux, Windows | Tauri-Sidecar | implementiert |
| `android-whisper-cpp` | Android | JNI/NDK | Schnittstelle vorbereitet, nicht implementiert |
| `ios-whisper-cpp` | iPhone/iPad | Swift-native Bridge | Schnittstelle vorbereitet, nicht implementiert |

Die mobilen Adapter sind absichtlich fail-closed. `implemented: false` und `available: false` verhindern, dass eine vorbereitete Schnittstelle bereits als funktionsfähige mobile STT-Laufzeit erscheint.

## Kompatibilität

Die bestehenden Felder `providers().browserOnDevice` und `providers().nativeWhisper` bleiben erhalten. Bestehende Desktop-Aufrufer können `transcribeNative()` unverändert verwenden. Neue Plattformlogik kann `adapterForPlatform()` und `transcribeWithAdapter()` verwenden.

## Architekturregel

Audioaufnahme, Modellverwaltung und UI dürfen keine plattformspezifischen whisper.cpp-Prozessdetails voraussetzen. Desktop darf einen Sidecar verwenden; Android und iOS/iPadOS sollen denselben fachlichen STT-Vertrag später über native Bibliotheksadapter erfüllen.

## Prüfung

```bash
node --check services/stt-core.js
node --check tests/stt_provider_contract.test.js
node tests/stt_provider_contract.test.js
```

Der Regressionstest prüft insbesondere Desktop-Rückwärtskompatibilität, Plattformauflösung sowie das fail-closed Verhalten der mobilen Stubs.
