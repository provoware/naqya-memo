from __future__ import annotations
from pathlib import Path
import os, tempfile

class AtomicWriteError(RuntimeError):
    pass

def atomic_write_bytes(target: Path, data: bytes) -> None:
    """Write a file transactionally in the same directory.

    Safety contract:
    PRE: parent exists and is writable.
    ACTION: temp file -> flush -> fsync -> os.replace.
    POST: caller validates content/hash.
    """
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=str(target.parent))
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, target)
        # Best-effort directory fsync on POSIX; harmlessly skipped elsewhere.
        if hasattr(os, "O_DIRECTORY"):
            try:
                dfd = os.open(str(target.parent), os.O_RDONLY | os.O_DIRECTORY)
                try:
                    os.fsync(dfd)
                finally:
                    os.close(dfd)
            except OSError:
                pass
    except Exception as exc:
        try:
            tmp.unlink(missing_ok=True)
        finally:
            raise AtomicWriteError(str(exc)) from exc
