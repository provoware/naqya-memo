#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE_PATH = ROOT / "registry" / "PRODUCT_BASELINE.json"
LEGACY_VERSION_PATH = ROOT / "registry" / "VERSION.json"


def fail(message: str) -> None:
    print(f"FAIL PRODUCT LINEAGE: {message}", file=sys.stderr)
    raise SystemExit(2)


def git(*args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        fail(f"git {' '.join(args)}: {proc.stderr.strip() or 'unknown git error'}")
    return proc.stdout.strip()


def main() -> int:
    if not BASELINE_PATH.is_file():
        fail("registry/PRODUCT_BASELINE.json fehlt")
    try:
        baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"PRODUCT_BASELINE.json unlesbar: {exc}")

    if baseline.get("schema_version") != 3:
        fail("schema_version muss exakt 3 sein")
    if baseline.get("product_id") != "naqya-memo":
        fail("unerwartete product_id")
    if baseline.get("ui_contract_version") != "0.12.2.5":
        fail("UI-Vertragsversion darf nicht unter V0.12.2.5 zurückfallen")

    lineage = baseline.get("lineage") or {}
    ancestor = lineage.get("required_ancestor_sha")
    donor = lineage.get("frozen_hardening_donor_sha")
    if not isinstance(ancestor, str) or len(ancestor) != 40:
        fail("required_ancestor_sha fehlt oder ist ungültig")
    if not isinstance(donor, str) or len(donor) != 40:
        fail("frozen_hardening_donor_sha fehlt oder ist ungültig")

    proc = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, "HEAD"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode != 0:
        head = git("rev-parse", "HEAD")
        fail(f"HEAD {head} stammt nicht vom qualifizierten Baseline-Anker {ancestor} ab")

    contracts = baseline.get("required_ui_contracts")
    if not isinstance(contracts, list) or len(contracts) != 4:
        fail("genau vier verpflichtende UI-Verträge werden erwartet")
    for contract in contracts:
        path = ROOT / str(contract.get("path", ""))
        expected_blob = contract.get("blob_sha")
        if not path.is_file():
            fail(f"Pflichtvertrag fehlt: {path.relative_to(ROOT)}")
        actual_blob = git("hash-object", str(path.relative_to(ROOT)))
        if actual_blob != expected_blob:
            fail(
                f"Pflichtvertrag verändert: {path.relative_to(ROOT)} "
                f"erwartet {expected_blob}, gefunden {actual_blob}"
            )

    if not LEGACY_VERSION_PATH.is_file():
        fail("registry/VERSION.json fehlt")
    try:
        legacy = json.loads(LEGACY_VERSION_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"registry/VERSION.json unlesbar: {exc}")
    expected_legacy = baseline.get("legacy_version_contract")
    if legacy.get("version") != expected_legacy:
        fail(
            "Legacy-Produktversion stimmt nicht mit der Produkt-Baseline überein: "
            f"erwartet {expected_legacy!r}, gefunden {legacy.get('version')!r}"
        )

    print("PASS PRODUCT LINEAGE")
    print(f"product_version={baseline['product_version']}")
    print(f"ui_contract_version={baseline['ui_contract_version']}")
    print(f"required_ancestor_sha={ancestor}")
    print(f"qualified_ui_source_sha={lineage.get('qualified_ui_source_sha')}")
    print(f"acceptance={baseline['acceptance']['track']} / {baseline['acceptance']['revision']}")
    print(f"head={git('rev-parse', 'HEAD')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
