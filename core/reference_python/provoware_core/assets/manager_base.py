from __future__ import annotations
from pathlib import Path
import hashlib, json, os, shutil, tempfile, uuid, datetime

ALLOWED_TYPES = {
    "audio": {".wav",".mp3",".ogg",".m4a",".flac"},
    "document": {".pdf",".txt",".md",".rtf",".docx"},
}

class AssetError(RuntimeError): pass

def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

class AssetManager:
    """Crash-safe asset intake.

    PRE: source exists, extension allowed, quota available.
    ACTION: copy into temp/staging, fsync, hash.
    POST: atomic replace into final asset path + manifest.
    """
    def __init__(self, project_dir: Path, quota_bytes: int = 2*1024*1024*1024):
        self.project=Path(project_dir)
        self.data=self.project/"daten"/"assets"
        self.temp=self.project/"temp"/"assets"
        self.quarantine=self.project/"daten"/"quarantaene"
        self.manifests=self.project/"manifeste"/"assets"
        for p in (self.data,self.temp,self.quarantine,self.manifests): p.mkdir(parents=True,exist_ok=True)
        self.quota_bytes=int(quota_bytes)

    def used_bytes(self) -> int:
        return sum(p.stat().st_size for p in self.data.rglob("*") if p.is_file())

    def quota_status(self) -> dict:
        used=self.used_bytes()
        return {"used":used,"quota":self.quota_bytes,"free":max(0,self.quota_bytes-used),"percent":round((used/self.quota_bytes*100) if self.quota_bytes else 100,2)}

    def _validate_source(self, source: Path, kind: str):
        source=Path(source)
        if not source.is_file(): raise AssetError("ASSET_SOURCE_NOT_FOUND")
        if kind not in ALLOWED_TYPES: raise AssetError("ASSET_KIND_UNSUPPORTED")
        if source.suffix.lower() not in ALLOWED_TYPES[kind]: raise AssetError("ASSET_EXTENSION_BLOCKED")
        size=source.stat().st_size
        if self.used_bytes()+size>self.quota_bytes: raise AssetError("ASSET_QUOTA_EXCEEDED")
        return size

    def import_asset(self, source: Path, kind: str, title: str = "") -> dict:
        source=Path(source); size=self._validate_source(source,kind)
        asset_id=str(uuid.uuid4())
        ext=source.suffix.lower()
        kind_dir=self.data/kind
        kind_dir.mkdir(parents=True,exist_ok=True)
        final=kind_dir/f"{asset_id}{ext}"
        tmp=self.temp/f"{asset_id}{ext}.part"
        with open(source,"rb") as src, open(tmp,"wb") as dst:
            shutil.copyfileobj(src,dst,1024*1024)
            dst.flush(); os.fsync(dst.fileno())
        digest=sha256_file(tmp)
        os.replace(tmp,final)
        manifest={
            "asset_id":asset_id,
            "kind":kind,
            "title":title or source.stem,
            "original_name":source.name,
            "stored_name":final.name,
            "size_bytes":size,
            "sha256":digest,
            "created_at":utc_now(),
            "status":"ACTIVE",
        }
        mpath=self.manifests/f"{asset_id}.json"
        data=json.dumps(manifest,indent=2,ensure_ascii=False).encode()
        fd,tmpname=tempfile.mkstemp(prefix=f".{asset_id}.",suffix=".json.tmp",dir=str(self.manifests))
        with os.fdopen(fd,"wb") as f:
            f.write(data); f.flush(); os.fsync(f.fileno())
        os.replace(tmpname,mpath)
        return manifest

    def validate_asset(self, asset_id: str) -> dict:
        mpath=self.manifests/f"{asset_id}.json"
        if not mpath.exists(): raise AssetError("ASSET_MANIFEST_MISSING")
        manifest=json.loads(mpath.read_text(encoding="utf-8"))
        final=self.data/manifest["kind"]/manifest["stored_name"]
        if not final.exists(): raise AssetError("ASSET_FILE_MISSING")
        actual=sha256_file(final)
        if actual!=manifest["sha256"]: raise AssetError("ASSET_CHECKSUM_MISMATCH")
        return manifest

    def quarantine_asset(self, asset_id: str, reason: str) -> Path:
        mpath=self.manifests/f"{asset_id}.json"
        if not mpath.exists(): raise AssetError("ASSET_MANIFEST_MISSING")
        manifest=json.loads(mpath.read_text(encoding="utf-8"))
        src=self.data/manifest["kind"]/manifest["stored_name"]
        target=self.quarantine/manifest["stored_name"]
        if src.exists(): shutil.move(str(src),str(target))
        manifest["status"]="QUARANTINED"
        manifest["quarantine_reason"]=reason
        manifest["quarantined_at"]=utc_now()
        mpath.write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
        return target

    def validate_or_quarantine(self, asset_id: str) -> dict:
        try:
            return {"status":"OK","manifest":self.validate_asset(asset_id)}
        except AssetError as e:
            if str(e)=="ASSET_CHECKSUM_MISMATCH":
                self.quarantine_asset(asset_id,"CHECKSUM_MISMATCH")
                return {"status":"QUARANTINED","reason":"CHECKSUM_MISMATCH"}
            raise


    def list_assets(self, kind: str | None = None, include_quarantine: bool = False) -> list[dict]:
        result=[]
        for mf in sorted(self.manifests.glob("*.json")):
            try: manifest=json.loads(mf.read_text(encoding="utf-8"))
            except Exception: continue
            if kind and manifest.get("kind")!=kind: continue
            if not include_quarantine and manifest.get("status")!="ACTIVE": continue
            result.append(manifest)
        result.sort(key=lambda x:x.get("created_at",""),reverse=True)
        return result

    def path_for(self, asset_id: str) -> Path:
        manifest=self.validate_asset(asset_id)
        return self.data/manifest["kind"]/manifest["stored_name"]

    def read_text_asset(self, asset_id: str) -> dict:
        manifest=self.validate_asset(asset_id)
        ext=Path(manifest["stored_name"]).suffix.lower()
        if ext not in {".txt",".md"}: raise AssetError("ASSET_TEXT_EDIT_UNSUPPORTED")
        path=self.data/manifest["kind"]/manifest["stored_name"]
        return {"manifest":manifest,"text":path.read_text(encoding="utf-8")}

    def edit_text_asset(self, asset_id: str, text: str, expected_revision: int | None = None) -> dict:
        mpath=self.manifests/f"{asset_id}.json"
        if not mpath.exists(): raise AssetError("ASSET_MANIFEST_MISSING")
        manifest=json.loads(mpath.read_text(encoding="utf-8"))
        if manifest.get("status")!="ACTIVE": raise AssetError("ASSET_NOT_ACTIVE")
        ext=Path(manifest["stored_name"]).suffix.lower()
        if ext not in {".txt",".md"}: raise AssetError("ASSET_TEXT_EDIT_UNSUPPORTED")
        current_revision=int(manifest.get("revision",1))
        if expected_revision is not None and current_revision!=int(expected_revision): raise AssetError("ASSET_REVISION_CONFLICT")
        path=self.data/manifest["kind"]/manifest["stored_name"]
        if sha256_file(path)!=manifest["sha256"]: raise AssetError("ASSET_CHECKSUM_MISMATCH")
        revdir=self.project/"daten"/"asset-revisionen"/asset_id
        revdir.mkdir(parents=True,exist_ok=True)
        snapshot=revdir/f"r{current_revision:04d}{ext}"
        shutil.copy2(path,snapshot)
        if sha256_file(snapshot)!=manifest["sha256"]: raise AssetError("ASSET_REVISION_SNAPSHOT_MISMATCH")
        fd,tmpname=tempfile.mkstemp(prefix=f".{asset_id}.",suffix=ext+".tmp",dir=str(self.temp))
        with os.fdopen(fd,"w",encoding="utf-8") as f:
            f.write(text); f.flush(); os.fsync(f.fileno())
        digest=sha256_file(Path(tmpname))
        os.replace(tmpname,path)
        history=list(manifest.get("revision_history",[]))
        history.append({"revision":current_revision,"sha256":manifest["sha256"],"snapshot":str(snapshot.relative_to(self.project)),"saved_at":utc_now()})
        manifest["revision"]=current_revision+1
        manifest["revision_history"]=history[-50:]
        manifest["sha256"]=digest
        manifest["size_bytes"]=path.stat().st_size
        manifest["updated_at"]=utc_now()
        fd,mtemp=tempfile.mkstemp(prefix=f".{asset_id}.",suffix=".json.tmp",dir=str(self.manifests))
        with os.fdopen(fd,"w",encoding="utf-8") as f:
            json.dump(manifest,f,indent=2,ensure_ascii=False); f.flush(); os.fsync(f.fileno())
        os.replace(mtemp,mpath)
        return manifest
