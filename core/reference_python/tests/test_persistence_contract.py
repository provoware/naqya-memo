from pathlib import Path
import tempfile, hashlib
from provoware_core import CoreStore, atomic_write_bytes
from provoware_core.backup import create_verified_backup

ROOT = Path(__file__).resolve().parents[3]
SCHEMA = ROOT / "schemas" / "core_schema_v1.sql"

def make_store(tmp):
    return CoreStore(Path(tmp)/"core.sqlite3", SCHEMA)

def test_profile_entity_revision_and_checksum():
    with tempfile.TemporaryDirectory() as td:
        s = make_store(td)
        pid = s.create_profile("Test", "not-a-real-pin")
        eid, rev1 = s.upsert_entity(profile_id=pid, entity_type="memo", title="A",
                                    payload={"body":"eins"})
        assert rev1 == 1
        obj = s.get_entity(eid)
        assert obj["payload"]["body"] == "eins"
        eid2, rev2 = s.upsert_entity(profile_id=pid, entity_type="memo", title="A",
                                     payload={"body":"zwei"}, entity_id=eid,
                                     expected_revision=1)
        assert eid2 == eid and rev2 == 2
        assert s.integrity_check() == "ok"
        s.close()

def test_revision_conflict_rolls_back():
    with tempfile.TemporaryDirectory() as td:
        s = make_store(td)
        pid = s.create_profile("Test", "hash")
        eid, _ = s.upsert_entity(profile_id=pid, entity_type="todo", title="T",
                                 payload={"done":False})
        try:
            s.upsert_entity(profile_id=pid, entity_type="todo", title="T2",
                            payload={"done":True}, entity_id=eid, expected_revision=99)
            raise AssertionError("conflict expected")
        except RuntimeError as e:
            assert str(e) == "REVISION_CONFLICT"
        assert s.get_entity(eid)["revision"] == 1
        s.close()

def test_soft_delete_is_not_hard_delete():
    with tempfile.TemporaryDirectory() as td:
        s = make_store(td)
        pid = s.create_profile("Test", "hash")
        eid, _ = s.upsert_entity(profile_id=pid, entity_type="memo", title="T",
                                 payload={"body":"safe"})
        rev = s.soft_delete(eid, expected_revision=1)
        obj = s.get_entity(eid)
        assert rev == 2 and obj["status"] == "TRASHED"
        s.close()

def test_atomic_write():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td)/"a.txt"
        atomic_write_bytes(p, b"provoware")
        assert p.read_bytes() == b"provoware"
        assert not list(Path(td).glob("*.tmp"))

def test_backup_restore_verification():
    with tempfile.TemporaryDirectory() as td:
        s = make_store(td)
        pid = s.create_profile("Test", "hash")
        s.upsert_entity(profile_id=pid, entity_type="memo", title="Backup",
                        payload={"body":"recover me"})
        s.close()
        gen = create_verified_backup(Path(td)/"core.sqlite3", Path(td)/"backups")
        assert (gen/"core.sqlite3").exists()
        assert (gen/"manifest.json").exists()

if __name__ == "__main__":
    tests = [v for k,v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        t()
        print("PASS", t.__name__)
    print(f"PASS total={len(tests)}")
