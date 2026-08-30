# Desktop Erststart-PIN – Dateipfad-, Parent-, Retry- und Cleanup-Härtung

Status: Release-Freeze-Härtung, kein neues Produktfeature.

## Befund

Die einmalige Erststart-PIN wird absichtlich unter einem bekannten Pfad abgelegt, damit ein Laie sie zuverlässig findet. Der bestehende Schutz verhindert bereits Symlink-Substitution am Dateinamen und Parent-Ordner sowie einen unsicheren Retry mit der internen Bootstrap-PIN `0000`.

Ein enger Restfall blieb offen: Nach erfolgreicher PIN-Prüfung wurde das Löschen der einmaligen PIN-Datei nur best-effort ausgeführt. Schlug `unlink` wegen Dateisystem-, Rechte- oder Pfadproblemen fehl, konnte der Request trotzdem autorisiert werden. Damit konnte eine Datei, deren Inhalt das aktuell gültige Credential enthält, entgegen dem dokumentierten Einmal-Vertrag am bekannten Pfad liegenbleiben.

## Vertrag

Der sichere Desktop-Server behandelt den Erststart jetzt als gemeinsamen fail-closed Sicherheitsvertrag:

- Der Parent-Ordner `nutzer-einstellungen` darf kein Symlink und muss ein echtes Verzeichnis sein.
- Auf Plattformen mit `dir_fd`-Unterstützung wird die PIN-Datei relativ zu einem geöffneten Parent-Descriptor erzeugt.
- Wo verfügbar werden `O_DIRECTORY` und `O_NOFOLLOW` verwendet.
- Die PIN-Datei wird ausschließlich neu und exklusiv mit `O_CREAT | O_EXCL` angelegt.
- Ein vorhandener Dateipfadeintrag wird weder überschrieben noch ersetzt.
- Die Datei bleibt auf Modus `0600` begrenzt und wird vor der Profil-PIN-Rotation synchronisiert.
- Ein persistiertes aktives Profil mit Bootstrap-PIN `0000` stoppt mit `INSECURE_DEFAULT_PIN_DETECTED`.
- Nach erfolgreicher PIN-Verifikation muss die einmalige PIN-Datei entfernt werden und der bekannte Pfad anschließend nachweislich fehlen.
- Scheitert dieser Cleanup, bleibt die Anfrage gesperrt und erhält `503` mit `FIRST_PIN_CLEANUP_FAILED` statt einer stillen Auth-Freigabe.
- Das Credential wird erst nach erfolgreich bewiesenem Cleanup im Auth-Cache gespeichert. Ein Cleanup-Fehler kann daher nicht durch einen bereits erzeugten Cachetreffer umgangen werden.

## Regression

`tests/security/test_first_pin_file_symlink_guard.py` beweist zehn Punkte:

1. symlinkter Parent wird fail-closed abgewiesen,
2. Parent-Symlink kann PIN-Erzeugung nicht aus dem Projekt umleiten,
3. Symlink am PIN-Dateipfad wird nicht verfolgt oder ersetzt,
4. dessen Ziel bleibt unverändert und der Bootstrap-Retry-Zustand wird erkannt,
5. ein Retry mit aktiver interner PIN `0000` wird fail-closed gestoppt,
6. normaler Erststart erzeugt eine reguläre `0600`-PIN-Datei mit Nicht-Default-PIN,
7. das Profil wird von `0000` wegrotiert,
8. gültige PIN erhält bei nicht möglichem Cleanup keine Autorisierung, sondern `503 FIRST_PIN_CLEANUP_FAILED`,
9. der Cleanup-Fehler bleibt explizit und wird nicht still ignoriert,
10. nach Beseitigung des Cleanup-Blockers gelingt derselbe gültige Login und der Einmal-PIN-Pfad bleibt entfernt.

CI-Schritt: `Desktop first-PIN file symlink guard`.

Maschinenlesbare Evidence: `registry/evidence/security/DESKTOP_FIRST_PIN_FILE_SYMLINK_GUARD_ACCEPTANCE.json`.

## Wirkung

Der bekannte Erststart-Credentialpfad ist jetzt nicht nur bei Erstellung, sondern auch beim Übergang in den authentifizierten Zustand abgesichert. Ein gültiges Credential wird nicht als erfolgreiche Desktop-Anmeldung akzeptiert, solange dessen Einmal-Datei nicht zuverlässig entfernt werden konnte. Damit stimmen Sicherheitsversprechen, Runtime-Verhalten und Cache-Reihenfolge überein.

## Release-Grenze

Diese Änderung führt keinen Session-/Logout-Mechanismus ein und ändert weder Produktdatenmodell noch UI-Funktionen. HTTP Basic Auth bleibt bestehen. Ein expliziter, garantiert invalidierbarer Browser-Lock benötigt weiterhin einen anderen Auth-Vertrag. Reale Browser-, Mikrofon-, Android- und iPhone-Gates sowie Backup-/Recovery- und Datenträger-Fehlermatrizen bleiben offen; der Release-Status bleibt NO-GO.
