from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import os, shutil, tempfile, uuid
from .atomic import atomic_write_bytes
from .store import utc_now

REQUIRED_DIRS=("daten","daten/assets","daten/assets/audio","daten/assets/dokumente","daten/assets/bilder","export","papierkorb","backups","temp","manifeste","nutzer-einstellungen")

@dataclass
class ProjectPreflight:
    ok: bool
    traffic: str
    project_path: str
    created: bool
    writable: bool
    free_bytes: int
    required_free_bytes: int
    directories_ready: list[str]
    warnings: list[str]
    errors: list[str]
    def as_dict(self): return asdict(self)

class ProjectFolderService:
    def __init__(self, minimum_free_bytes: int = 128*1024*1024):
        self.minimum_free_bytes=minimum_free_bytes

    def preflight(self, path: Path, *, create: bool = True) -> ProjectPreflight:
        path=Path(path).expanduser()
        created=False; warnings=[]; errors=[]; dirs=[]
        if path.exists() and not path.is_dir():
            return ProjectPreflight(False,"RED",str(path),False,False,0,self.minimum_free_bytes,[],[],["PROJECT_PATH_IS_NOT_DIRECTORY"])
        if not path.exists():
            if not create:
                return ProjectPreflight(False,"RED",str(path),False,False,0,self.minimum_free_bytes,[],[],["PROJECT_FOLDER_MISSING"])
            path.mkdir(parents=True, exist_ok=False); created=True
        for rel in REQUIRED_DIRS:
            p=path/rel; p.mkdir(parents=True, exist_ok=True); dirs.append(rel)
        writable=self._write_probe(path/'temp')
        usage=shutil.disk_usage(path)
        if not writable: errors.append("PROJECT_FOLDER_NOT_WRITABLE")
        if usage.free < self.minimum_free_bytes: errors.append("LOW_DISK_SPACE")
        traffic="GREEN" if not errors else "RED"
        return ProjectPreflight(not errors,traffic,str(path.resolve()),created,writable,usage.free,self.minimum_free_bytes,dirs,warnings,errors)

    def _write_probe(self, temp_dir: Path) -> bool:
        probe=temp_dir/(".write_probe_"+uuid.uuid4().hex)
        try:
            atomic_write_bytes(probe,b"provoware-write-probe")
            return probe.read_bytes()==b"provoware-write-probe"
        except Exception:
            return False
        finally:
            probe.unlink(missing_ok=True)
