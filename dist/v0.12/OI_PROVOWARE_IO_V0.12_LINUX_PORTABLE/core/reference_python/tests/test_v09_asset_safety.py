from pathlib import Path
import tempfile, os, json
ROOT=Path(__file__).resolve().parents[3]
import sys
sys.path.insert(0,str(ROOT/"core/reference_python"))
from provoware_core.assets import AssetManager, AssetError
from provoware_core.assets.backup import backup_assets
from provoware_core import CoreStore, MutationQueue
from provoware_core.modules import PlaylistService
SCHEMA=ROOT/"schemas"/"core_schema_v2.sql"

def test_audio_import_manifest_hash_and_quota():
    with tempfile.TemporaryDirectory() as td:
        base=Path(td); src=base/"in.wav"; src.write_bytes(b"RIFF"+b"x"*100)
        am=AssetManager(base/"project",quota_bytes=10000)
        m=am.import_asset(src,"audio","Test")
        assert m["kind"]=="audio" and len(m["sha256"])==64
        assert am.validate_asset(m["asset_id"])["asset_id"]==m["asset_id"]
        assert am.quota_status()["used"]==src.stat().st_size

def test_document_extension_guard():
    with tempfile.TemporaryDirectory() as td:
        base=Path(td); src=base/"evil.exe"; src.write_bytes(b"x")
        am=AssetManager(base/"project")
        try: am.import_asset(src,"document")
        except AssetError as e: assert str(e)=="ASSET_EXTENSION_BLOCKED"
        else: raise AssertionError("blocked extension expected")

def test_quota_guard():
    with tempfile.TemporaryDirectory() as td:
        base=Path(td); src=base/"big.wav"; src.write_bytes(b"x"*200)
        am=AssetManager(base/"project",quota_bytes=100)
        try: am.import_asset(src,"audio")
        except AssetError as e: assert str(e)=="ASSET_QUOTA_EXCEEDED"
        else: raise AssertionError("quota expected")

def test_corrupt_asset_moves_to_quarantine():
    with tempfile.TemporaryDirectory() as td:
        base=Path(td); src=base/"a.wav"; src.write_bytes(b"abc")
        am=AssetManager(base/"project"); m=am.import_asset(src,"audio")
        stored=am.data/"audio"/m["stored_name"]; stored.write_bytes(b"tampered")
        r=am.validate_or_quarantine(m["asset_id"])
        assert r["status"]=="QUARANTINED"
        assert not stored.exists()
        assert any(am.quarantine.iterdir())

def test_asset_backup_verifies_hash():
    with tempfile.TemporaryDirectory() as td:
        base=Path(td); src=base/"a.pdf"; src.write_bytes(b"%PDF-1.4\nhello")
        am=AssetManager(base/"project"); m=am.import_asset(src,"document")
        r=backup_assets(am,base/"backup")
        assert r["count"]==1 and m["asset_id"] in r["copied"]

def test_playlist_persistent():
    with tempfile.TemporaryDirectory() as td:
        base=Path(td); s=CoreStore(base/"db.sqlite3",SCHEMA); pid=s.create_profile("P","hash"); q=MutationQueue();q.start()
        svc=PlaylistService(s,q); eid,rev=svc.create(pid,"Mix"); svc.add_asset(eid,pid,rev,"asset-1")
        obj=s.get_entity(eid); assert obj["payload"]["items"]==["asset-1"]
        q.stop();s.close()

if __name__=="__main__":
    tests=[v for k,v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    bad=[]
    for t in tests:
        try:t();print("PASS",t.__name__)
        except Exception as e:bad.append((t.__name__,repr(e)));print("FAIL",t.__name__,repr(e))
    print(f"SUMMARY total={len(tests)} passed={len(tests)-len(bad)} failed={len(bad)}")
    if bad:raise SystemExit(1)
