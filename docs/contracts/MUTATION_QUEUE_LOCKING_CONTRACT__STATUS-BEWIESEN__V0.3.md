# MUTATION QUEUE & LOCKING CONTRACT — V0.3

## Ziel
Kein paralleler Schreibpfad darf dieselben Produktdaten unkoordiniert verändern.

## Regeln
1. Alle fachlichen Mutationen laufen über eine Single-Writer-Queue.
2. Projektinstanzen besitzen eine exklusive Lock-Datei.
3. Ein Lock darf nur als stale verworfen werden, wenn der Besitzerprozess nachweislich nicht mehr existiert.
4. DB-Lock ist ein erwartbarer Fehlerzustand, kein Grund für aggressive Reparatur.
5. Retry muss begrenzt, sichtbar und abbrechbar sein.
6. Reads dürfen parallel erfolgen, sofern keine inkonsistente Zwischenrepräsentation sichtbar wird.
