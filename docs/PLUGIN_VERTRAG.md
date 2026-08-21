# Plugin-Vertrag – Planungsstand

> **Dokumentenstatus:** Architekturidee, noch nicht als aktive Fremdplugin-Schnittstelle implementiert. Dieser Status gilt weiterhin für NAQYA 0.5.0.

Die Plugin-API wird bislang nur als zukünftiger Architekturvertrag geführt. Aktiv ladbare Fremdplugins dürfen erst nach Stabilisierung des Kerns und eines belastbaren Berechtigungsmodells eingeführt werden.

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

Grundregel: minimale Rechte, keine implizite Vollfreigabe und keine Plugin-Ausführung ohne expliziten Vertrauens- und Berechtigungsvertrag.
