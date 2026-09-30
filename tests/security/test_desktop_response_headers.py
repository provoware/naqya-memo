#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import base64
import http.client
import os
import socket
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
SERVER = ROOT / 'app' / 'secure_response_server.py'


def free_port() -> int:
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def request(port: int, path: str = '/index.html', pin: str | None = None):
    headers = {'Host': f'127.0.0.1:{port}'}
    if pin is not None:
        token = base64.b64encode(f'provoware:{pin}'.encode()).decode()
        headers['Authorization'] = f'Basic {token}'
    c = http.client.HTTPConnection('127.0.0.1', port, timeout=4)
    c.request('GET', path, headers=headers)
    r = c.getresponse()
    body = r.read()
    out = (r.status, {k.lower(): v for k, v in r.getheaders()}, body)
    c.close()
    return out


def assert_security_headers(headers: dict[str, str]) -> None:
    assert headers.get('x-frame-options') == 'DENY', headers
    csp = headers.get('content-security-policy', '')
    assert "frame-ancestors 'none'" in csp, headers
    assert "base-uri 'none'" in csp, headers
    assert "object-src 'none'" in csp, headers
    assert headers.get('referrer-policy') == 'no-referrer', headers
    assert headers.get('x-content-type-options') == 'nosniff', headers
    assert 'no-store' in headers.get('cache-control', ''), headers


def wait(port: int, proc: subprocess.Popen) -> None:
    deadline = time.time() + 12
    while time.time() < deadline:
        if proc.poll() is not None:
            raise AssertionError(f'server exited rc={proc.returncode}: {proc.stdout.read()}')
        try:
            if request(port)[0] == 401:
                return
        except OSError:
            pass
        time.sleep(.1)
    raise AssertionError('response-hardened server did not become ready')


def main() -> None:
    port = free_port()
    with tempfile.TemporaryDirectory(prefix='provoware-response-headers-') as td:
        project = Path(td) / 'project'
        env = os.environ.copy()
        env['PROVOWARE_PROJECT_PATH'] = str(project)
        env['PROVOWARE_PORT'] = str(port)
        env['PYTHONPATH'] = str(ROOT / 'core' / 'reference_python')
        proc = subprocess.Popen(
            [sys.executable, '-S', str(SERVER), '--no-browser'],
            cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )
        try:
            wait(port, proc)
            status, headers, _ = request(port)
            assert status == 401, status
            assert_security_headers(headers)
            print('PASS unauthenticated challenge has full response-security contract')

            first_pin_file = project / 'nutzer-einstellungen' / 'ERSTSTART_PIN_EINMAL.txt'
            pin_line = next(line for line in first_pin_file.read_text(encoding='utf-8').splitlines() if line.startswith('PIN: '))
            pin = pin_line.split(':', 1)[1].strip()

            status, headers, _ = request(port, '/api/state', pin)
            assert status == 200, status
            assert_security_headers(headers)
            print('PASS authenticated API response has full response-security contract')

            status, headers, _ = request(port, '/index.html', pin)
            assert status == 200, status
            assert_security_headers(headers)
            print('PASS authenticated UI response has full response-security contract')

            linux = (ROOT / 'STARTEN_LINUX.sh').read_text(encoding='utf-8')
            headless = (ROOT / 'STARTEN_OHNE_BROWSER.sh').read_text(encoding='utf-8')
            assert 'app/secure_response_server.py' in linux
            assert 'app/secure_response_server.py' in headless
            print('PASS both official Linux launchers use the response-hardened entrypoint')

            print('SUMMARY total=4 passed=4 failed=0')
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill(); proc.wait(timeout=5)


if __name__ == '__main__':
    main()
