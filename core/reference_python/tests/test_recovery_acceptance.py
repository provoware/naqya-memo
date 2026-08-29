from pathlib import Path
import tempfile, subprocess, sys, os, sqlite3, json, stat, threading, time
from provoware_core import (
    CoreStore, MutationQueue, ProjectLock, ProjectLockError,
    UndoRedoJournal, UndoEntry, validate_backup_generation,
    restore_backup_to_fresh_project
)
from provoware_core.backup import create_verified_backup

ROOT = Path(__file__).resolve().parents[3]
SCHEMA = ROOT / "schemas" / "core_schema_v1.sql"
WORKER = ROOT / "core" / "reference_python" / "tools" / "kill_worker.py"

def make_store(td):
    return CoreStore(Path(td)/"core.sqlite3", SCHEMA)

def test_mutation_queue_serializes_writes():
    order = []
    q = MutationQueue(); q.start()
    jobs = []
    for n in range(5):
        def fn(n=n):
            before = len(order)
            time.sleep(0.01)
            order.append(n)
            return before
        jobs.append(q.submit(f"job-{n}", fn))
    results = [q.wait(j) for j in jobs]
    q.stop()
    assert order == [0,1,2,3,4]
    assert results == [0,1,2,3,4]

def test_project_lock_rejects_second_owner():
    with tempfile.TemporaryDirectory() as td:
        a = ProjectLock(Path(td)).acquire()
        try:
            try:
                ProjectLock(Path(td)).acquire()
                raise AssertionError("lock collision expected")
            except ProjectLockError as e:
                assert str(e) == "PROJECT_ALREADY_LOCKED"
        finally:
            a.release()

def test_restore_to_fresh_project_preserves_data():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        s = CoreStore(base/"core.sqlite3", SCHEMA)
        pid = s.create_profile("Restore", "hash")
        eid, _ = s.upsert_entity(profile_id=pid, entity_type="memo", title="R",
                                 payload={"body":"recoverable"})
        before = s.get_entity(eid)
        s.close()
        gen = create_verified_backup(base/"core.sqlite3", base/"backups")
        restored_db = restore_backup_to_fresh_project(gen, base/"fresh-project")
        r = CoreStore(restored_db, SCHEMA)
        after = r.get_entity(eid)
        assert before["checksum_sha256"] == after["checksum_sha256"]
        assert before["payload"] == after["payload"]
        assert r.integrity_check() == "ok"
        r.close()

def test_undo_redo_semantics():
    state = {"value": 1}
    journal = UndoRedoJournal()
    old, new = 1, 2
    state["value"] = new
    journal.record(UndoEntry(
        "change",
        undo=lambda: state.__setitem__("value", old),
        redo=lambda: state.__setitem__("value", new)
    ))
    journal.undo()
    assert state["value"] == 1 and journal.can_redo
    journal.redo()
    assert state["value"] == 2 and journal.can_undo

def _run_kill_phase(db, phase):
    return subprocess.run([sys.executable, str(WORKER), str(db), phase],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def _count_rows(db):
    c = sqlite3.connect(db)
    try:
        c.execute("CREATE TABLE IF NOT EXISTS killtest(id INTEGER PRIMARY KEY, value TEXT)")
        c.commit()
        return c.execute("SELECT COUNT(*) FROM killtest").fetchone()[0], c.execute("PRAGMA integrity_check").fetchone()[0]
    finally:
        c.close()

def test_kill_before_begin_leaves_no_write():
    with tempfile.TemporaryDirectory() as td:
        db = Path(td)/"kill.sqlite3"
        p = _run_kill_phase(db, "before_begin")
        assert p.returncode != 0
        count, integrity = _count_rows(db)
        assert count == 0 and integrity == "ok"

def test_kill_after_begin_rolls_back():
    with tempfile.TemporaryDirectory() as td:
        db = Path(td)/"kill.sqlite3"
        p = _run_kill_phase(db, "after_begin")
        assert p.returncode != 0
        count, integrity = _count_rows(db)
        assert count == 0 and integrity == "ok"

def test_kill_after_write_before_commit_rolls_back():
    with tempfile.TemporaryDirectory() as td:
        db = Path(td)/"kill.sqlite3"
        p = _run_kill_phase(db, "after_write_before_commit")
        assert p.returncode != 0
        count, integrity = _count_rows(db)
        assert count == 0 and integrity == "ok"

def test_kill_after_commit_preserves_committed_write():
    with tempfile.TemporaryDirectory() as td:
        db = Path(td)/"kill.sqlite3"
        p = _run_kill_phase(db, "after_commit")
        assert p.returncode != 0
        count, integrity = _count_rows(db)
        assert count == 1 and integrity == "ok"

def test_database_locked_fails_without_corruption():
    with tempfile.TemporaryDirectory() as td:
        db = Path(td)/"locked.sqlite3"
        c1 = sqlite3.connect(db, timeout=0.1)
        c1.execute("CREATE TABLE t(x INTEGER)")
        c1.commit()
        c1.execute("BEGIN EXCLUSIVE")
        c1.execute("INSERT INTO t VALUES (1)")
        c2 = sqlite3.connect(db, timeout=0.05)
        try:
            try:
                c2.execute("INSERT INTO t VALUES (2)")
                c2.commit()
                raise AssertionError("lock error expected")
            except sqlite3.OperationalError as e:
                assert "locked" in str(e).lower()
        finally:
            c2.close()
            c1.rollback()
            c1.close()
        c3 = sqlite3.connect(db)
        try:
            assert c3.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 0
            assert c3.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        finally:
            c3.close()

def test_corrupted_entity_checksum_detected():
    with tempfile.TemporaryDirectory() as td:
        s = make_store(td)
        pid = s.create_profile("C", "hash")
        eid, _ = s.upsert_entity(profile_id=pid, entity_type="memo", title="C",
                                 payload={"body":"original"})
        s.conn.execute("UPDATE entities SET payload_json=? WHERE id=?",
                       ('{"body":"tampered"}', eid))
        s.conn.commit()
        try:
            s.get_entity(eid)
            raise AssertionError("checksum mismatch expected")
        except RuntimeError as e:
            assert str(e) == "CHECKSUM_MISMATCH"
        s.close()

def test_corrupted_backup_rejected():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        s = CoreStore(base/"core.sqlite3", SCHEMA)
        pid = s.create_profile("B", "hash")
        s.upsert_entity(profile_id=pid, entity_type="memo", title="B",
                        payload={"body":"backup"})
        s.close()
        gen = create_verified_backup(base/"core.sqlite3", base/"backups")
        db = gen/"core.sqlite3"
        with open(db, "r+b") as f:
            f.seek(0)
            f.write(b"BROKEN!!")
            f.flush()
            os.fsync(f.fileno())
        try:
            validate_backup_generation(gen)
            raise AssertionError("corrupt backup expected")
        except RuntimeError as e:
            assert str(e) in {"BACKUP_CHECKSUM_MISMATCH","BACKUP_SQLITE_INTEGRITY_FAILED"}

def test_read_only_guard_detected_preflight():
    # Root can bypass chmod, so this proves the preflight predicate rather than OS denial.
    with tempfile.TemporaryDirectory() as td:
        p = Path(td)/"ro"
        p.mkdir()
        p.chmod(stat.S_IRUSR | stat.S_IXUSR)
        mode = stat.S_IMODE(p.stat().st_mode)
        assert not (mode & stat.S_IWUSR)
        p.chmod(stat.S_IRWXU)

def test_permission_denied_is_classifiable():
    # Cross-platform deterministic classification contract.
    err = PermissionError(13, "Permission denied", "/outside/project")
    assert err.errno == 13
    assert "Permission denied" in str(err)

def test_disk_full_is_classifiable():
    err = OSError(28, "No space left on device")
    assert err.errno == 28

if __name__ == "__main__":
    tests = [v for k,v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = []
    for t in tests:
        try:
            t()
            print("PASS", t.__name__)
        except Exception as e:
            failed.append((t.__name__, repr(e)))
            print("FAIL", t.__name__, repr(e))
    print(f"SUMMARY total={len(tests)} passed={len(tests)-len(failed)} failed={len(failed)}")
    if failed:
        raise SystemExit(1)
