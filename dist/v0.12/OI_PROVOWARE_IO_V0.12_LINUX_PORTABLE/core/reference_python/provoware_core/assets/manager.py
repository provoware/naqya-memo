from __future__ import annotations
from pathlib import Path
import json, os, shutil, tempfile
from .manager_base import AssetManager as BaseAssetManager, AssetError, sha256_file, utc_now, ALLOWED_TYPES

def atomic_json(path: Path, payload: dict) -> None:
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=f'.{path.name}.',suffix='.tmp',dir=str(path.parent))
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as f:
            json.dump(payload,f,indent=2,ensure_ascii=False); f.flush(); os.fsync(f.fileno())
        os.replace(tmp,path)
    except Exception:
        Path(tmp).unlink(missing_ok=True)
        raise

class AssetManager(BaseAssetManager):
    '''V0.12 crash-recoverable AssetManager.

    Transaction states: STAGING -> STAGED -> FILE_COMMITTED -> MANIFEST_COMMITTED.
    The journal is intentionally tiny and stores enough data to finish or roll
    back safely after a process kill.
    '''
    def __init__(self, project_dir: Path, quota_bytes: int = 2*1024*1024*1024):
        super().__init__(project_dir,quota_bytes)
        self.transactions=self.project/'temp'/'asset-transaktionen'
        self.transactions.mkdir(parents=True,exist_ok=True)

    def _phase(self, hook, name: str):
        if hook is not None: hook(name)

    def _manifest_from_txn(self, tx: dict) -> dict:
        return {
            'asset_id':tx['asset_id'],'kind':tx['kind'],'title':tx['title'],
            'original_name':tx['original_name'],'stored_name':tx['stored_name'],
            'size_bytes':tx['size_bytes'],'sha256':tx['sha256'],
            'created_at':tx['created_at'],'status':'ACTIVE','revision':1,
        }

    def import_asset(self, source: Path, kind: str, title: str = '', _phase_hook=None) -> dict:
        import uuid
        source=Path(source); size=self._validate_source(source,kind)
        asset_id=str(uuid.uuid4()); ext=source.suffix.lower()
        kind_dir=self.data/kind; kind_dir.mkdir(parents=True,exist_ok=True)
        final=kind_dir/f'{asset_id}{ext}'; tmp=self.temp/f'{asset_id}{ext}.part'
        txn_path=self.transactions/f'{asset_id}.json'
        tx={'asset_id':asset_id,'kind':kind,'title':title or source.stem,'original_name':source.name,
            'stored_name':final.name,'size_bytes':size,'created_at':utc_now(),'state':'STAGING',
            'tmp_path':str(tmp.relative_to(self.project)),'final_path':str(final.relative_to(self.project))}
        atomic_json(txn_path,tx); self._phase(_phase_hook,'journal_created')
        try:
            with open(source,'rb') as src, open(tmp,'wb') as dst:
                shutil.copyfileobj(src,dst,1024*1024); dst.flush(); os.fsync(dst.fileno())
            tx['sha256']=sha256_file(tmp); tx['state']='STAGED'; atomic_json(txn_path,tx)
            self._phase(_phase_hook,'staged')
            os.replace(tmp,final)
            tx['state']='FILE_COMMITTED'; atomic_json(txn_path,tx)
            self._phase(_phase_hook,'file_committed')
            manifest=self._manifest_from_txn(tx); mpath=self.manifests/f'{asset_id}.json'
            atomic_json(mpath,manifest)
            tx['state']='MANIFEST_COMMITTED'; atomic_json(txn_path,tx)
            self._phase(_phase_hook,'manifest_committed')
            txn_path.unlink(missing_ok=True)
            return manifest
        except Exception:
            # The journal is evidence for recovery. Only a definitely partial
            # first-stage file is removed immediately.
            if tmp.exists() and tx.get('state')=='STAGING': tmp.unlink(missing_ok=True)
            raise

    def recover_incomplete_transactions(self) -> dict:
        recovered=[]; rolled_back=[]; errors=[]
        for txn_path in sorted(self.transactions.glob('*.json')):
            try:
                tx=json.loads(txn_path.read_text(encoding='utf-8')); aid=tx['asset_id']
                tmp=self.project/tx['tmp_path']; final=self.project/tx['final_path']; manifest_path=self.manifests/f'{aid}.json'
                expected=tx.get('sha256')
                if manifest_path.exists():
                    self.validate_asset(aid); tmp.unlink(missing_ok=True); txn_path.unlink(missing_ok=True)
                    recovered.append({'asset_id':aid,'action':'FINALIZED_EXISTING_MANIFEST'}); continue
                if final.exists() and expected and sha256_file(final)==expected:
                    atomic_json(manifest_path,self._manifest_from_txn(tx)); tmp.unlink(missing_ok=True); txn_path.unlink(missing_ok=True)
                    recovered.append({'asset_id':aid,'action':'REBUILT_MANIFEST'}); continue
                tmp.unlink(missing_ok=True)
                if final.exists():
                    q=self.quarantine/f'{aid}_{final.name}'; shutil.move(str(final),str(q))
                    rolled_back.append({'asset_id':aid,'action':'QUARANTINED_UNCERTAIN_FINAL'})
                else:
                    rolled_back.append({'asset_id':aid,'action':'ROLLED_BACK_STAGING'})
                txn_path.unlink(missing_ok=True)
            except Exception as exc:
                errors.append({'transaction':txn_path.name,'error':repr(exc)})
        return {'recovered':recovered,'rolled_back':rolled_back,'errors':errors}
