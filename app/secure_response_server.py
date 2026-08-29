#!/usr/bin/env python3
from __future__ import annotations

import os
import sys

import secure_server as secure

JSON_POST_MAX_BYTES = max(
    4096,
    min(int(os.environ.get('PROVOWARE_JSON_POST_MAX_BYTES', str(1024 * 1024))), 16 * 1024 * 1024),
)


class ResponseHardenedHandler(secure.SecureHandler):
    """Final desktop response boundary for the official launch path.

    The lower secure_server owns authentication, rate limiting, cache policy and
    loopback/origin trust. This final layer adds browser containment headers and
    a bounded JSON request-body contract without duplicating product logic.
    """

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
