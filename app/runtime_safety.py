"""Read-only boundaries for local web files and truthful backup indicators."""
from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path
from urllib.parse import unquote, urlsplit

from provoware_core.recovery import sha256_file


def ui_file_path(root: Path, request_path: str) -> Path:
    """Resolve once, including symlinks, before allowing a static-file read."""
    try:
        parsed = urlsplit(request_path)
        path = unquote(parsed.path, errors="strict")
        if parsed.scheme or parsed.netloc or "\x00" in path or "\\" in path:
            raise ValueError("Invalid local path")
        base = Path(root).resolve(strict=True)
        target = (base / path.lstrip("/")).resolve()
        if not target.is_relative_to(base):
            raise ValueError("Outside UI directory")
        return target
    except (OSError, ValueError, RuntimeError) as exc:
        raise PermissionError("Dateizugriff außerhalb der Oberfläche gesperrt.") from exc


def _regular_file(root: Path, relative: str) -> Path:
    candidate = root / relative
    # Reject every symlink component, including links pointing back inside.
    for part in (candidate, *candidate.parents):
        if part == root:
            break
        if part.is_symlink():
            raise ValueError("Linked backup file")
    if not candidate.resolve(strict=True).is_relative_to(root.resolve(strict=True)):
        raise ValueError("Outside backup generation")
    if not candidate.is_file():
        raise ValueError("Backup file missing")
    return candidate


def _manifest(root: Path, name: str) -> dict:
    path = _regular_file(root, name)
    if path.stat().st_size > 4 * 1024 * 1024:
        raise ValueError("Backup manifest too large")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Backup manifest must be an object")
    return value


def _component(value) -> bool:
    return (isinstance(value, str) and bool(value) and value not in (".", "..")
            and not any(c in value for c in ("/", "\\", "\x00")))


def _digest(value) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _check_standalone_database(database: Path, expected_hash: str) -> None:
    def reject_sidecars() -> None:
        for suffix in ("-wal", "-shm", "-journal"):
            sidecar = Path(str(database) + suffix)
            if sidecar.exists() or sidecar.is_symlink():
                raise ValueError("Backup database has journal sidecars")

    # A status request must never checkpoint a WAL or create/remove sidecars.
    # Immutable reads ignore WAL contents, so only standalone snapshots qualify.
    reject_sidecars()
    if sha256_file(database) != expected_hash:
        raise ValueError("Backup database checksum mismatch")
    connection = sqlite3.connect(database.resolve(strict=True).as_uri()
                                 + "?mode=ro&immutable=1", uri=True)
    try:
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    finally:
        connection.close()
    reject_sidecars()
    if integrity != "ok" or sha256_file(database) != expected_hash:
        raise ValueError("Backup database changed or failed integrity check")


def _generation_kind(generation: Path) -> str:
    database_path = _regular_file(generation, "core.sqlite3")
    checkpoint = generation / "checkpoint_manifest.json"
    if checkpoint.exists() or checkpoint.is_symlink():
        manifest = _manifest(generation, "checkpoint_manifest.json")
        database = manifest.get("database")
        assets = manifest.get("assets")
        if (manifest.get("format") != "OI_PROVOWARE_CHECKPOINT"
                or type(manifest.get("version")) is not int or manifest["version"] != 1
                or not isinstance(database, dict) or database.get("file") != "core.sqlite3"
                or database.get("integrity") != "ok" or not _digest(database.get("sha256"))
                or not isinstance(assets, list)):
            raise ValueError("Invalid checkpoint")
        seen = set()
        for asset in assets:
            if not isinstance(asset, dict):
                raise ValueError("Invalid checkpoint asset")
            aid, kind, name = (asset.get(k) for k in ("asset_id", "kind", "stored_name"))
            if (not _component(aid) or kind not in ("audio", "document")
                    or not _component(name) or not _digest(asset.get("sha256"))
                    or aid in seen):
                raise ValueError("Invalid checkpoint asset path")
            seen.add(aid)
            media = _regular_file(generation, f"assets/{kind}/{name}")
            if sha256_file(media) != asset["sha256"]:
                raise ValueError("Checkpoint asset checksum mismatch")
            saved = _manifest(generation, f"manifeste/assets/{aid}.json")
            if any(saved.get(k) != asset[k] for k in ("asset_id", "kind", "stored_name", "sha256")):
                raise ValueError("Checkpoint restore manifest mismatch")
            if (saved.get("status") != "ACTIVE"
                    or not isinstance(saved.get("title"), str)
                    or not isinstance(saved.get("original_name"), str)
                    or type(saved.get("size_bytes")) is not int
                    or saved["size_bytes"] != media.stat().st_size):
                raise ValueError("Incomplete checkpoint restore metadata")
        _check_standalone_database(database_path, database["sha256"])
        return "project"
    manifest = _manifest(generation, "manifest.json")
    if (manifest.get("database") != "core.sqlite3"
            or manifest.get("generation") != generation.name
            or manifest.get("integrity_check") != "ok"
            or manifest.get("verified_restore") is not True
            or not _digest(manifest.get("sha256"))):
        raise ValueError("Invalid database backup")
    _check_standalone_database(database_path, manifest["sha256"])
    return "database"


def verified_backup_status(project: Path) -> dict:
    """Never equate a filename or an old success flag with current integrity."""
    counts = {"database": 0, "project": 0}
    invalid = 0
    seen = set()
    for root in (Path(project) / "backups", Path(project) / "daten" / "backups"):
        try:
            if not root.exists() and not root.is_symlink():
                continue
            if root.is_symlink() or root.parent.is_symlink():
                raise ValueError("Linked backup root")
            for generation in root.iterdir():
                if generation.is_symlink():
                    invalid += 1
                    continue
                if not generation.is_dir():
                    continue
                resolved = generation.resolve(strict=True)
                if resolved in seen:
                    continue
                seen.add(resolved)
                try:
                    counts[_generation_kind(generation)] += 1
                except (OSError, ValueError, RuntimeError, KeyError, TypeError, sqlite3.Error):
                    invalid += 1
        except (OSError, ValueError, RuntimeError):
            invalid += 1
    total = sum(counts.values())
    label = (f"{counts['project']} Projekt / {counts['database']} Datenbank"
             if total else "Keine geprüfte Sicherung")
    if invalid:
        label += f" · {invalid} ungültig"
    return {"generations": total, "project_generations": counts["project"],
            "database_generations": counts["database"], "invalid_generations": invalid,
            "state": "WARNING" if invalid else ("READY" if total else "EMPTY"),
            "label": label}
