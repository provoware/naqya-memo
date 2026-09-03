# Provoware Naqya Memo Tool 2026 – v0.3.16

Dieser Ordner enthält den **vollständigen lokal validierten Release-Bestand** mit `54` Dateien.

- Version: `0.3.16`
- Status: `KANDIDAT`
- Lokales Release-Gate: `219 PASS · 0 WARN · 0 FAIL`
- Entwicklerdokumentation/Logs: **nicht Bestandteil des Release-Bestands**

## Reproduzierbarer GitHub-Transport

Wegen einer Binärtransport-Grenze der verwendeten GitHub-Schnittstelle liegt der Bestand im Repo als geordnet segmentiertes Base64 eines kanonischen `tar.xz` vor. Die CI rekonstruiert daraus bitgenau das Archiv und prüft anschließend **jede der 54 Dateien** gegen `RELEASE_INDEX_FERTIG_v0.3.16.json`.

- kanonisches Archiv: `77.052` Byte
- SHA-256: `65705a2254744cd0df4793f48029e851282767d5a8f593dfdb579b9d69e80af2`
- Base64-Gesamtlänge: `102.736` Zeichen
- Segmente: `24`

Der ursprünglich lokal erzeugte Release-ZIP bleibt als Herkunftsnachweis im Index dokumentiert:
`5bcf7372454787af12ff85c760faee9f796b7c415ea4ece71f9aa1130bb289f1`

Der Status bleibt `KANDIDAT`, bis das **separate** PRE-AUTOSAVE-Cross-Platform-Gate abgeschlossen ist.
