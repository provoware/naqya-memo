# CI Dependency Execution Boundary – STATUS: AKTIV

## Zweck
Der kanonische Quality-Workflow arbeitet im Release-Freeze ohne Projekt-Abhängigkeitsinstallation. Diese Eigenschaft ist ab jetzt ein fail-closed Release-Sicherheitsvertrag und darf nicht still durch neue Install-, Paket-Runner- oder Download-Kommandos aufgeweicht werden.

## Verbindlicher Vertrag
`tests/release_gate/test_ci_dependency_execution_boundary.py` analysiert alle `run: |`-Blöcke von `.github/workflows/quality.yml` und blockiert direkte Befehle aus folgenden Klassen:

- System-Paketinstallation: `apt`, `apt-get`, `dnf`, `yum`, `zypper`, `pacman`, `apk`
- Python-Abhängigkeitsinstallation: `pip install`, `pip sync`, `python -m pip install/sync`, `uv pip install/sync`
- JavaScript-Paketinstallation oder Paket-Runner: `npm install`, `npm ci`, `npx`, `yarn`, `pnpm`, `bun install`, `bun x`
- direkte Netzwerkdownloads: `curl`, `wget`
- implizite Git-Inhaltsnachladung: `git submodule init/update`, `git lfs fetch/pull`

Der Test selbst wird als eigener früher Quality-Schritt ausgeführt. Wird später tatsächlich eine externe Abhängigkeit benötigt, muss der CI-Vertrag bewusst geändert, die Quelle/Version unveränderlich gebunden und die Supply-Chain-Auswirkung separat geprüft werden. Ein beiläufiges Installkommando ist kein zulässiger Freeze-Slice.

## Abgrenzung
Die bereits verwendeten, auf Commit-SHAs gepinnten offiziellen Actions `actions/checkout`, `actions/setup-python` und `actions/setup-node` bleiben zulässig. Der Vertrag fügt keine Workflow-Berechtigungen, Secrets, OIDC-Rechte, Signaturschlüssel oder Produktfunktionen hinzu und verändert keine realen Browser-/Geräte-Gates.

## Erwartete Wirkung
- geringere CI-Supply-Chain-Angriffsfläche,
- reproduzierbarere Quality-Läufe,
- keine unbemerkten Install-Hooks aus neu eingeführten Package-Managern,
- explizite Review-Pflicht, bevor der Release-Prüfpfad externe Projektabhängigkeiten ausführt.
