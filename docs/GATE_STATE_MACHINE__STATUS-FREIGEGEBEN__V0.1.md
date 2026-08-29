# 🚦 GATE STATE MACHINE — STATUS: FREIGEGEBEN — V0.1

```text
ENTWURF
  ↓
IMPLEMENTIERT
  ↓
GEPRÜFT
  ↓
BEWIESEN
  ↓
FREIGEGEBEN
```

Rücksprünge:
- Testfehler → IMPLEMENTIERT
- Evidence fehlt → GEPRÜFT
- Regression → IMPLEMENTIERT
- Sicherheitsverletzung → ENTWURF oder BLOCKIERT

## Release-Gates
G0 Struktur
G1 Datenintegrität
G2 Recovery
G3 Plattformfähigkeit
G4 Accessibility
G5 Performance
G6 Regression
G7 Dokumentationssync
G8 Release-Reproduzierbarkeit

Kein Release bei rotem P0-Gate.
