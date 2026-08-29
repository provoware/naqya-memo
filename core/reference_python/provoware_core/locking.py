from __future__ import annotations
from pathlib import Path
import os, time, json

class ProjectLockError(RuntimeError):
    pass

class ProjectLock:
    """Portable conservative lock-file guard.

    The lock contains PID and timestamp. A stale lock may be recovered only
    after the owner PID is proven absent on the local system.
    """
    def __init__(self, project_dir: Path, filename: str = ".provoware.lock"):
        self.project_dir = Path(project_dir)
        self.path = self.project_dir / filename
        self.acquired = False

    def acquire(self):
        self.project_dir.mkdir(parents=True, exist_ok=True)
        payload = {"pid": os.getpid(), "created_at": time.time()}
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
        try:
            fd = os.open(self.path, flags, 0o600)
        except FileExistsError:
            if self._is_stale():
                self.path.unlink(missing_ok=True)
                fd = os.open(self.path, flags, 0o600)
            else:
                raise ProjectLockError("PROJECT_ALREADY_LOCKED")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f)
            f.flush()
            os.fsync(f.fileno())
        self.acquired = True
        return self

    def release(self):
        if self.acquired:
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                if int(data.get("pid", -1)) == os.getpid():
                    self.path.unlink(missing_ok=True)
            finally:
                self.acquired = False

    def _is_stale(self) -> bool:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            pid = int(data.get("pid", -1))
        except Exception:
            return True
        if pid <= 0:
            return True
        if os.name == "posix":
            try:
                os.kill(pid, 0)
                return False
            except ProcessLookupError:
                return True
            except PermissionError:
                return False
        # Conservative fallback on platforms without a safe PID probe.
        return False

    def __enter__(self):
        return self.acquire()

    def __exit__(self, exc_type, exc, tb):
        self.release()
