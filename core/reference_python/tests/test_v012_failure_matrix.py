from pathlib import Path
import tempfile, sys, os, errno, subprocess, sqlite3
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'core/reference_python'))
from provoware_core.assets import AssetManager
from provoware_core import CoreStore, MutationQueue, MemoService
from provoware_core.backup import create_verified_backup
from provoware_core.recovery import validate_backup_generation
from provoware_core.project_checkpoint import create_project_checkpoint, restore_project_checkpoint
SCHEMA=ROOT/'schemas'/'core_schema_v2.sql'; WORKER=ROOT/'core/reference_python/tools/asset_kill_worker.py'

def test_disk_full_during_asset_commit_is_recoverable():
    with tempfile.TemporaryDirectory() as td:
        b=Path(td); src=b/'a.wav'; src.write_bytes(b'RIFF'+b'x'*1024); am=AssetManager(b/'p'); original=os.replace
        def fail_replace(a,bp):
            if str(a).endswith('.part'): raise OSError(errno.ENOSPC,'No space left on device')
            return original(a,bp)
        try:
            with patch('provoware_core.assets.manager.os.replace',side_effect=fail_replace): am.import_asset(src,'audio')
        except OSError as e: assert e.errno==errno.ENOSPC
        else: raise AssertionError('ENOSPC expected')
        rec=am.recover_incomplete_transactions(); assert not list((am.data/'audio').glob('*')); assert rec['errors']==[]

def test_permission_denied_during_stage_has_no_final_asset():
    with tempfile.TemporaryDirectory() as td:
        b=Path(td); src=b/'a.wav'; src.write_bytes(b'RIFFx'); am=AssetManager(b/'p'); real_open=open
        def guarded(path,*args,**kwargs):
            if str(path).endswith('.part'): raise PermissionError(errno.EACCES,'Permission denied')
            return real_open(path,*args,**kwargs)
        try:
            with patch('builtins.open',side_effect=guarded): am.import_asset(src,'audio')
        except PermissionError: pass
        else: raise AssertionError('permission error expected')
        am.recover_incomplete_transactions(); assert not list((am.data/'audio').glob('*'))

def test_asset_kill_phases_recover():
    for phase in ('journal_created','staged','file_committed','manifest_committed'):
        with tempfile.TemporaryDirectory() as td:
            b=Path(td); project=b/'p'; src=b/'a.wav'; src.write_bytes(b'RIFF'+b'x'*4096)
            p=subprocess.run([sys.executable,str(WORKER),str(ROOT),str(project),str(src),phase],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            assert p.returncode!=0
            am=AssetManager(project); rec=am.recover_incomplete_transactions(); active=am.list_assets()
            if phase in ('file_committed','manifest_committed'): assert len(active)==1 and am.validate_asset(active[0]['asset_id'])
            else: assert len(active)==0
            assert rec['errors']==[]

def test_corrupted_db_backup_rejected():
    with tempfile.TemporaryDirectory() as td:
        b=Path(td); s=CoreStore(b/'db.sqlite3',SCHEMA); s.create_profile('P','hash'); s.close(); gen=create_verified_backup(b/'db.sqlite3',b/'backups'); db=gen/'core.sqlite3'
        with open(db,'r+b') as f: f.seek(0); f.write(b'BROKEN!!')
        try: validate_backup_generation(gen)
        except RuntimeError: pass
        else: raise AssertionError('corrupted db backup must fail')

def test_corrupted_asset_quarantined():
    with tempfile.TemporaryDirectory() as td:
        b=Path(td); src=b/'a.pdf'; src.write_bytes(b'%PDF-1.4\nX'); am=AssetManager(b/'p'); m=am.import_asset(src,'document'); am.path_for(m['asset_id']).write_bytes(b'tampered')
        r=am.validate_or_quarantine(m['asset_id']); assert r['status']=='QUARANTINED'

def test_full_checkpoint_restore_db_and_assets():
    with tempfile.TemporaryDirectory() as td:
        b=Path(td); project=b/'project'; am=AssetManager(project); s=CoreStore(project/'daten/core.sqlite3',SCHEMA); pid=s.create_profile('P','hash'); q=MutationQueue(); q.start(); memo=MemoService(s,q); mid,_=memo.create(pid,'Restore','works')
        src=b/'a.pdf'; src.write_bytes(b'%PDF-1.4\nrestore'); am.import_asset(src,'document'); gen=create_project_checkpoint(project/'daten/core.sqlite3',am,b/'checkpoints'); out=restore_project_checkpoint(gen,b/'fresh')
        assert out['database_integrity']=='ok' and out['assets_verified']==1
        c=sqlite3.connect(b/'fresh/daten/core.sqlite3'); assert c.execute('SELECT COUNT(*) FROM entities WHERE id=?',(mid,)).fetchone()[0]==1; c.close(); q.stop(); s.close()

if __name__=='__main__':
    tests=[v for k,v in sorted(globals().items()) if k.startswith('test_') and callable(v)]; bad=[]
    for t in tests:
        try:t();print('PASS',t.__name__)
        except Exception as e:bad.append((t.__name__,repr(e)));print('FAIL',t.__name__,repr(e))
    print(f'SUMMARY total={len(tests)} passed={len(tests)-len(bad)} failed={len(bad)}')
    if bad:raise SystemExit(1)
