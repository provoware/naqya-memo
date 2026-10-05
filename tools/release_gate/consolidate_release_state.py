#!/usr/bin/env python3
"""Kanonischen NAQYA-Release-Stand prüfen oder dokumentarisch synchronisieren.

Dieses Werkzeug wertet ausschließlich bereits vorhandene Repository-Evidence aus.
Es führt keine reale Browser-, Mikrofon-, Android-, iOS- oder Langzeitabnahme aus
und darf solche Gates niemals selbst auf PASS setzen.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERSION_FILE = ROOT / "registry" / "VERSION.json"
STATUS_FILE = ROOT / "registry" / "PROJECT_STATUS.json"
GATE_DIR = ROOT / "registry" / "evidence" / "v0.12.2" / "gates"
README = ROOT / "README.md"
TODO = ROOT / "TODO.md"
UPGRADE = ROOT / "UPGRADE_POTENZIAL.md"

START = "<!-- NAQYA_RELEASE_STATE:START -->"
END = "<!-- NAQYA_RELEASE_STATE:END -->"

GATES = [
    ("01", "8H_SOAK", "8-Stunden-Dauertest"),
    ("02", "CHROMIUM", "Chromium reale Browser-Abnahme"),
    ("03", "FIREFOX", "Firefox reale Browser-Abnahme"),
    ("04", "LINUX_MICROPHONE", "Linux reales Mikrofon"),
    ("05", "STORAGE_FAILURE", "Linux Speicherfehler/Recovery"),
    ("06", "ANDROID_DEVICE", "Android APK + echtes Gerät"),
    ("07", "IOS_IPHONE_X", "iPhone X / iOS 16.7.16"),
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_gates() -> list[dict]:
    items = []
    for no, code, label in GATES:
        path = GATE_DIR / f"GATE_{no}_{code}.json"
        if not path.exists():
            items.append({"gate": f"GATE_{no}_{code}", "status": "NOT_RUN", "label": label})
            continue
        try:
            data = load_json(path)
        except Exception as exc:
            data = {"gate": f"GATE_{no}_{code}", "status": "INVALID_EVIDENCE", "error": repr(exc)}
        data = dict(data)
        data["label"] = label
        items.append(data)
    return items


def icon(status: str) -> str:
    if status == "PASS":
        return "🟢"
    if status in {"PRECHECK_PASS", "BLOCKED", "NOT_RUN"}:
        return "🟡"
    return "🔴"


def render_block(version: dict, status: dict, gates: list[dict]) -> str:
    passed = sum(g.get("status") == "PASS" for g in gates)
    required = len(gates)
    rows = []
    for gate in gates:
        rows.append(
            f'| {gate["gate"]} | {gate["label"]} | {icon(gate.get("status", ""))} {gate.get("status", "UNKNOWN")} |'
        )
    return "\n".join(
        [
            START,
            "# 🚦 NAQYA · KANONISCHER RELEASE-STAND",
            "",
            f'> **Version:** {version["version"]}  ',
            f'> **Feature Freeze:** {"🔒 AKTIV" if status.get("feature_freeze") else "OFFEN"}  ',
            f'> **Reale Release-Gates:** **{passed}/{required} PASS**  ',
            f'> **Release:** {"🟢 GO" if status.get("release_status") == "GO" else "🔴 NO-GO"}  ',
            "> **Wahrheitsquelle:** registry/VERSION.json + registry/PROJECT_STATUS.json + reale Gate-Evidence",
            "",
            "| Gate | Prüfung | Zustand |",
            "|---|---|---|",
            *rows,
            "",
            "**Regel:** Automatische Tests, Simulationen und Quellcode-Prüfungen ersetzen keine reale Evidence.",
            "",
            f'**Nächster erlaubter Schritt:** {status.get("next_step", "Offene reale Release-Gates schließen.")}',
            END,
        ]
    )


def replace_block(text: str, block: str) -> str:
    if START in text and END in text:
        pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
        return pattern.sub(block, text, count=1)
    return block + "\n\n---\n\n" + text.lstrip()


def validate_workflow_pins(errors: list[str]) -> None:
    workflow_dir = ROOT / ".github" / "workflows"
    floating = []
    pattern = re.compile(r"^\\s*uses:\\s*([^\\s#]+)@([^\\s#]+)")
    for path in sorted(workflow_dir.glob("*.yml")):
        for no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            match = pattern.match(line)
            if not match:
                continue
            action, ref = match.groups()
            if action.startswith("./"):
                continue
            if not re.fullmatch(r"[0-9a-fA-F]{40}", ref):
                floating.append(f"{path.name}:{no} {action}@{ref}")
    if floating:
        errors.append("Nicht unveränderlich gepinnte Workflow-Aktionen: " + "; ".join(floating))


def validate_upgrade_ids(errors: list[str]) -> None:
    ids = re.findall(r"^\|\s*(UP-\d{3})\s*\|", UPGRADE.read_text(encoding="utf-8"), flags=re.M)
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    if duplicates:
        errors.append("UPGRADE_POTENZIAL.md enthält doppelte IDs: " + ", ".join(duplicates))


def validate(check_docs: bool = True) -> tuple[list[str], str]:
    errors: list[str] = []
    version = load_json(VERSION_FILE)
    status = load_json(STATUS_FILE)
    gates = collect_gates()

    if version.get("version") != status.get("version"):
        errors.append(
            f'Versionsdrift: VERSION={version.get("version")!r}, PROJECT_STATUS={status.get("version")!r}'
        )
    if bool(version.get("feature_freeze")) != bool(status.get("feature_freeze")):
        errors.append("Feature-Freeze driftet zwischen VERSION.json und PROJECT_STATUS.json.")

    actual_gate_map = {g["gate"]: g.get("status", "UNKNOWN") for g in gates}
    expected_gate_map = {f"GATE_{no}_{code}": None for no, code, _ in GATES}
    status_gate_map = status.get("gates", {})

    if set(status_gate_map) != set(expected_gate_map):
        errors.append("PROJECT_STATUS.gates enthält nicht exakt die sieben kanonischen Gates.")
    for gate_name, actual in actual_gate_map.items():
        if status_gate_map.get(gate_name) != actual:
            errors.append(
                f'Gate-Drift {gate_name}: Evidence={actual!r}, PROJECT_STATUS={status_gate_map.get(gate_name)!r}'
            )

    passed = sum(value == "PASS" for value in actual_gate_map.values())
    required = len(GATES)
    if status.get("required_release_gates") != required:
        errors.append("required_release_gates ist nicht 7.")
    if status.get("passed_release_gates") != passed:
        errors.append(
            f'passed_release_gates driftet: erwartet {passed}, gefunden {status.get("passed_release_gates")}.'
        )

    mobile_source = ROOT / "registry" / "evidence" / "v0.12.2" / "MOBILE_RUNTIME_SOURCE_ACCEPTANCE.json"
    mobile_source_pass = mobile_source.exists() and load_json(mobile_source).get("status") == "PASS"
    should_go = passed == required and mobile_source_pass
    if status.get("release_status") != ("GO" if should_go else "NO-GO"):
        errors.append("release_status widerspricht realer Gate-Evidence.")
    if bool(status.get("v1_rc_allowed")) != should_go:
        errors.append("v1_rc_allowed widerspricht realer Gate-Evidence.")

    current_steps = " ".join(
        [str(status.get("next_step", "")), str(status.get("next_next_step", ""))]
    )
    for stale in ("PR #100", "PR #102"):
        if stale in current_steps:
            errors.append(f"Aktueller nächster Schritt enthält veraltete Referenz {stale}.")

    validate_workflow_pins(errors)
    validate_upgrade_ids(errors)

    block = render_block(version, status, gates)
    if check_docs:
        for path in (README, TODO):
            text = path.read_text(encoding="utf-8")
            if text.count(START) != 1 or text.count(END) != 1:
                errors.append(f"{path.name}: kanonischer Release-Block fehlt oder ist mehrfach vorhanden.")
            elif block not in text:
                errors.append(f"{path.name}: kanonischer Release-Block driftet vom Repository-Zustand.")

    return errors, block


def write_sync() -> None:
    version = load_json(VERSION_FILE)
    status = load_json(STATUS_FILE)
    gates = collect_gates()
    gate_map = {g["gate"]: g.get("status", "UNKNOWN") for g in gates}
    passed = sum(value == "PASS" for value in gate_map.values())
    required = len(gate_map)

    mobile_source = ROOT / "registry" / "evidence" / "v0.12.2" / "MOBILE_RUNTIME_SOURCE_ACCEPTANCE.json"
    mobile_source_pass = mobile_source.exists() and load_json(mobile_source).get("status") == "PASS"
    should_go = passed == required and mobile_source_pass

    status["version"] = version["version"]
    status["feature_freeze"] = bool(version.get("feature_freeze"))
    status["required_release_gates"] = required
    status["passed_release_gates"] = passed
    status["gates"] = gate_map
    status["release_status"] = "GO" if should_go else "NO-GO"
    status["v1_rc_allowed"] = bool(should_go)
    STATUS_FILE.write_text(json.dumps(status, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    block = render_block(version, status, gates)
    for path in (README, TODO):
        path.write_text(replace_block(path.read_text(encoding="utf-8"), block), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write",
        action="store_true",
        help="Gate-Zähler/Status aus vorhandener Evidence übernehmen und README/TODO synchronisieren.",
    )
    args = parser.parse_args()

    if args.write:
        write_sync()

    errors, _ = validate(check_docs=True)
    if errors:
        print("RELEASE-STATE: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    status = load_json(STATUS_FILE)
    print(
        "RELEASE-STATE: PASS | "
        f'version={status["version"]} | '
        f'gates={status["passed_release_gates"]}/{status["required_release_gates"]} | '
        f'release={status["release_status"]}'
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
