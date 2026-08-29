# ENTWICKLUNGSITERATION V0.3 — TRANSACTION-KILL & RECOVERY ACCEPTANCE
**Datum:** 2026-08-28

## Patchvorankündigung
- Mutation Queue
- Projekt-Locking
- Restore in frischen Projektordner
- Undo/Redo-Semantik
- Kill-Worker und Failure-Injection
- Recovery-/Locking-Verträge
- Regression-Suite
- Repo-/Doku-Synchronisierung

## Grund
Domainmodule dürfen nicht auf einer Datenschicht aufbauen, deren Crash- und Kollisionsverhalten nur theoretisch beschrieben ist.

## Wirkung
V0.3 erzeugt echte Subprozess-Kill-Evidence an Transaktionsgrenzen und trennt klar:
- nicht begonnen,
- zurückgerollt,
- committed,
- beschädigt/abgelehnt.

## Restrisiko
OS-native Failure-Injection für Android/iOS/Linux muss später auf realen Zielgeräten bzw. Runnern erfolgen.
