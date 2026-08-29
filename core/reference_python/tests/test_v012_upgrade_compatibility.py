from pathlib import Path
import tempfile, sys, json
ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(ROOT/'core/reference_python'))
from provoware_core import CoreStore
from provoware_core.assets import AssetManager
SCHEMA=ROOT/'schemas'/'core_schema_v2.sql'
def test_v010_v011_compatible_project_fixture():
    with tempfile.TemporaryDirectory() as td:
        b=Path(td); project=b/'v010'; db=project/'daten/core.sqlite3'; db.parent.mkdir(parents=True); s=CoreStore(db,SCHEMA); pid=s.create_profile('Altprojekt','hash'); eid,_=s.upsert_entity(profile_id=pid,entity_type='memo',title='V0.10 Memo',payload={'body':'alt','tags':[],'pinned':False,'archived':False}); s.close()
        src=b/'legacy.pdf'; src.write_bytes(b'%PDF-1.4\nlegacy'); am=AssetManager(project); m=am.import_asset(src,'document','Legacy PDF'); mp=am.manifests/f"{m['asset_id']}.json"; data=json.loads(mp.read_text()); data.pop('revision',None); mp.write_text(json.dumps(data),encoding='utf-8')
        reopened=CoreStore(db,SCHEMA); assert reopened.get_entity(eid)['title']=='V0.10 Memo'; reopened.close(); assert am.validate_asset(m['asset_id'])['title']=='Legacy PDF'
if __name__=='__main__':
    try:test_v010_v011_compatible_project_fixture();print('PASS test_v010_v011_compatible_project_fixture');print('SUMMARY total=1 passed=1 failed=0')
    except Exception as e:print('FAIL',repr(e));print('SUMMARY total=1 passed=0 failed=1');raise
