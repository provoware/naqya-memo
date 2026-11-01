# Sicherheits- und Bedienprüfung vom 01.11.2026

## Ausgang und Umfang
Basis: main@9b1dbab0442058bb819ab9152b9ddef17590f8d5. Freigegebener Auftrag: Pfadbegrenzung, ehrlicher Sicherungsstatus, deutsche Beschriftungen und 800x600-Vergleich bei 100/150/200 Prozent. Keine neue Fachfunktion und keine Datenmigration.

## Änderungen und Nachweise
- `app/runtime_safety.py`: Pfadgrenze einschließlich URL-kodierter Eingaben und externer Symlinks; gültige Oberfläche und Querystrings weiterhin zugänglich. HTTP GET/HEAD liefern bei Ausbruchsversuchen 403.
- Bekannte Datenbank- und Projektgenerationen werden über vorhandene Integritätsvalidatoren geprüft. Projektsicherungen verlangen alle Medien und Restoremanifeste. Beschädigte Checkpoints werden nicht zu Datenbanksicherungen herabgestuft.
- Ungültige Generationen erzeugen WARNING auch neben gültigen Generationen. Die Anzeige nennt den Schutzumfang. Jede Statusabfrage prüft aktuell; große Sicherungsbestände können dadurch längere Statusabfragen verursachen.
- Bei höchstens 900px wachsen die Kopfzeilen vertikal statt benachbarte Bedienelemente zu überlagern. Markenfarben und große Desktopansicht bleiben erhalten. Kleine Bildschirme benötigen vertikales Scrollen.

## Ausgeführte Prüfungen
- `python3 -S tests/startup/test_runtime_safety.py`: 11/11 PASS, echte temporäre SQLite-/Medienstände und frische Wiederherstellung.
- `PYTHONPATH=core/reference_python python3 -S core/reference_python/tests/test_recovery_acceptance.py`: 14/14 PASS.
- `PYTHONPATH=core/reference_python python3 -S core/reference_python/tests/test_persistence_contract.py`: 5/5 PASS.
- Zwei bestehende UI-Verträge: 13/13 und 7/7 PASS; mobile Cross-Runtime-Parität PASS.
- `PROVOWARE_PLAYWRIGHT_MODULE=<installiertes Playwright-Modul> node tests/ui_consistency/runtime_safety_browser.cjs`: Chromium 134, jeweils 800x600, Schrift und Arbeitsbereich 100/150/200 Prozent. In jedem Fall Memo speichern, bearbeiten, Papierkorb und Wiederherstellen erfolgreich, kein Seitenüberlauf und keine JavaScript-Ausnahme. Der Runner startet einen eigenen Dienst und nutzt ausschließlich einen eigenen temporären Datenordner.

## Grenzen und Rückweg
Kein natives Kubuntu/Wayland, kein Mikrofon- oder Mobilgerätetest, kein 8h-Test. Kanonische Gates unverändert 1/7, NO-GO. Der pauschale unittest-discover-Aufruf ist für die vorhandenen selbststartenden Skripte ungeeignet (SystemExit wird als Importfehler erfasst); deshalb wurden die zuständigen Skripte direkt ausgeführt. Rückweg: diesen isolierten Änderungscommit zurücknehmen; es wurden keine Nutzerdaten umgewandelt.
