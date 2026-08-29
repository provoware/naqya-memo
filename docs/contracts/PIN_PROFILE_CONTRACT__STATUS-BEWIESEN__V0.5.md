# 🔐 PIN-/PROFIL-CONTRACT — V0.5

- PIN exakt vier ASCII-Ziffern.
- Speicherung ausschließlich als gesalzener PBKDF2-SHA256-Hash.
- PIN ist **keine Verschlüsselung** der Nutzerdaten.
- Falsche und erfolgreiche Versuche werden mit Zeitstempel protokolliert.
- PIN-Wechsel benötigt den aktuellen PIN.
- Spätere PIN-Recovery muss klar sichtbar und ohne falsches Sicherheitsversprechen erfolgen.
