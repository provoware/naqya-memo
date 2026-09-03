#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT_DEFAULT = Path(__file__).resolve().parents[1]


class DialogUI:
    def __init__(self) -> None:
        self.desktop = bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
        self.kdialog = shutil.which("kdialog") if self.desktop else None
        self.zenity = shutil.which("zenity") if self.desktop else None
        self.terminal = sys.stdin.isatty() and sys.stderr.isatty()

    @property
    def interactive(self) -> bool:
        return bool(self.kdialog or self.zenity or self.terminal)

    def choose(self, title: str, prompt: str, options: list[tuple[str, str]]) -> str | None:
        if self.kdialog:
            cmd = [self.kdialog, "--title", title, "--menu", prompt]
            for key, label in options:
                cmd.extend([key, label])
            result = subprocess.run(cmd, text=True, capture_output=True)
            return result.stdout.strip() if result.returncode == 0 else None
        if self.zenity:
            rows = []
            for key, label in options:
                rows.extend([key, label])
            cmd = [
                self.zenity, "--list", "--title", title, "--text", prompt,
                "--column", "Kennung", "--column", "Profil", "--hide-column", "1",
                *rows,
            ]
            result = subprocess.run(cmd, text=True, capture_output=True)
            return result.stdout.strip() if result.returncode == 0 else None
        if self.terminal:
            print(f"\n{title}\n{prompt}", file=sys.stderr)
            for i, (_, label) in enumerate(options, 1):
                print(f"  {i}. {label}", file=sys.stderr)
            try:
                raw = input("Auswahl (Enter = Abbrechen): ").strip()
                if not raw:
                    return None
                idx = int(raw) - 1
                return options[idx][0] if 0 <= idx < len(options) else None
            except (EOFError, ValueError):
                return None
        return None

    def text(self, title: str, prompt: str, default: str = "") -> str | None:
        if self.kdialog:
            result = subprocess.run([self.kdialog, "--title", title, "--inputbox", prompt, default], text=True, capture_output=True)
            return result.stdout.rstrip("\n") if result.returncode == 0 else None
        if self.zenity:
            result = subprocess.run([self.zenity, "--entry", "--title", title, "--text", prompt, "--entry-text", default], text=True, capture_output=True)
            return result.stdout.rstrip("\n") if result.returncode == 0 else None
        if self.terminal:
            try:
                return input(f"{prompt}: ").strip()
            except EOFError:
                return None
        return None

    def pin(self, title: str, prompt: str) -> str | None:
        if self.kdialog:
            result = subprocess.run([self.kdialog, "--title", title, "--password", prompt], text=True, capture_output=True)
            return result.stdout.rstrip("\n") if result.returncode == 0 else None
        if self.zenity:
            result = subprocess.run([self.zenity, "--password", "--title", title], text=True, capture_output=True)
            return result.stdout.rstrip("\n") if result.returncode == 0 else None
        if self.terminal:
            import getpass
            try:
                return getpass.getpass(f"{prompt}: ")
            except (EOFError, KeyboardInterrupt):
                return None
        return None

    def error(self, title: str, message: str) -> None:
        if self.kdialog:
            subprocess.run([self.kdialog, "--title", title, "--error", message], check=False)
        elif self.zenity:
            subprocess.run([self.zenity, "--error", "--title", title, "--text", message], check=False)
        else:
            print(f"FEHLER: {message}", file=sys.stderr)


NEW_PROFILE = "__NEW_PROFILE__"


def active_profiles(store) -> list[tuple[str, str]]:
    rows = store.conn.execute(
        "SELECT id,display_name FROM profiles WHERE status='ACTIVE' ORDER BY created_at,id"
    ).fetchall()
    return [(str(row[0]), str(row[1])) for row in rows]


def select_or_create(store, profile_service, ui: DialogUI) -> str | None:
    profiles = active_profiles(store)
    if not ui.interactive:
        # Headless/service starts must not block. Preserve the historical first-profile behavior.
        return profiles[0][0] if profiles else ""

    options = [(profile_id, f"Vorhanden: {name}") for profile_id, name in profiles]
    options.append((NEW_PROFILE, "＋ Neues Profil anlegen"))
    selected = ui.choose(
        "PROVOWARE – Profilstart",
        "Profil auswählen oder ein neues Profil anlegen.",
        options,
    )
    if selected is None:
        return None
    if selected != NEW_PROFILE:
        return selected

    while True:
        name = ui.text("PROVOWARE – Neues Profil", "Profilname", "Mein Profil")
        if name is None:
            return None
        name = name.strip()
        if not name:
            ui.error("PROVOWARE – Neues Profil", "Bitte einen Profilnamen eingeben.")
            continue
        pin = ui.pin("PROVOWARE – Neues Profil", "Neue 4-stellige PIN")
        if pin is None:
            return None
        confirm = ui.pin("PROVOWARE – Neues Profil", "PIN zur Kontrolle wiederholen")
        if confirm is None:
            return None
        if pin != confirm:
            ui.error("PROVOWARE – Neues Profil", "Die beiden PIN-Eingaben stimmen nicht überein.")
            continue
        try:
            return profile_service.create(name, pin)
        except ValueError as exc:
            code = str(exc)
            message = "Die PIN muss genau 4 Ziffern haben." if "PIN_MUST_BE_FOUR_DIGITS" in code else "Das Profil konnte mit diesen Angaben nicht angelegt werden."
            ui.error("PROVOWARE – Neues Profil", message)


def main() -> int:
    parser = argparse.ArgumentParser(description="PROVOWARE Profilwahl vor dem geschützten Desktop-Start")
    parser.add_argument("--root", type=Path, default=ROOT_DEFAULT)
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    core = root / "core" / "reference_python"
    sys.path.insert(0, str(core))

    from provoware_core import CoreStore
    from provoware_core.profile import ProfileService

    project = Path(os.environ.get("PROVOWARE_PROJECT_PATH", str(root / "runtime" / "projektordner"))).expanduser().resolve()
    db = project / "daten" / "core.sqlite3"
    schema = root / "schemas" / "core_schema_v2.sql"
    store = CoreStore(db, schema)
    try:
        selected = select_or_create(store, ProfileService(store), DialogUI())
    finally:
        store.close()

    if selected is None:
        print("__CANCEL__")
    else:
        print(selected)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
