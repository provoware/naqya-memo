# Desktop Erststart-PIN – Dateipfad-, Parent-, Retry- und Cleanup-Härtung

Status: Release-Freeze-Härtung, kein neues Produktfeature.

## Befund

Die einmalige Erststart-PIN wird absichtlich unter einem bekannten Pfad abgelegt, damit ein Laie sie zuverlässig findet. Der bestehende Schutz verhindert bereits Symlink-Substitution am Dateinamen und Parent-Ordner sowie einen unsicheren Retry mit der internen Bootstrap-PIN `0000`.

Der Cleanup war jedoch asymmetrisch zur sicheren Erstellung: Die PIN-Erzeugung nutzt auf unterstützten Plattformen einen geöffneten Parent-Descriptor, das spätere Entfernen verwendete wieder `FIRST_PIN_FILE.unlink()` über den auflösbaren vollständigen Pfad. Wird der Parent zwischen Erststart und Anmeldung gegen einen Symlink ausgetauscht, könnte ein gleichnamiger externer Pfad zum Ziel des Löschens werden. Für einen Credential-Cleanup ist ein solcher destruktiver TOCTOU-Randfall nicht akzeptabel.

## Vertrag

Der sichere Desktop-Server behandelt den Erststart jetzt als gemeinsamen fail-closed Sicherheitsvertrag:

- Der Parent-Ordner `nutzer-einstellungen` darf kein Symlink und muss ein echtes Verzeichnis sein.
- Auf Plattformen mit `dir_fd`-Unterstützung wird die PIN-Datei relativ zu einem geöffneten Parent-Descriptor erzeugt.
- Wo verfügbar werden `O_DIRECTORY` und `O_NOFOLLOW` verwendet.
- Die PIN-Datei wird ausschließlich neu und exklusiv mit `O_CREAT | O_EXCL` angelegt.
- Ein vorhandener Dateipfadeintrag wird weder überschrieben noch ersetzt.
- Die Datei bleibt auf Modus `0600` begrenzt und wird vor der Profil-PIN-Rotation synchronisiert.
- Ein persistiertes aktives Profil mit Bootstrap-PIN `0000` stoppt mit `INSECURE_DEFAULT_PIN_DETECTED`.
- Nach erfolgreicher PIN-Verifikation muss die einmalige PIN-Datei entfernt werden und ihre Abwesenheit nachweisbar sein.
- Ein symlinkter, falscher oder nicht sicher öffnbarer Cleanup-Parent führt fail-closed zu `FIRST_PIN_CLEANUP_FAILED`; der externe Zielpfad wird nicht angefasst.
- Auf Plattformen mit descriptor-relativem `unlink/stat` werden Löschung und Nachweis der Abwesenheit gegen denselben geöffneten Parent-Descriptor ausgeführt.
- Auf Plattformen ohne diese Unterstützung bleibt ein konservativer Fallback mit Parent-Symlink-/Typprüfung vor und nach dem path-basierten Cleanup; dessen engeres TOCTOU-Restfenster ist dokumentiert.
- Scheitert der Cleanup, bleibt die Anfrage gesperrt und erhält `503` statt einer stillen Auth-Freigabe.
- Das Credential wird erst nach erfolgreich bewiesenem Cleanup im Auth-Cache gespeichert.

## Regression

`tests/security/test_first_pin_file_symlink_guard.py` beweist vierzehn Punkte. Zusätzlich zu den bisherigen Erstellungs-, Bootstrap-, Modus- und Cleanup-Verträgen reproduziert der Test nun explizit eine Parent-Substitution zwischen Erststart und Login:

1. symlinkter Parent wird beim Erststart fail-closed abgewiesen,
2. Parent-Symlink kann PIN-Erzeugung nicht aus dem Projekt umleiten,
3. Symlink am PIN-Dateipfad wird nicht verfolgt oder ersetzt,
4. dessen Ziel bleibt unverändert und der Bootstrap-Retry-Zustand wird erkannt,
5. Retry mit aktiver interner PIN `0000` wird gestoppt,
6. normaler Erststart erzeugt eine reguläre `0600`-PIN-Datei,
7. Profil wird von `0000` wegrotiert,
8. gültige PIN erhält bei nicht möglichem Cleanup keine Autorisierung,
9. Cleanup-Fehler bleibt explizit,
10. Retry nach Beseitigung des Cleanup-Blockers gelingt,
11. nach Parent-Substitution liefert gültige PIN `503 FIRST_PIN_CLEANUP_FAILED`,
12. eine gleichnamige externe Sentinel-Datei bleibt bytegenau unverändert,
13. die echte Einmal-PIN bleibt für einen sicheren Retry erhalten,
14. nach Wiederherstellung des echten Parents wird ausschließlich die echte PIN entfernt und Login freigegeben.

CI-Schritt: `Desktop first-PIN file symlink guard`.

Maschinenlesbare Evidence: `registry/evidence/security/DESKTOP_FIRST_PIN_FILE_SYMLINK_GUARD_ACCEPTANCE.json`.

## Wirkung

Erstellung und Entfernung der Erststart-PIN folgen jetzt demselben Vertrauensmodell. Ein ausgetauschter Parent-Symlink kann den Cleanup nicht mehr auf eine externe gleichnamige Datei umlenken. Gleichzeitig bleibt die Authentifizierung fail-closed, bis der echte Credentialpfad sicher bereinigt wurde. Das reduziert destruktive Dateisystemrisiken ohne Produkt-, UI-, Schema- oder Sessionerweiterung.

## Release-Grenze

Diese Änderung führt keinen Session-/Logout-Mechanismus ein und ändert weder Produktdatenmodell noch UI-Funktionen. HTTP Basic Auth bleibt bestehen. Auf Plattformen ohne descriptor-relatives `unlink/stat` bleibt ein kleines TOCTOU-Restfenster im konservativen Fallback. Ein expliziter, garantiert invalidierbarer Browser-Lock benötigt weiterhin einen anderen Auth-Vertrag. Reale Browser-, Mikrofon-, Android- und iPhone-Gates sowie Backup-/Recovery- und Datenträger-Fehlermatrizen bleiben offen; der Release-Status bleibt NO-GO.
