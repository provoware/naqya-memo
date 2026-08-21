#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import os
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPACK = ROOT / "tools/repack_deb_deterministic.sh"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_raw(base: Path, name: str, timestamp: int) -> Path:
    root = base / f"root-{name}"
    debian = root / "DEBIAN"
    payload = root / "usr/share/naqya-repro-test"
    debian.mkdir(parents=True)
    payload.mkdir(parents=True)
    (debian / "control").write_text(
        "Package: naqya-repro-test\nVersion: 1.0\nArchitecture: all\nMaintainer: PROVOWARE\nDescription: NAQYA reproducibility contract\n",
        encoding="utf-8",
    )
    (payload / "payload.txt").write_text("identischer Paketinhalt\n", encoding="utf-8")
    for path in root.rglob("*"):
        os.utime(path, (timestamp, timestamp), follow_symlinks=False)
    raw = base / f"raw-{name}.deb"
    subprocess.run(["dpkg-deb", "--build", "--root-owner-group", str(root), str(raw)], check=True, capture_output=True)
    return raw


def main() -> None:
    assert REPACK.is_file(), "DEB-Repacker fehlt"
    script = REPACK.read_text(encoding="utf-8")
    for marker in (
        "SOURCE_DATE_EPOCH",
        "dpkg-deb -R",
        "--root-owner-group",
        "--uniform-compression",
        "-Zgzip",
        "-z9",
        "touch -h",
        "cmp -s",
    ):
        assert marker in script, f"Reproduzierbarkeitsvertrag fehlt: {marker}"

    with tempfile.TemporaryDirectory(prefix="naqya-deb-repro-") as tmp:
        base = Path(tmp)
        now = int(time.time())
        raw_a = build_raw(base, "a", now - 3600)
        raw_b = build_raw(base, "b", now)
        assert sha256(raw_a) != sha256(raw_b), "Testaufbau muss zunächst unterschiedliche Roh-DEBs erzeugen"

        out_a = base / "det-a.deb"
        out_b = base / "det-b.deb"
        env = os.environ.copy()
        env["SOURCE_DATE_EPOCH"] = "946684800"
        subprocess.run(["bash", str(REPACK), str(raw_a), str(out_a)], check=True, env=env, capture_output=True)
        subprocess.run(["bash", str(REPACK), str(raw_b), str(out_b)], check=True, env=env, capture_output=True)

        assert out_a.read_bytes() == out_b.read_bytes(), "Normalisierte DEBs sind nicht byteidentisch"
        assert sha256(out_a) == sha256(out_b)

    print("NAQYA deterministische DEB-Reproduzierbarkeit: PASS")


if __name__ == "__main__":
    main()
