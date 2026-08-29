#!/usr/bin/env python3
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import sys
import threading
import time
from urllib.parse import urlparse

import server as base

AUTH_REALM = 'PROVOWARE Desktop PIN'
AUTH_USER = 'provoware'
AUTH_CACHE_TTL_SECONDS = max(5, min(int(os.environ.get('PROVOWARE_AUTH_CACHE_TTL','300')), 3600))
_AUTH_CACHE: dict[str, float] = {}
_AUTH_LOCK = threading.Lock()


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
    """Fail-closed desktop transport guard around the existing product handler.

    The browser authenticates once through HTTP Basic Auth. The username is fixed
    to ``provoware``; the password is the active profile PIN. Only a SHA-256 digest
    of the Authorization header is kept briefly in RAM to avoid expensive PIN
    verification on every static asset request. No PIN or reusable session token
    is persisted by this wrapper.
    """

    def _challenge(self):
        body=(
            'PROVOWARE ist gesperrt. Im Browser-Benutzerfeld "provoware" '
            'und als Passwort die Profil-PIN eingeben.\n'
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
