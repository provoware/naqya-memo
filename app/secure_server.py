#!/usr/bin/env python3
from __future__ import annotations

import base64
import hashlib
import hmac
import math
import os
from pathlib import Path
import secrets
import sqlite3
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[1]
PROJECT = Path(os.environ.get('PROVOWARE_PROJECT_PATH', str(ROOT / 'runtime' / 'projektordner'))).expanduser().resolve()
DB = PROJECT / 'daten' / 'core.sqlite3'
FIRST_PIN_FILE = PROJECT / 'nutzer-einstellungen' / 'ERSTSTART_PIN_EINMAL.txt'


def _active_profile_exists_before_product_import() -> bool:
    """Detect whether the project already owns an active profile.

    This check intentionally runs before importing ``server`` because that module
    creates the reference profile during import. A missing/empty/old database is
    therefore treated as a first-profile bootstrap and hardened immediately after
    the product module has initialized its schema.
    """
    if not DB.is_file():
        return False
    try:
        con = sqlite3.connect(f'file:{DB}?mode=ro', uri=True, timeout=2)
        try:
            row = con.execute("SELECT 1 FROM profiles WHERE status='ACTIVE' LIMIT 1").fetchone()
            return row is not None
        finally:
            con.close()
    except (sqlite3.Error, OSError):
        return False


_HAD_ACTIVE_PROFILE = _active_profile_exists_before_product_import()

import server as base

AUTH_REALM = 'PROVOWARE Desktop PIN'
AUTH_USER = 'provoware'
AUTH_CACHE_TTL_SECONDS = max(5, min(int(os.environ.get('PROVOWARE_AUTH_CACHE_TTL','300')), 3600))
AUTH_MAX_DISTINCT_FAILURES = max(3, min(int(os.environ.get('PROVOWARE_AUTH_MAX_FAILURES','5')), 20))
AUTH_FAILURE_WINDOW_SECONDS = max(5, min(int(os.environ.get('PROVOWARE_AUTH_FAILURE_WINDOW','120')), 3600))
AUTH_LOCKOUT_SECONDS = max(1, min(int(os.environ.get('PROVOWARE_AUTH_LOCKOUT_SECONDS','30')), 3600))
_AUTH_CACHE: dict[str, tuple[float, int]] = {}
_AUTH_FAILURES: dict[str, dict[str, float]] = {}
_AUTH_LOCKED_UNTIL: dict[str, float] = {}
_AUTH_LOCK = threading.Lock()


def _write_first_pin_file(pin: str) -> None:
    FIRST_PIN_FILE.parent.mkdir(parents=True, exist_ok=True)
    text = (
        'PROVOWARE – EINMALIGE ERSTSTART-PIN\n'
        '===================================\n\n'
        f'PIN: {pin}\n\n'
        'Diese Datei wurde nur für die erste Anmeldung angelegt.\n'
        'Nach der ersten erfolgreichen Anmeldung löscht PROVOWARE sie automatisch.\n'
        'Bitte die PIN nicht weitergeben.\n'
    )
    fd = os.open(FIRST_PIN_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        os.write(fd, text.encode('utf-8'))
        os.fsync(fd)
    finally:
        os.close(fd)
    os.chmod(FIRST_PIN_FILE, 0o600)


def _remove_first_pin_file() -> None:
    try:
        FIRST_PIN_FILE.unlink(missing_ok=True)
    except OSError:
        # Authentication must not become a false failure after the PIN itself was
        # proven valid. A leftover credential file is reported at next start.
        pass


def _generate_first_pin() -> str:
    """Generate a random PIN compatible with the current four-digit core contract."""
    while True:
        pin = f'{secrets.randbelow(10000):04d}'
        if pin != '0000':
            return pin


def _harden_first_profile_if_needed() -> None:
    if _HAD_ACTIVE_PROFILE:
        return
    # server.py currently bootstraps its development reference profile with 0000.
    # If that upstream contract changes, fail closed instead of guessing.
    if not base.profile_service.verify_access(base.PROFILE_ID, '0000', source='FIRST_PIN_BOOTSTRAP_CHECK'):
        raise RuntimeError('FIRST_PIN_BOOTSTRAP_CONTRACT_CHANGED')
    pin = _generate_first_pin()
    _write_first_pin_file(pin)
    try:
        base.profile_service.change_pin(base.PROFILE_ID, '0000', pin)
    except Exception:
        _remove_first_pin_file()
        raise
    print(f'ERSTSTART_PIN_DATEI: {FIRST_PIN_FILE}', flush=True)


_harden_first_profile_if_needed()


def _authorization_digest(header: str) -> str:
    return hashlib.sha256(header.encode('utf-8')).hexdigest()


def _profile_revision() -> int | None:
    """Return the active profile security revision, failing closed on DB errors."""
    try:
        row = base.store.conn.execute(
            "SELECT revision FROM profiles WHERE id=? AND status='ACTIVE'",
            (base.PROFILE_ID,),
        ).fetchone()
        return int(row[0]) if row is not None else None
    except (sqlite3.Error, OSError, TypeError, ValueError):
        return None


def _cached(header: str) -> bool:
    now=time.monotonic(); key=_authorization_digest(header)
    revision=_profile_revision()
    if revision is None:
        # The security state is global. If it cannot be proven, no credential
        # cached under a previously known state may survive and later resurrect.
        with _AUTH_LOCK:
            _AUTH_CACHE.clear()
        return False
    with _AUTH_LOCK:
        entry=_AUTH_CACHE.get(key)
        if entry is not None:
            expires,cached_revision=entry
            if expires>now and cached_revision==revision:
                return True
        _AUTH_CACHE.pop(key,None)
        return False


def _remember(header: str, revision: int) -> None:
    key=_authorization_digest(header)
    with _AUTH_LOCK:
        _AUTH_CACHE[key]=(time.monotonic()+AUTH_CACHE_TTL_SECONDS,revision)


def _decode_basic(header: str) -> tuple[str,str] | None:
    try:
        scheme, token = header.split(' ',1)
        if scheme.lower()!='basic':
            return None
        raw=base64.b64decode(token.strip(),validate=True).decode('utf-8')
        user,pin=raw.split(':',1)
        return user,pin
    except Exception:
        return None


def _prune_failures_locked(client: str, now: float) -> dict[str, float]:
    failures=_AUTH_FAILURES.setdefault(client,{})
    cutoff=now-AUTH_FAILURE_WINDOW_SECONDS
    stale=[digest for digest,seen in failures.items() if seen<cutoff]
    for digest in stale:
        failures.pop(digest,None)
    if not failures:
        _AUTH_FAILURES.pop(client,None)
        return {}
    return failures


def _retry_after(client: str) -> int:
    now=time.monotonic()
    with _AUTH_LOCK:
        until=_AUTH_LOCKED_UNTIL.get(client,0.0)
        if until<=now:
            _AUTH_LOCKED_UNTIL.pop(client,None)
            return 0
        return max(1,math.ceil(until-now))


def _record_failure(client: str, header: str) -> int:
    """Count distinct wrong credentials, not parallel retries of the same PIN.

    Browsers can fan one Basic-Auth attempt out to many asset requests. Counting
    the Authorization digest once per window avoids locking a user after a single
    typo while still bounding automated PIN enumeration.
    """
    now=time.monotonic(); digest=_authorization_digest(header)
    with _AUTH_LOCK:
        failures=_prune_failures_locked(client,now)
        failures=_AUTH_FAILURES.setdefault(client,failures)
        failures.setdefault(digest,now)
        if len(failures)>=AUTH_MAX_DISTINCT_FAILURES:
            until=now+AUTH_LOCKOUT_SECONDS
            _AUTH_LOCKED_UNTIL[client]=until
            _AUTH_FAILURES.pop(client,None)
            return AUTH_LOCKOUT_SECONDS
        return 0


def _clear_failures(client: str) -> None:
    with _AUTH_LOCK:
        _AUTH_FAILURES.pop(client,None)
        _AUTH_LOCKED_UNTIL.pop(client,None)


class SecureHandler(base.Handler):
    """Fail-closed desktop transport guard around the existing product handler."""

    def end_headers(self):
        """Prevent authenticated memo/profile responses from surviving in caches."""
        self.send_header('Cache-Control','no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma','no-cache')
        self.send_header('Expires','0')
        self.send_header('Vary','Authorization')
        return super().end_headers()

    def _allowed_local_authorities(self) -> set[str]:
        port=str(self.server.server_port)
        return {f'127.0.0.1:{port}',f'localhost:{port}'}

    def _transport_trust_error(self) -> tuple[int,str] | None:
        """Reject DNS-rebinding and cross-site use of the loopback HTTP service."""
        allowed=self._allowed_local_authorities()
        host=self.headers.get('Host','').strip().lower()
        if host not in allowed:
            return 421,'LOCAL_HOST_BLOCKED'
        origin=self.headers.get('Origin','').strip().lower()
        if origin and origin not in {f'http://{authority}' for authority in allowed}:
            return 403,'CROSS_SITE_ORIGIN_BLOCKED'
        fetch_site=self.headers.get('Sec-Fetch-Site','').strip().lower()
        if fetch_site=='cross-site':
            return 403,'CROSS_SITE_REQUEST_BLOCKED'
        return None

    def _reject_transport(self,status: int,code: str) -> None:
        body=(f'PROVOWARE hat eine nicht vertrauenswürdige lokale Browser-Anfrage blockiert ({code}).\n').encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type','text/plain; charset=utf-8')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Length',str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _require_transport_trust(self) -> bool:
        error=self._transport_trust_error()
        if error is None:
            return True
        self._reject_transport(*error)
        return False

    def _challenge(self):
        body=(
            'PROVOWARE ist gesperrt. Im Browser-Benutzerfeld "provoware" '
            'und als Passwort die Profil-PIN eingeben. Bei einem ganz neuen Projekt '
            'steht die einmalige PIN in nutzer-einstellungen/ERSTSTART_PIN_EINMAL.txt.\n'
        ).encode('utf-8')
        self.send_response(401)
        self.send_header('WWW-Authenticate',f'Basic realm="{AUTH_REALM}", charset="UTF-8"')
        self.send_header('Content-Type','text/plain; charset=utf-8')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Length',str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _rate_limited(self,retry_after: int):
        body=(
            'Zu viele unterschiedliche falsche PIN-Versuche. '
            f'Bitte {retry_after} Sekunden warten und dann erneut versuchen.\n'
        ).encode('utf-8')
        self.send_response(429)
        self.send_header('Retry-After',str(retry_after))
        self.send_header('Content-Type','text/plain; charset=utf-8')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Length',str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _authorized(self) -> tuple[bool,int]:
        header=self.headers.get('Authorization','').strip()
        if not header:
            return False,0
        client=self.client_address[0] if self.client_address else 'unknown'
        retry_after=_retry_after(client)
        if retry_after:
            return False,retry_after
        if _cached(header):
            return True,0
        credentials=_decode_basic(header)
        if credentials is None:
            return False,_record_failure(client,header)
        user,pin=credentials
        if not hmac.compare_digest(user,AUTH_USER):
            return False,_record_failure(client,header)
        revision_before=_profile_revision()
        if revision_before is None:
            return False,0
        try:
            ok=base.profile_service.verify_access(base.PROFILE_ID,pin,source='DESKTOP_HTTP_PIN_GATE')
        except Exception:
            return False,_record_failure(client,header)
        revision_after=_profile_revision()
        if ok and revision_after is not None and revision_after==revision_before:
            _remember(header,revision_after)
            _clear_failures(client)
            _remove_first_pin_file()
            return True,0
        if ok:
            # The profile changed while this request was being authenticated.
            # Fail closed and require the browser to authenticate against the new
            # profile revision instead of caching a credential from stale state.
            return False,0
        return False,_record_failure(client,header)

    def _require_auth(self) -> bool:
        authorized,retry_after=self._authorized()
        if authorized:
            return True
        if retry_after:
            self._rate_limited(retry_after)
        else:
            self._challenge()
        return False

    def do_GET(self):
        if not self._require_transport_trust():
            return
        if not self._require_auth():
            return
        return super().do_GET()

    def do_POST(self):
        if not self._require_transport_trust():
            return
        if not self._require_auth():
            return
        return super().do_POST()


def run(port=8765,open_browser=True):
    base.Handler=SecureHandler
    return base.run(port,open_browser)


if __name__=='__main__':
    port=int(os.environ.get('PROVOWARE_PORT','8765'))
    run(port,'--no-browser' not in sys.argv)
