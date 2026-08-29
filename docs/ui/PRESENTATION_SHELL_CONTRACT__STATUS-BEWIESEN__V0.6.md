# PRESENTATION SHELL CONTRACT — V0.6

## Enthalten
Header-Dashboard, Hauptmenü, Schnellstartleiste, leerer Arbeitsbereich, Kontextleiste, Footer/Debug, Mobile Drawer, Desktop/Kompakt/Mobil-Layout, 4 Themes, Schrift-Skalierung 80–200 %, Bereichszoom 80–150 %.

## Architekturregel
Die Shell enthält **keine Fachlogik** und importiert keine Memo/Todo/Kalender-/SQLite-Services. Aktionsflächen, die Daten verändern würden, bleiben bis V0.7 ohne Schreibwirkung.

## Responsive
- Desktop >1050 px
- Kompakt 721–1050 px
- Mobil <=720 px
- Extra klein <=380 px

## Accessibility
Skip-Link, Fokusindikator, semantische Regionen, ARIA, Reduced-Motion, Mindestkontraste, skalierbare Schrift, Touch-orientierte Controls.
