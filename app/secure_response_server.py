#!/usr/bin/env python3
from __future__ import annotations

import os
import sys

import secure_server as secure


class ResponseHardenedHandler(secure.SecureHandler):
    """Final desktop response boundary for the official launch path.

    The lower secure_server owns authentication, rate limiting, cache policy and
    loopback/origin trust. This final layer adds browser containment headers that
    are intentionally independent of UI implementation details.
    """

    def end_headers(self):
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Content-Security-Policy', "frame-ancestors 'none'; base-uri 'none'; object-src 'none'")
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('X-Content-Type-Options', 'nosniff')
        return super().end_headers()


def run(port: int = 8765, open_browser: bool = True):
    # secure.run resolves its handler through the module global. Rebinding only
    # that class keeps all existing security logic and adds this narrow response
    # contract without duplicating server implementation.
    secure.SecureHandler = ResponseHardenedHandler
    return secure.run(port, open_browser)


if __name__ == '__main__':
    port = int(os.environ.get('PROVOWARE_PORT', '8765'))
    run(port, '--no-browser' not in sys.argv)
