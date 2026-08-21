# Plugin-Vertrag – Vorstufe

Die Plugin-API wird in 0.1.0 nur als Architekturvertrag geführt. Aktiv ladbare Fremdplugins folgen nach Stabilisierung des Kerns.

## Geplantes Manifest

```json
{
  "id": "beispiel.plugin",
  "name": "Beispiel",
  "version": "1.0.0",
  "apiVersion": 1,
  "permissions": ["dokumente:lesen"],
  "entrypoints": ["dashboard-kachel"]
}
```

## Geplante Berechtigungen
- kalender:lesen/schreiben
- dokumente:lesen/schreiben
- audio:lesen/schreiben
- kamera
- mikrofon
- benachrichtigungen
- netzwerk

Standard: minimale Rechte, keine implizite Vollfreigabe.
