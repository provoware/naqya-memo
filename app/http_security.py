from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from urllib.parse import unquote, urlparse

SERVICE_ID = "oi-provoware-io"
DEFAULT_JSON_BODY_MAX_BYTES = 2 * 1024 * 1024


def project_fingerprint(path: Path) -> str:
    """Stable local identity without disclosing the absolute project path."""
    resolved = str(Path(path).expanduser().resolve())
    return sha256(resolved.encode("utf-8")).hexdigest()


def resolve_static_path(ui_root: Path, request_target: str) -> Path | None:
    """Resolve a URL path only when it remains inside the UI root."""
    root = Path(ui_root).resolve()
    raw_path = unquote(urlparse(request_target).path)
    candidate = (root / raw_path.lstrip("/")).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


def host_is_loopback(host_header: str | None, port: int) -> bool:
    host = (host_header or "").strip().lower()
    return host in {f"127.0.0.1:{port}", f"localhost:{port}"}


def origin_is_same_loopback(origin_header: str | None, port: int) -> bool:
    """Browsers may omit Origin for same-origin legacy/local requests; reject foreign ones."""
    origin = (origin_header or "").strip()
    if not origin:
        return True
    try:
        parsed = urlparse(origin)
        origin_port = parsed.port
    except ValueError:
        return False
    return (
        parsed.scheme == "http"
        and (parsed.hostname or "").lower() in {"127.0.0.1", "localhost"}
        and origin_port == port
    )
