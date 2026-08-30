# Desktop Erststart-PIN – Dateipfad-, Parent- und Retry-Härtung

Status: Release-Freeze-Härtung, kein neues Produktfeature.

## Befund

Die einmalige Erststart-PIN wird absichtlich unter einem bekannten Pfad abgelegt, damit ein Laie sie zuverlässig findet. Der bisherige Schutz verhinderte bereits, dass der eigentliche PIN-Dateiname als Symlink verfolgt oder ein vorhandener Pfadeintrag überschrieben wird.

Ein Restfall blieb offen: Der übergeordnete Ordner `nutzer-einstellungen` konnte selbst ein Symlink sein. In diesem Fall konnte die exklusive PIN-Dateianlage trotz sicherem Dateinamen in ein Verzeichnis außerhalb des Projektordners umgelenkt werden.

Beim Schließen dieses Pfades bleibt außerdem der bereits abgesicherte Retry-Fall relevant: Wenn der erste sichere Start nach Anlage des Bootstrap-Profils, aber vor erfolgreicher PIN-Rotation abbricht, kann die Referenzdatenbank bereits ein aktives Profil mit der internen Bootstrap-PIN `0000` enthalten. Ein späterer sicherer Start darf dieses Profil niemals als bereits gehärtet akzeptieren.

## Vertrag

Der sichere Desktop-Server behandelt den Erststart jetzt als einen gemeinsamen fail-closed Sicherheitsvertrag:

- Der Parent-Ordner `nutzer-einstellungen` darf kein Symlink und muss ein echtes Verzeichnis sein.
- Auf Plattformen mit `dir_fd`-Unterstützung wird dieses Verzeichnis mit eigenem Descriptor geöffnet; die PIN-Datei wird anschließend relativ zu genau diesem geöffneten Verzeichnis erzeugt. Ein späterer Austausch des Parent-Pfadnamens kann den Schreibvorgang dadurch nicht umlenken.
- Wo verfügbar werden `O_DIRECTORY` und `O_NOFOLLOW` beim Öffnen des Parent-Verzeichnisses eingesetzt.
- Auf Plattformen ohne `dir_fd` bleibt ein expliziter Parent-Symlink-/Verzeichnistyp-Check als fail-closed Fallback aktiv.
- Die PIN-Datei wird ausschließlich neu und exklusiv mit `O_CREAT | O_EXCL` angelegt.
- Wo die Plattform `O_NOFOLLOW` anbietet, wird zusätzlich das Folgen eines Symlinks im letzten Pfadelement unterbunden.
- Ein bereits vorhandener Dateipfadeintrag wird weder überschrieben noch ersetzt.
- Die Datei bleibt auf Modus `0600` begrenzt und wird vor der Profil-PIN-Rotation auf Datenträger synchronisiert.
- Wenn eine frühere Bootstrap-Ausführung ein aktives Profil mit der internen Default-PIN `0000` hinterlassen hat, startet der sichere Desktopserver nicht weiter, sondern beendet sich mit `INSECURE_DEFAULT_PIN_DETECTED`.

Damit kann weder der Dateiname noch der direkte Parent-Pfad der Erststart-PIN als Umleitung aus dem Projektordner verwendet werden.

## Regression

`tests/security/test_first_pin_file_symlink_guard.py` beweist sieben Punkte:

1. ein symlinkter Parent-Ordner wird fail-closed mit `FIRST_PIN_PARENT_UNSAFE` abgewiesen,
2. durch diesen Parent-Symlink entsteht keine PIN-Datei außerhalb des Projektordners,
3. ein vorbereiteter Symlink am Erststart-PIN-Dateipfad wird nicht verfolgt oder ersetzt,
4. das Symlink-Ziel bleibt bytegenau unverändert und der persistierte Bootstrap-Zustand wird erkannt,
5. ein Retry mit noch aktiver interner PIN `0000` wird fail-closed gestoppt,
6. ein normaler Erststart erzeugt genau eine reguläre PIN-Datei mit Modus `0600` und nicht-default PIN,
7. der normale Erststart rotiert das persistierte Profil erfolgreich von `0000` weg.

CI-Schritt: `Desktop first-PIN file symlink guard`.

Maschinenlesbare Evidence: `registry/evidence/security/DESKTOP_FIRST_PIN_FILE_SYMLINK_GUARD_ACCEPTANCE.json`.

## Wirkung

Der bekannte Credential-Pfad kann weder über den PIN-Dateinamen noch über den direkten Parent-Ordner in ein fremdes Dateisystemziel umgelenkt werden. Auf POSIX-artigen Plattformen bleibt die Dateierzeugung durch den geöffneten Parent-Descriptor zusätzlich gegen einen Pfadtausch zwischen Prüfung und Schreiben gebunden. Gleichzeitig bleibt ein durch Dateisystemfehler oder Substitution unterbrochener Erststart auf Folgestarts gesperrt, statt die interne Bootstrap-PIN versehentlich als Produktions-PIN zu akzeptieren.

## Release-Grenze

Diese Änderung führt keinen Session-/Logout-Mechanismus ein und ändert weder Produktdatenmodell noch UI-Funktionen. HTTP Basic Auth bleibt bestehen. Ein expliziter, garantiert invalidierbarer Browser-Lock benötigt weiterhin einen anderen Auth-Vertrag. Reale Browser-, Mikrofon-, Android- und iPhone-Gates bleiben offen; der Release-Status bleibt NO-GO.
