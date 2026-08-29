# 🏗️ ARCHITEKTUR — STATUS: FREIGEGEBEN — V0.1

## Schichten
1. Presentation
2. Application/Use-Cases
3. Domain
4. Validation Contracts
5. Mutation Queue
6. Repository/Persistence
7. Platform Adapter
8. Infrastructure/Diagnostics

## Modulgrenzen
Jedes Fachmodul besitzt:
- Domain-Modell
- Use-Case-Schnittstelle
- Repository-Schnittstelle
- Validierungsregeln
- Ereignisse
- Tests
- Hilfe-/Textschlüssel

Keine UI-Komponente schreibt direkt Dateien.

## Zielordnerstruktur
```text
app/
  domain/
  application/
  contracts/
  persistence/
  platform/
    android/
    linux/
    ios/
  modules/
    memo/
    voice/
    todo/
    calendar/
    documents/
    audio/
    profile/
    settings/
    search/
    rewards/
  diagnostics/
  recovery/
  ui/
  resources/texts/
tests/
docs/
manifeste/
registry/
runtime-data/      # nicht mit Release-Quellpaket vermischen
```

## Architekturregeln
- Dependency Inversion
- keine zyklischen Modulabhängigkeiten
- IDs statt Dateinamen als Identität
- Schema-Version an jedem persistierten Aggregat
- strukturierte Domain Events
- keine Geschäftslogik in Views
- keine plattformspezifischen APIs im Domain-Kern
