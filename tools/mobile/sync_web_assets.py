#!/usr/bin/env python3
from pathlib import Path
import shutil, hashlib, json, datetime
ROOT=Path(__file__).resolve().parents[2]
src=ROOT/'ui/reference_web'
targets=[ROOT/'platform/android/app/src/main/assets/www', ROOT/'platform/ios/WebAssets']
for dst in targets:
    if dst.exists(): shutil.rmtree(dst)
    shutil.copytree(src,dst)
files=[]
for p in sorted(src.rglob('*')):
    if p.is_file(): files.append({'file':p.relative_to(src).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
version=json.loads((ROOT/'registry/VERSION.json').read_text(encoding='utf-8')).get('version','UNKNOWN')
numeric=version.split('-',1)[0]
evidence_dir=ROOT/'registry'/'evidence'/f'v{numeric}'; evidence_dir.mkdir(parents=True,exist_ok=True)
out={'version':version,'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':'ui/reference_web','targets':[str(x.relative_to(ROOT)) for x in targets],'files':files}
(evidence_dir/'MOBILE_WEB_BUNDLE_SYNC.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(f'Synced {len(files)} web files to Android and iOS bundles.')
