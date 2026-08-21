# Architektur 0.1.0

## Prinzipien

1. offline-first
2. lokale Datenhoheit
3. keine Cloudpflicht
4. UI, Domänenlogik und Plattformdienste getrennt
5. Feature-Erkennung statt versteckter Online-Fallbacks
6. progressive Erweiterung Richtung Tauri/Capacitor + whisper.cpp

## Ebenen

- UI: `index.html`, `styles.css`
- Anwendungslogik: `app.js`
- Persistenz: IndexedDB-Adapter
- Dateispeicher: Blob-Store in IndexedDB (PWA-Prototyp)
- Offline-Cache: `sw.js`
- Plattformstart: `START_NAQYA.sh`, `START_NAQYA.bat`

## Nächste Zielarchitektur

- gemeinsamer TypeScript-Domänenkern
- SQLite für native Desktop/Mobil-Pakete
- IndexedDB nur für PWA
- AudioDienst, VADDienst, SpracheZuTextDienst, TranskriptDienst, SprachmodellDienst
- whisper.cpp native Bridge für Linux/Windows/iOS/Android
- vollständiges Backupformat mit Binärdateien und SHA-256-Manifest
