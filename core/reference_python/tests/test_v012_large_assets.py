from pathlib import Path
import tempfile, sys, json, time
ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(ROOT/'core/reference_python'))
from provoware_core.assets import AssetManager
from provoware_core.assets.backup import backup_assets
with tempfile.TemporaryDirectory() as td:
    b=Path(td); am=AssetManager(b/'project',quota_bytes=256*1024*1024); audio=b/'template.wav'; audio.write_bytes(b'RIFF'+b'\0'*(2*1024*1024-4)); pdf=b/'template.pdf'; pdf.write_bytes(b'%PDF-1.4\n'+b'\0'*(2*1024*1024-9)); ids=[]; t0=time.perf_counter()
    for i in range(20): ids.append(am.import_asset(audio,'audio',f'Audio {i}')['asset_id'])
    for i in range(20): ids.append(am.import_asset(pdf,'document',f'PDF {i}')['asset_id'])
    import_s=time.perf_counter()-t0; t1=time.perf_counter(); br=backup_assets(am,b/'backup'); backup_s=time.perf_counter()-t1; valid=sum(1 for aid in ids if am.validate_asset(aid)); q=am.quota_status()
    result={'assets':len(ids),'verified':valid,'used_bytes':q['used'],'import_seconds':round(import_s,3),'backup_seconds':round(backup_s,3),'backup_count':br['count'],'pass':len(ids)==40 and valid==40 and br['count']==40 and q['used']>=80*1024*1024}
    print(json.dumps(result)); raise SystemExit(0 if result['pass'] else 1)
