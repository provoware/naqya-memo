#!/usr/bin/env python3
from __future__ import annotations

import base64
import hashlib
import hmac
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
_AUTH_CACHE: dict[str, float] = {}
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


def _cached(header: str) -> bool:
    now=time.monotonic(); key=_authorization_digest(header)
    with _AUTH_LOCK:
        expires=_AUTH_CACHE.get(key,0.0)
        if expires>now:
            return True
        _AUTH_CACHE.pop(key,None)
        return False


def _remember(header: str) -> None:
    key=_authorization_digest(header)
    with _AUTH_LOCK:
        _AUTH_CACHE[key]=time.monotonic()+AUTH_CACHE_TTL_SECONDS


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


class SecureHandler(base.Handler):
    """Fail-closed desktop transport guard around the existing product handler."""

    def _challenge(self):
        body=(
            'PROVOWARE ist gesperrt. Im Browser-Benutzerfeld "provoware" '
            'und als Passwort die Profil-PIN eingeben. Bei einem ganz neuen Projekt '
            'steht die einmalige PIN in nutzer-einstellungen/ERSTSTART_PIN_EINMAL.txt.\n'
        ).encode('utf-8')
        self.send_response(401)
        self.send_header('WWW-Authenticate',f'Basic realm="{AUTH_REALM}", charset="UTF-8"')
        self.send_header('Content-Type','text/plain; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Length',str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _authorized(self) -> bool:
        header=self.headers.get('Authorization','').strip()
        if not header:
            return False
        if _cached(header):
            return True
        credentials=_decode_basic(header)
        if credentials is None:
            return False
        user,pin=credentials
        if not hmac.compare_digest(user,AUTH_USER):
            return False
        try:
            ok=base.profile_service.verify_access(base.PROFILE_ID,pin,source='DESKTOP_HTTP_PIN_GATE')
        except Exception:
            return False
        if ok:
            _remember(header)
            _remove_first_pin_file()
        return ok

    def _require_auth(self) -> bool:
        if self._authorized():
            return True
        self._challenge()
        return False

    def do_GET(self):
        if not self._require_auth():
            return
        return super().do_GET()

    def do_POST(self):
        if not self._require_auth():
            return
        return super().do_POST()


def run(port=8765,open_browser=True):
    base.Handler=SecureHandler
    return base.run(port,open_browser)


if __name__=='__main__':
    port=int(os.environ.get('PROVOWARE_PORT','8765'))
    run(port,'--no-browser' not in sys.argv)
