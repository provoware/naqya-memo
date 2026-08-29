from __future__ import annotations
from pathlib import Path
import sqlite3, json, shutil, datetime, uuid
from provoware_core.assets.manager import sha256_file, atomic_json

def create_project_checkpoint(db_path: Path, asset_manager, backup_root: Path) -> Path:
    backup_root=Path(backup_root); backup_root.mkdir(parents=True,exist_ok=True)
    gen=backup_root/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S')+'_'+uuid.uuid4().hex[:8]); gen.mkdir()
    db_out=gen/'core.sqlite3'; src=sqlite3.connect(db_path); dst=sqlite3.connect(db_out)
    try: src.backup(dst); dst.commit()
    finally: src.close(); dst.close()
    dbc=sha256_file(db_out); c=sqlite3.connect(db_out)
    try: integ=c.execute('PRAGMA integrity_check').fetchone()[0]
    finally: c.close()
    if integ!='ok': raise RuntimeError('CHECKPOINT_DB_INTEGRITY_FAILED')
    assets=[]
    for m in asset_manager.list_assets():
        srcp=asset_manager.path_for(m['asset_id']); dstp=gen/'assets'/m['kind']/m['stored_name']; dstp.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(srcp,dstp)
        if sha256_file(dstp)!=m['sha256']: raise RuntimeError('CHECKPOINT_ASSET_HASH_MISMATCH')
        mf=gen/'manifeste'/'assets'/f"{m['asset_id']}.json"; mf.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(asset_manager.manifests/f"{m['asset_id']}.json",mf)
        assets.append({'asset_id':m['asset_id'],'kind':m['kind'],'stored_name':m['stored_name'],'sha256':m['sha256']})
    manifest={'format':'OI_PROVOWARE_CHECKPOINT','version':1,'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'database':{'file':'core.sqlite3','sha256':dbc,'integrity':'ok'},'assets':assets}
    atomic_json(gen/'checkpoint_manifest.json',manifest); return gen

def validate_project_checkpoint(gen: Path) -> dict:
    gen=Path(gen); mp=gen/'checkpoint_manifest.json'
    if not mp.exists(): raise RuntimeError('CHECKPOINT_MANIFEST_MISSING')
    m=json.loads(mp.read_text(encoding='utf-8')); db=gen/m['database']['file']
    if sha256_file(db)!=m['database']['sha256']: raise RuntimeError('CHECKPOINT_DB_HASH_MISMATCH')
    c=sqlite3.connect(db)
    try: integ=c.execute('PRAGMA integrity_check').fetchone()[0]
    finally: c.close()
    if integ!='ok': raise RuntimeError('CHECKPOINT_DB_INTEGRITY_FAILED')
    for a in m['assets']:
        p=gen/'assets'/a['kind']/a['stored_name']
        if not p.exists(): raise RuntimeError('CHECKPOINT_ASSET_MISSING')
        if sha256_file(p)!=a['sha256']: raise RuntimeError('CHECKPOINT_ASSET_HASH_MISMATCH')
    return m

def restore_project_checkpoint(gen: Path, fresh_project: Path) -> dict:
    m=validate_project_checkpoint(gen); fresh_project=Path(fresh_project)
    if fresh_project.exists() and any(fresh_project.iterdir()): raise RuntimeError('RESTORE_TARGET_NOT_EMPTY')
    (fresh_project/'daten').mkdir(parents=True,exist_ok=True); shutil.copy2(Path(gen)/m['database']['file'],fresh_project/'daten'/'core.sqlite3')
    for a in m['assets']:
        src=Path(gen)/'assets'/a['kind']/a['stored_name']; dst=fresh_project/'daten'/'assets'/a['kind']/a['stored_name']; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
        ms=Path(gen)/'manifeste'/'assets'/f"{a['asset_id']}.json"; md=fresh_project/'manifeste'/'assets'/f"{a['asset_id']}.json"; md.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(ms,md)
    return validate_restored_project(fresh_project,m)

def validate_restored_project(project: Path, manifest: dict) -> dict:
    project=Path(project); db=project/'daten'/'core.sqlite3'
    if sha256_file(db)!=manifest['database']['sha256']: raise RuntimeError('RESTORED_DB_HASH_MISMATCH')
    c=sqlite3.connect(db)
    try: integ=c.execute('PRAGMA integrity_check').fetchone()[0]
    finally: c.close()
    if integ!='ok': raise RuntimeError('RESTORED_DB_INTEGRITY_FAILED')
    checked=0
    for a in manifest['assets']:
        if sha256_file(project/'daten'/'assets'/a['kind']/a['stored_name'])!=a['sha256']: raise RuntimeError('RESTORED_ASSET_HASH_MISMATCH')
        checked+=1
    return {'database_integrity':integ,'assets_verified':checked}
