# PROVOWARE – Globale Toolstandards V1.0

Status: **AKTIV**

## Ausgabe
- Standardausgabe ist nur ein vollständiges, lauffähiges Basisprojekt.
- Keine Patch-Dateien, Logs, CI-Artefakte, Caches, temporären Dateien oder Einmal-Skripte in der Nutzerausgabe.
- Jedes Basisprojekt enthält `BASISPROJEKT_MANIFEST.json` mit SHA-256 je Datei.
- Programmdateien und Nutzerdaten/Runtime-Daten bleiben strikt getrennt.

## Pflichtdateien
- `SCHNELLSTART.sh`: Vorprüfung, sicherer Start und automatisches Öffnen der Oberfläche.
- `requirements.txt`: alle externen Python-Runtime-Abhängigkeiten exakt mit `==`; keine erfundenen Pakete.
- Maschinenlesbares Basisprojekt-Manifest mit Include-/Exclude-Regeln.

## Erscheinungsbild
- Dunkle, klare Hierarchie; Neon-Türkis, Leucht-Lila und Knallgelb nur als kontrollierte Markenakzente.
- Hoher Kontrast, sichtbarer Tastaturfokus, große Klickziele und 100–200 % Zoom.
- Kein horizontaler Überlauf; Status niemals nur durch Farbe vermitteln.
- Keine unnötigen Glows, Doppelinformationen, Textwüsten oder permanent sichtbaren Entwicklerdetails.
- Kernfunktionen mit möglichst 1–2 Aktionen erreichbar.

## Fehlerhandling und Fehlerprävention
- Fehler nach Möglichkeit verhindern, bevor Mutationen beginnen: Eingaben, Pfade, Rechte, Speicherplatz, Dateityp, Größe und Prozessidentität prüfen.
- Stabile Fehlercodes plus einfache deutsche Handlungsempfehlung.
- Keine rohen Exceptions, Stacktraces, Tokens oder privaten absoluten Pfade in der Nutzeroberfläche.
- Keine stillen relevanten `except: pass`-Pfade.
- Schreibvorgänge atomar oder mit eindeutigem Recovery-/Rollback-Pfad.
- Idempotenter Start, Port-/Prozessidentität, Timeouts, Concurrency-Guard und sicherer eingeschränkter Modus.
- Nutzerdaten niemals wegen UI-/Startfehlern löschen oder überschreiben.

## Release
- Kleine, ursachengerechte Slices.
- Manifest nach Codeänderungen neu erzeugen.
- Regressionstest für jeden relevanten behobenen Fehler.
- Freigabe nur mit Evidence auf exakt demselben Git-SHA und vollständigem finalem Diff-Audit.
- Codex für GitHub-Code-Reviews niemals ohne ausdrückliche Nutzeranweisung verwenden.
- Release-Freeze bedeutet: keine neue Produktfunktion außerhalb des freigegebenen Scopes.
