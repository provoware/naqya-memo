# 🔎 NEUANALYSE — ERGÄNZUNGEN NACH V0.1

Nach vollständiger Gegenprüfung wurden folgende zusätzliche Schutzpunkte aufgenommen bzw. für die nächste Planung markiert:

1. **Daten-Exportformat als offener Vertrag** – verhindert Hersteller-/Tool-Lock-in.
2. **Konfliktstrategie bei Importen** – gleiche ID, verschiedene Revisionen niemals still überschreiben.
3. **PIN-Recovery** – da keine Verschlüsselung, muss Profilzugang kontrolliert zurücksetzbar sein.
4. **Mobile Lifecycle Recovery** – App kann jederzeit vom OS beendet werden; jeder Use Case muss unterbrechbar sein.
5. **Notification Health** – prüfen, ob Benachrichtigungsrecht/Kanal/OS-Energiesparen Reminder blockiert.
6. **Monotone Operationszeit** – Dauer- und Timeoutmessung nicht nur über verstellbare Systemuhr.
7. **Anhangs-Limits und Quoten** – große Audios/PDFs dürfen Speicher und Backup nicht unkontrolliert aufblasen.
8. **Storage Quota Dashboard** – Daten, Anhänge, Backups und Papierkorb getrennt anzeigen.
9. **Retention-Policy** – Papierkorb, Logs und Diagnoseberichte brauchen klare Aufbewahrung.
10. **Log Rotation** – Debugdateien dürfen Datenträger nicht langsam füllen.
11. **Schema-Migration im Dry-Run** – vor echter Migration anzeigen, was geändert wird.
12. **Feature Flags** – unfertige Module sicher deaktivierbar halten.
13. **Capability Matrix je Gerät** – nicht nur OS, sondern echte verfügbare Funktionen erkennen.
14. **Safe Mode** – Start ohne Plugins, Index, Audio oder optionale Module zur Reparatur.
15. **Quarantäne für beschädigte Daten** – defekte Datensätze isolieren statt Gesamtstart blockieren.
16. **Index rebuildable by design** – Suchindex nie einzige Quelle der Wahrheit.
17. **Canonical Text Store** – ausgelagerte UI-Texte besitzen Schlüssel, Schema und Version.
18. **Theme Contrast Validator** – jedes Theme automatisiert gegen Kontrastregeln testen.
19. **Focus Recovery** – nach Dialog/Fehler muss Fokus logisch zurückkehren.
20. **Undo-Grenzen sichtbar machen** – Nutzer muss wissen, wann Rückgängig nicht mehr möglich ist.
21. **Automatischer Pre-Release Restore-Test** – Release gesperrt, wenn Restore scheitert.
22. **Support-Paket-ID** – Diagnoseberichte erhalten eindeutige ID ohne unnötige persönliche Daten.
23. **Dependency Failure Mode** – fehlende optionale Abhängigkeit deaktiviert nur das betroffene Modul.
24. **Plugin-API-Versionierung** – spätere Erweiterungen dürfen Kernschema nicht ungeprüft verändern.
25. **Datums-/Termin-Fuzzing** – Monatsende, Schaltjahr, DST, Zeitzonenwechsel automatisch testen.
