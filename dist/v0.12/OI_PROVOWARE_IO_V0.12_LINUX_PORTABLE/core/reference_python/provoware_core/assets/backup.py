from __future__ import annotations
from pathlib import Path
import json, shutil
from .manager import sha256_file

def backup_assets(asset_manager, backup_dir: Path) -> dict:
    backup_dir=Path(backup_dir)
    target=backup_dir/"assets"
    if target.exists(): shutil.rmtree(target)
    target.mkdir(parents=True)
    copied=[]
    for manifest_file in asset_manager.manifests.glob("*.json"):
        m=json.loads(manifest_file.read_text(encoding="utf-8"))
        if m.get("status")!="ACTIVE": continue
        src=asset_manager.data/m["kind"]/m["stored_name"]
        if not src.exists(): raise RuntimeError("ASSET_BACKUP_SOURCE_MISSING")
        dst=target/m["kind"]/m["stored_name"]
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(src,dst)
        if sha256_file(dst)!=m["sha256"]: raise RuntimeError("ASSET_BACKUP_HASH_MISMATCH")
        shutil.copy2(manifest_file,target/f"{m['asset_id']}.manifest.json")
        copied.append(m["asset_id"])
    return {"copied":copied,"count":len(copied)}
