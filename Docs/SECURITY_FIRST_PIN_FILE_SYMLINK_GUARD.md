# Desktop Erststart-PIN – Dateipfad- und Retry-Härtung

Status: Release-Freeze-Härtung, kein neues Produktfeature.

## Befund

Die einmalige Erststart-PIN wird absichtlich unter einem bekannten Pfad abgelegt, damit ein Laie sie zuverlässig findet. Der bisherige Schreibpfad öffnete diesen Pfad jedoch mit `O_TRUNC`. Ein vorab platziertes Dateisystem-Symbolziel (Symlink) konnte dadurch auf Plattformen mit Symlink-Unterstützung einem fremden Ziel folgen und dessen Inhalt überschreiben.

Beim Schließen dieses Pfades entsteht zusätzlich ein wichtiger Retry-Fall: Wenn der erste sichere Start nach Anlage des Bootstrap-Profils, aber vor erfolgreicher PIN-Rotation abbricht, kann die Referenzdatenbank bereits ein aktives Profil mit der internen Bootstrap-PIN `0000` enthalten. Ein späterer sicherer Start darf dieses Profil niemals als bereits gehärtet akzeptieren.

## Vertrag

Der sichere Desktop-Server behandelt den Erststart jetzt als einen gemeinsamen fail-closed Sicherheitsvertrag:

- Die PIN-Datei wird ausschließlich neu und exklusiv mit `O_CREAT | O_EXCL` angelegt.
- Wo die Plattform `O_NOFOLLOW` anbietet, wird zusätzlich das Folgen eines Symlinks im letzten Pfadelement explizit unterbunden.
- Ein bereits vorhandener Pfadeintrag wird weder überschrieben noch ersetzt.
- Die Datei behält den bestehenden Modus `0600` und wird vor der Profil-PIN-Rotation auf Datenträger synchronisiert.
- Wenn eine frühere Bootstrap-Ausführung ein aktives Profil mit der internen Default-PIN `0000` hinterlassen hat, startet der sichere Desktopserver nicht weiter, sondern beendet sich mit `INSECURE_DEFAULT_PIN_DETECTED`.

Damit wird weder eine fremde Datei überschrieben noch nach einem fehlgeschlagenen Erststart ein unsicheres Bootstrap-Credential still als gültiger Produktionszustand freigegeben.

## Regression

`tests/security/test_first_pin_file_symlink_guard.py` beweist fünf Punkte:

1. ein vorbereiteter Symlink am Erststart-PIN-Pfad wird nicht verfolgt oder ersetzt,
2. das Symlink-Ziel bleibt bytegenau unverändert,
3. der nach dem abgebrochenen Bootstrap persistierte `0000`-Zustand wird bei einem Retry fail-closed erkannt,
4. ein normaler Erststart erzeugt genau eine reguläre PIN-Datei mit Modus `0600` und nicht-default PIN,
5. der normale Erststart rotiert das persistierte Profil erfolgreich von `0000` weg.

CI-Schritt: `Desktop first-PIN file symlink guard`.

Maschinenlesbare Evidence: `registry/evidence/security/DESKTOP_FIRST_PIN_FILE_SYMLINK_GUARD_ACCEPTANCE.json`.

## Wirkung

Der bekannte Credential-Dateipfad kann nicht mehr als ungewollter Truncate-/Overwrite-Kanal für ein fremdes Symlink-Ziel dienen. Gleichzeitig bleibt ein durch Dateisystemfehler oder Substitution unterbrochener Erststart auf Folgestarts gesperrt, statt die interne Bootstrap-PIN versehentlich als Produktions-PIN zu akzeptieren.

## Release-Grenze

Diese Änderung führt keinen Session-/Logout-Mechanismus ein und ändert weder Produktdatenmodell noch UI-Funktionen. HTTP Basic Auth bleibt bestehen. Ein expliziter, garantiert invalidierbarer Browser-Lock benötigt weiterhin einen anderen Auth-Vertrag. Reale Browser-, Mikrofon-, Android- und iPhone-Gates bleiben offen; der Release-Status bleibt NO-GO.
