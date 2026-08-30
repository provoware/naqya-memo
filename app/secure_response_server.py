#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import os
import sqlite3
import sys


def _bounded_int_env(name: str, default: int, minimum: int, maximum: int) -> int:
    """Read an integer security setting without letting malformed env break startup.

    A missing, empty or non-integer value falls back to the documented safe
    default. Valid numeric values are clamped to the accepted safety envelope.
    """
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    try:
        value = int(raw.strip())
    except (TypeError, ValueError):
        return default
    return max(minimum, min(value, maximum))


def _normalize_int_env(name: str, default: int, minimum: int, maximum: int) -> int:
    """Normalize an upstream security env before importing the auth layer.

    ``secure_server`` reads its auth limits during module import. Normalizing the
    existing integer settings here keeps the official production entrypoint
    fail-safe without changing the established defaults or safety envelopes.
    """
    value = _bounded_int_env(name, default, minimum, maximum)
    os.environ[name] = str(value)
    return value


def _normalize_positive_int_env(name: str, default: int) -> int:
    """Normalize a positive upstream integer while preserving valid overrides.

    The base upload handler converts ``PROVOWARE_UPLOAD_MAX_BYTES`` with a raw
    ``int(...)`` on every upload request. Missing, empty, malformed, zero or
    negative values are configuration errors and fall back to the established
    512 MiB default. Every valid positive integer remains unchanged, so this
    robustness guard does not silently redefine an operator's existing limit.
    """
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        value = default
    else:
        try:
            parsed = int(raw.strip())
        except (TypeError, ValueError):
            parsed = default
        value = parsed if parsed > 0 else default
    os.environ[name] = str(value)
    return value


# These settings are consumed while importing secure_server/base server. Normalize
# them first so malformed operator/environment values cannot break the official
# production path later during authentication or a file upload.
AUTH_CACHE_TTL_SECONDS = _normalize_int_env('PROVOWARE_AUTH_CACHE_TTL', 300, 5, 3600)
AUTH_MAX_DISTINCT_FAILURES = _normalize_int_env('PROVOWARE_AUTH_MAX_FAILURES', 5, 3, 20)
AUTH_FAILURE_WINDOW_SECONDS = _normalize_int_env('PROVOWARE_AUTH_FAILURE_WINDOW', 120, 5, 3600)
AUTH_LOCKOUT_SECONDS = _normalize_int_env('PROVOWARE_AUTH_LOCKOUT_SECONDS', 30, 1, 3600)
UPLOAD_MAX_BYTES = _normalize_positive_int_env('PROVOWARE_UPLOAD_MAX_BYTES', 512 * 1024 * 1024)

import secure_server as secure


JSON_POST_MAX_BYTES = _bounded_int_env(
    'PROVOWARE_JSON_POST_MAX_BYTES', 1024 * 1024, 4096, 16 * 1024 * 1024
)
REQUEST_IO_TIMEOUT_SECONDS = _bounded_int_env(
    'PROVOWARE_REQUEST_IO_TIMEOUT_SECONDS', 30, 1, 120
)


def _profile_security_state_from_readonly_db() -> tuple[int, str] | None:
    """Read the active profile incarnation on an isolated read-only connection.

    ``revision`` invalidates cached credentials after normal security mutations.
    ``created_at`` additionally distinguishes a replacement profile that happens
    to reuse the same profile id and revision. Both values are read from one
    committed SQLite snapshot; any read/shape/conversion error fails closed.
    """
    try:
        con = sqlite3.connect(f'file:{secure.DB}?mode=ro', uri=True, timeout=2)
        try:
            con.execute('PRAGMA query_only=ON')
            row = con.execute(
                "SELECT revision, created_at FROM profiles WHERE id=? AND status='ACTIVE'",
                (secure.base.PROFILE_ID,),
            ).fetchone()
            if row is None:
                return None
            revision = int(row[0])
            created_at = str(row[1]).strip()
            if revision < 1 or not created_at:
                return None
            return revision, created_at
        finally:
            con.close()
    except (sqlite3.Error, OSError, TypeError, ValueError):
        return None


def _profile_revision_from_readonly_db() -> int | None:
    """Compatibility read used by the existing isolation regression contract."""
    state = _profile_security_state_from_readonly_db()
    return state[0] if state is not None else None


def _profile_cache_epoch_from_readonly_db() -> int | None:
    """Return an opaque integer cache epoch bound to revision and incarnation."""
    state = _profile_security_state_from_readonly_db()
    if state is None:
        return None
    revision, created_at = state
    material = f'{revision}\x00{created_at}'.encode('utf-8')
    return int.from_bytes(hashlib.sha256(material).digest(), 'big')


# The official production entrypoint owns the final runtime boundary. Keep the
# lower auth implementation intact but route its security-state token through an
# independent read-only lookup. The token preserves the lower layer's integer
# equality contract while binding cache validity to both revision and profile
# incarnation, so a replacement profile cannot inherit a predecessor's cache.
secure._profile_revision = _profile_cache_epoch_from_readonly_db


class ResponseHardenedHandler(secure.SecureHandler):
    """Final desktop response boundary for the official launch path.

    The lower secure_server owns authentication, rate limiting, cache policy and
    loopback/origin trust. This final layer adds browser containment headers,
    bounded JSON request bodies and a bounded per-connection I/O wait without
    duplicating product logic.
    """

    def setup(self):
        """Prevent stalled local clients from holding a request thread forever."""
        super().setup()
        self.connection.settimeout(REQUEST_IO_TIMEOUT_SECONDS)

    def end_headers(self):
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Content-Security-Policy', "frame-ancestors 'none'; base-uri 'none'; object-src 'none'")
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('X-Content-Type-Options', 'nosniff')
        return super().end_headers()

    def _reject_request_body(self, status: int, code: str, message: str) -> None:
        data = secure.base.json.dumps(
            {'ok': False, 'code': code, 'message': message}, ensure_ascii=False
        ).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _json_body_preflight(self) -> bool:
        """Bound ordinary JSON mutations before the base handler reads into RAM.

        Asset uploads keep their independent streaming/quota contract in
        server.py and are therefore deliberately excluded here.
        """
        path = self.path.split('?', 1)[0]
        if path == '/api/assets/upload':
            return True
        raw = self.headers.get('Content-Length', '0').strip()
        try:
            length = int(raw or '0')
        except ValueError:
            self._reject_request_body(400, 'REQUEST_CONTENT_LENGTH_INVALID', 'Ungültige Anfragegröße.')
            return False
        if length < 0:
            self._reject_request_body(400, 'REQUEST_CONTENT_LENGTH_INVALID', 'Ungültige Anfragegröße.')
            return False
        if length > JSON_POST_MAX_BYTES:
            self._reject_request_body(
                413,
                'REQUEST_BODY_TOO_LARGE',
                f'Diese Anfrage ist zu groß. Erlaubt sind höchstens {JSON_POST_MAX_BYTES} Byte.',
            )
            return False
        return True

    def do_POST(self):
        if not self._json_body_preflight():
            return
        return super().do_POST()


def run(port: int = 8765, open_browser: bool = True):
    # secure.run resolves its handler through the module global. Rebinding only
    # that class keeps all existing security logic and adds this narrow response
    # contract without duplicating server implementation.
    secure.SecureHandler = ResponseHardenedHandler
    return secure.run(port, open_browser)


if __name__ == '__main__':
    port = int(os.environ.get('PROVOWARE_PORT', '8765'))
    run(port, '--no-browser' not in sys.argv)
