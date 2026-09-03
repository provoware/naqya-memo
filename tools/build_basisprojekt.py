#!/usr/bin/env python3
from __future__ import annotations
import argparse, fnmatch, hashlib, json, os, re, subprocess, sys, zipfile
from pathlib import Path, PurePosixPath
ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/'manifeste'/'MANIFEST_BASISPROJEKT__STATUS-AKTIV__V1.0.json'
ZIP_EPOCH=(1980,1,1,0,0,0)
class BuildError(RuntimeError): pass

def load_contract():
    try:data=json.loads(CONTRACT.read_text(encoding='utf-8'))
    except Exception as exc: raise BuildError(f'Basisprojekt-Manifest ist nicht lesbar: {exc}') from exc
    if data.get('schema_version')!=1 or data.get('status')!='AKTIV': raise BuildError('Basisprojekt-Manifest besitzt keinen aktiven Schema-v1-Vertrag.')
    return data

def excluded(rel,patterns):
    posix=PurePosixPath(rel).as_posix()
    return any(fnmatch.fnmatch(posix,p) for p in patterns)

def collect_files(c):
    pats=list(c['exclude_globs']); files={}
    for name in c['mandatory_root_files']:
        p=ROOT/name
        if not p.is_file(): raise BuildError(f'Pflichtdatei fehlt: {name}')
        files[name]=p
    for rel in c['include_files']:
        p=ROOT/rel
        if not p.is_file(): raise BuildError(f'Freigegebene Basisdatei fehlt: {rel}')
        files[PurePosixPath(rel).as_posix()]=p
    for root_name in c['include_roots']:
        root=ROOT/root_name
        if not root.is_dir(): raise BuildError(f'Freigegebener Basisordner fehlt: {root_name}')
        for p in root.rglob('*'):
            if p.is_file():
                rel=p.relative_to(ROOT).as_posix()
                if not excluded(rel,pats): files[rel]=p
    for rel in files:
        if excluded(rel,pats): raise BuildError(f'Ausgeschlossene Datei würde exportiert: {rel}')
    return [files[k] for k in sorted(files)]

def sha256_file(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def git_head():
    try:return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
    except Exception:return 'UNKNOWN'

def source_version():
    try:return str(json.loads((ROOT/'registry'/'VERSION.json').read_text(encoding='utf-8')).get('version') or 'UNKNOWN')
    except Exception:return 'UNKNOWN'

def generated_manifest(paths,c):
    rows=[{'path':p.relative_to(ROOT).as_posix(),'size':p.stat().st_size,'sha256':sha256_file(p)} for p in paths]
    return {'schema_version':1,'project':c['project'],'source_version':source_version(),'source_git_head':git_head(),'artifact_type':'vollstaendiges_basisprojekt','file_count':len(rows),'files':rows}

def safe_version(v): return re.sub(r'[^A-Za-z0-9._-]+','_',v).strip('._-') or 'UNKNOWN'

def write_zip(paths,m,outdir):
    outdir.mkdir(parents=True,exist_ok=True)
    out=outdir/f"PROVOWARE_Naqya-Memo_BASISPROJEKT_{safe_version(m['source_version'])}.zip"
    tmp=out.with_suffix(out.suffix+'.tmp')
    if tmp.exists(): tmp.unlink()
    with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in paths:
            rel=p.relative_to(ROOT).as_posix(); info=zipfile.ZipInfo(rel,ZIP_EPOCH)
            mode=0o755 if os.access(p,os.X_OK) else 0o644; info.external_attr=(mode&0xFFFF)<<16
            z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
        info=zipfile.ZipInfo('BASISPROJEKT_MANIFEST.json',ZIP_EPOCH); info.external_attr=(0o644&0xFFFF)<<16
        z.writestr(info,(json.dumps(m,ensure_ascii=False,indent=2,sort_keys=True)+'\n').encode('utf-8'),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    os.replace(tmp,out); return out

def verify_zip(path,m):
    expected={r['path']:r for r in m['files']}; expected['BASISPROJEKT_MANIFEST.json']=None
    with zipfile.ZipFile(path) as z:
        names=z.namelist()
        if len(names)!=len(set(names)) or set(names)!=set(expected): raise BuildError('ZIP-Inhalt weicht vom Manifest ab.')
        for rel,row in expected.items():
            if row is None: continue
            data=z.read(rel)
            if len(data)!=row['size'] or hashlib.sha256(data).hexdigest()!=row['sha256']: raise BuildError(f'Integritätsfehler: {rel}')

def main():
    ap=argparse.ArgumentParser(description='Erzeugt das saubere vollständige PROVOWARE-Basisprojekt.')
    ap.add_argument('--output-dir',default=str(ROOT/'dist')); ap.add_argument('--check',action='store_true'); a=ap.parse_args()
    try:
        c=load_contract(); paths=collect_files(c); m=generated_manifest(paths,c)
        if a.check: print(f"PASS basis project contract files={len(paths)} version={m['source_version']}"); return 0
        out=write_zip(paths,m,Path(a.output_dir).resolve()); verify_zip(out,m); print(out); print(f'PASS basis project zip files={len(paths)}'); return 0
    except BuildError as exc:
        print(f'FEHLER BASISPROJEKT: {exc}',file=sys.stderr); return 2
if __name__=='__main__': raise SystemExit(main())
