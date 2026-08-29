from pathlib import Path
import tempfile, sys, json
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'core/reference_python'))
from provoware_core.assets import AssetManager, AssetError

def test_text_revision_history_and_conflict():
    with tempfile.TemporaryDirectory() as td:
        b=Path(td); src=b/'note.txt'; src.write_text('v1',encoding='utf-8'); am=AssetManager(b/'project'); m=am.import_asset(src,'document','Note')
        out=am.edit_text_asset(m['asset_id'],'v2',1); assert out['revision']==2 and len(out['revision_history'])==1
        assert am.read_text_asset(m['asset_id'])['text']=='v2'
        try:am.edit_text_asset(m['asset_id'],'stale',1)
        except AssetError as e:assert str(e)=='ASSET_REVISION_CONFLICT'
        else:raise AssertionError('conflict expected')

def test_pdf_is_read_only_for_internal_editor():
    with tempfile.TemporaryDirectory() as td:
        b=Path(td); src=b/'a.pdf'; src.write_bytes(b'%PDF-1.4\n%%EOF'); am=AssetManager(b/'project'); m=am.import_asset(src,'document')
        try:am.read_text_asset(m['asset_id'])
        except AssetError as e:assert str(e)=='ASSET_TEXT_EDIT_UNSUPPORTED'
        else:raise AssertionError('PDF edit must be blocked')

if __name__=='__main__':
    tests=[v for k,v in sorted(globals().items()) if k.startswith('test_')]
    bad=[]
    for t in tests:
        try:t();print('PASS',t.__name__)
        except Exception as e:bad.append((t.__name__,repr(e)));print('FAIL',t.__name__,repr(e))
    print(f'SUMMARY total={len(tests)} passed={len(tests)-len(bad)} failed={len(bad)}')
    if bad:raise SystemExit(1)
