"""Real temporary files, snapshots and fresh restores; no user data."""
import json
import hashlib
import http.client
import os
import socket
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "app"), str(ROOT / "core/reference_python")]
from runtime_safety import ui_file_path, verified_backup_status
from provoware_core.backup import create_verified_backup
from provoware_core.recovery import restore_backup_to_fresh_project
from provoware_core.project_checkpoint import create_project_checkpoint, restore_project_checkpoint
from provoware_core.assets import AssetManager


class RuntimeSafetyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name)
        self.ui = self.project / "ui"
        self.ui.mkdir()
        (self.ui / "index.html").write_text("<h1>safe</h1>")
        (self.project / "outside.txt").write_text("outside")
        self.db = self.project / "source.sqlite3"
        with sqlite3.connect(self.db) as conn:
            conn.execute("CREATE TABLE sample(value TEXT)")
            conn.execute("INSERT INTO sample VALUES ('retained')")

    def snapshot(self):
        return create_verified_backup(self.db, self.project / "backups")

    def checkpoint(self):
        manager = AssetManager(self.project)
        source = self.project / "sample.txt"
        source.write_text("retained media")
        manager.import_asset(source, "document")
        return create_project_checkpoint(self.db, manager, self.project / "backups")

    def test_valid_ui_file_and_query(self):
        self.assertEqual(ui_file_path(self.ui, "/index.html?x=1"), self.ui / "index.html")

    def test_traversal_encoded_paths_and_invalid_characters(self):
        for path in ("/../outside.txt", "/a/../../outside.txt", "/%2e%2e/outside.txt",
                     "/%2e%2e%2foutside.txt", "/..\\outside.txt", "/%00", "/%ff",
                     "//external/path", "https://external/path"):
            with self.subTest(path=path), self.assertRaises(PermissionError):
                ui_file_path(self.ui, path)

    def test_external_symlink_blocked(self):
        (self.ui / "link.txt").symlink_to(self.project / "outside.txt")
        with self.assertRaises(PermissionError):
            ui_file_path(self.ui, "/link.txt")

    def test_missing_and_fake_backups_never_ready(self):
        self.assertEqual(verified_backup_status(self.project)["state"], "EMPTY")
        fake = self.project / "backups/fake"
        fake.mkdir(parents=True)
        (fake / "manifest.json").write_text("not json")
        state = verified_backup_status(self.project)
        self.assertEqual(state["generations"], 0)
        self.assertEqual(state["state"], "WARNING")

    def test_real_snapshot_and_fresh_restore(self):
        generation = self.snapshot()
        state = verified_backup_status(self.project)
        self.assertEqual(state["database_generations"], 1)
        self.assertEqual(state["project_generations"], 0)
        restored = restore_backup_to_fresh_project(generation, self.project / "fresh")
        with sqlite3.connect(restored) as conn:
            self.assertEqual(conn.execute("SELECT value FROM sample").fetchone()[0], "retained")

    @staticmethod
    def tree_bytes(root):
        return {p.relative_to(root).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
                for p in root.rglob("*") if p.is_file()}

    def update_database_hash(self, generation):
        checkpoint = generation / "checkpoint_manifest.json"
        path = checkpoint if checkpoint.exists() else generation / "manifest.json"
        manifest = json.loads(path.read_text())
        digest = hashlib.sha256((generation / "core.sqlite3").read_bytes()).hexdigest()
        if checkpoint.exists():
            manifest["database"]["sha256"] = digest
        else:
            manifest["sha256"] = digest
        path.write_text(json.dumps(manifest))

    def test_real_wal_backups_rejected_without_changing_any_file(self):
        for create in (self.snapshot, self.checkpoint):
            generation = create()
            source = self.project / (generation.name + ".sqlite3")
            conn = sqlite3.connect(source)
            try:
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA wal_autocheckpoint=0")
                conn.execute("CREATE TABLE pending(value TEXT)")
                conn.execute("INSERT INTO pending VALUES ('committed in WAL')")
                conn.commit()
                for suffix in ("", "-wal", "-shm"):
                    shutil.copyfile(Path(str(source) + suffix), generation / ("core.sqlite3" + suffix))
            finally:
                conn.close()
            self.update_database_hash(generation)
        before = self.tree_bytes(self.project / "backups")
        for _ in range(2):
            state = verified_backup_status(self.project)
            self.assertEqual(state["state"], "WARNING")
            self.assertEqual(state["generations"], 0)
            self.assertEqual(self.tree_bytes(self.project / "backups"), before)

    def test_sidecars_and_sidecar_symlinks_block_both_formats(self):
        for create in (self.snapshot, self.checkpoint):
            generation = create()
            for suffix in ("-wal", "-shm", "-journal"):
                sidecar = generation / ("core.sqlite3" + suffix)
                for linked in (False, True):
                    with self.subTest(format=create.__name__, suffix=suffix, linked=linked):
                        if linked:
                            sidecar.symlink_to(self.project / "missing-sidecar")
                        else:
                            sidecar.write_bytes(b"pending journal")
                        before = self.tree_bytes(generation) if not linked else None
                        state = verified_backup_status(self.project)
                        self.assertEqual(state["state"], "WARNING")
                        if linked:
                            self.assertTrue(sidecar.is_symlink())
                        else:
                            self.assertEqual(self.tree_bytes(generation), before)
                        sidecar.unlink()

    def test_standalone_wal_mode_and_uri_special_characters_stay_valid(self):
        generation = self.snapshot()
        renamed = generation.with_name(generation.name + " space ?#%")
        generation.rename(renamed)
        path = renamed / "manifest.json"
        manifest = json.loads(path.read_text())
        manifest["generation"] = renamed.name
        path.write_text(json.dumps(manifest))
        conn = sqlite3.connect(renamed / "core.sqlite3")
        conn.execute("PRAGMA journal_mode=WAL")
        conn.close()
        self.update_database_hash(renamed)
        before = self.tree_bytes(renamed)
        for _ in range(2):
            self.assertEqual(verified_backup_status(self.project)["state"], "READY")
            self.assertEqual(self.tree_bytes(renamed), before)

    def test_sidecar_created_during_inspection_is_rejected_without_checkpoint(self):
        generation = self.snapshot()
        database = generation / "core.sqlite3"
        before = database.read_bytes()
        connect = sqlite3.connect
        sidecar = generation / "core.sqlite3-journal"

        def concurrent_journal(*args, **kwargs):
            sidecar.write_bytes(b"created concurrently")
            return connect(*args, **kwargs)

        with patch("runtime_safety.sqlite3.connect", side_effect=concurrent_journal):
            state = verified_backup_status(self.project)
        self.assertEqual(state["state"], "WARNING")
        self.assertEqual(state["generations"], 0)
        self.assertEqual(database.read_bytes(), before)
        self.assertEqual(sidecar.read_bytes(), b"created concurrently")

    def test_manifest_type_missing_database_bad_hash_and_invalid_sqlite(self):
        for defect in ("list", "missing", "hash", "sqlite", "false_success"):
            with self.subTest(defect=defect):
                generation = self.snapshot()
                manifest_path = generation / "manifest.json"
                manifest = json.loads(manifest_path.read_text())
                if defect == "list":
                    manifest = []
                elif defect == "missing":
                    (generation / "core.sqlite3").unlink()
                elif defect == "hash":
                    manifest["sha256"] = "0" * 64
                elif defect == "false_success":
                    manifest["verified_restore"] = "true"
                else:
                    import hashlib
                    (generation / "core.sqlite3").write_bytes(b"not a database")
                    manifest["sha256"] = hashlib.sha256(b"not a database").hexdigest()
                manifest_path.write_text(json.dumps(manifest))
        self.assertEqual(verified_backup_status(self.project)["generations"], 0)

    def test_symlink_generation_manifest_database_and_root_rejected(self):
        generation = self.snapshot()
        (self.project / "backups/linked").symlink_to(generation, target_is_directory=True)
        self.assertEqual(verified_backup_status(self.project)["generations"], 1)
        for name in ("manifest.json", "core.sqlite3"):
            path = generation / name
            saved = self.project / (name + ".saved")
            path.rename(saved)
            path.symlink_to(saved)
            self.assertEqual(verified_backup_status(self.project)["generations"], 0)
            path.unlink()
            saved.rename(path)
        root = self.project / "backups"
        root.rename(self.project / "saved-backups")
        root.symlink_to(self.project / "saved-backups", target_is_directory=True)
        self.assertEqual(verified_backup_status(self.project)["generations"], 0)

    def test_full_checkpoint_and_fresh_restore(self):
        generation = self.checkpoint()
        state = verified_backup_status(self.project)
        self.assertEqual(state["project_generations"], 1)
        self.assertEqual(state["database_generations"], 0)
        restored = restore_project_checkpoint(generation, self.project / "restored")
        self.assertEqual(restored["assets_verified"], 1)

    def test_checkpoint_invalid_paths_missing_media_and_restore_manifest(self):
        for defect in ("db_path", "asset_path", "missing_media", "media_hash", "missing_manifest", "metadata", "inactive_metadata"):
            with self.subTest(defect=defect):
                generation = self.checkpoint()
                path = generation / "checkpoint_manifest.json"
                manifest = json.loads(path.read_text())
                asset = manifest["assets"][0]
                if defect == "db_path":
                    manifest["database"]["file"] = "../source.sqlite3"
                elif defect == "asset_path":
                    asset["stored_name"] = "../../outside.txt"
                elif defect == "missing_media":
                    (generation / "assets" / asset["kind"] / asset["stored_name"]).unlink()
                elif defect == "media_hash":
                    (generation / "assets" / asset["kind"] / asset["stored_name"]).write_text("tampered")
                elif defect == "missing_manifest":
                    (generation / "manifeste/assets" / (asset["asset_id"] + ".json")).unlink()
                else:
                    saved = generation / "manifeste/assets" / (asset["asset_id"] + ".json")
                    metadata = json.loads(saved.read_text())
                    if defect == "metadata":
                        metadata = {k: metadata[k] for k in ("asset_id", "kind", "stored_name", "sha256")}
                    else:
                        metadata["status"] = "TRASHED"
                    saved.write_text(json.dumps(metadata))
                path.write_text(json.dumps(manifest))
        self.assertEqual(verified_backup_status(self.project)["generations"], 0)

    def test_bad_checkpoint_cannot_fall_back_to_valid_snapshot(self):
        generation = self.snapshot()
        (generation / "checkpoint_manifest.json").write_text("{}")
        self.assertEqual(verified_backup_status(self.project)["generations"], 0)

    def test_http_get_and_head_enforce_the_same_boundary(self):
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        env = dict(os.environ, PROVOWARE_PORT=str(port),
                   PROVOWARE_PROJECT_PATH=str(self.project / "http-project"))
        server = subprocess.Popen([sys.executable, "-S", str(ROOT / "app/server.py"), "--no-browser"],
                                  env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            for _ in range(80):
                try:
                    with socket.create_connection(("127.0.0.1", port), timeout=.1):
                        break
                except OSError:
                    time.sleep(.05)
            for method in ("GET", "HEAD"):
                for path, expected in (("/index.html?normal=1", 200),
                                       ("/../../README.md", 403),
                                       ("/%2e%2e/%2e%2e/README.md", 403)):
                    with self.subTest(method=method, path=path):
                        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=3)
                        try:
                            conn.request(method, path)
                            response = conn.getresponse()
                            self.assertEqual(response.status, expected)
                            response.read()
                        finally:
                            conn.close()
        finally:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=5)


if __name__ == "__main__":
    unittest.main()
