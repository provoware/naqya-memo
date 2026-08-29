# UNDO/REDO CONTRACT — V0.3

- Jede reversible Nutzeraktion definiert inverse Operation.
- Neue Mutation nach Undo leert Redo-Zweig.
- Undo/Redo besitzt sichtbare Grenzen.
- Hard Delete ist nicht Teil normaler Undo-Kette.
- V0.3 beweist Semantik in-memory.
- Persistentes Undo-Journal wird vor Domainmodulen in V0.4 integriert.
