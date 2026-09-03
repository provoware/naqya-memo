#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import base64
import http.client
import json
import os
import socket
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
SERVER = ROOT / 'app' / 'secure_response_server.py'
LIMIT = 4096


def free_port() -> int:
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def auth_header(pin: str) -> str:
    token = base64.b64encode(f'provoware:{pin}'.encode()).decode()
    return f'Basic {token}'


def request(port: int, method: str, path: str, pin: str | None = None, body: bytes | None = None):
    headers = {'Host': f'127.0.0.1:{port}'}
    if pin is not None:
        headers['Authorization'] = auth_header(pin)
    if body is not None:
        headers['Content-Type'] = 'application/json'
    c = http.client.HTTPConnection('127.0.0.1', port, timeout=4)
    c.request(method, path, body=body, headers=headers)
    r = c.getresponse()
    raw = r.read()
    out = (r.status, {k.lower(): v for k, v in r.getheaders()}, raw)
    c.close()
    return out


def wait(port: int, proc: subprocess.Popen) -> None:
    deadline = time.time() + 12
    while time.time() < deadline:
        if proc.poll() is not None:
            raise AssertionError(f'server exited rc={proc.returncode}: {proc.stdout.read()}')
        try:
            if request(port, 'GET', '/index.html')[0] == 401:
                return
        except OSError:
            pass
        time.sleep(.1)
    raise AssertionError('server did not become ready')


def decoded(raw: bytes) -> dict:
    return json.loads(raw.decode('utf-8'))


def main() -> None:
    port = free_port()
    with tempfile.TemporaryDirectory(prefix='provoware-json-limit-') as td:
        project = Path(td) / 'project'
        env = os.environ.copy()
        env['PROVOWARE_PROJECT_PATH'] = str(project)
        env['PROVOWARE_PORT'] = str(port)
        env['PROVOWARE_JSON_POST_MAX_BYTES'] = str(LIMIT)
        env['PYTHONPATH'] = str(ROOT / 'core' / 'reference_python')
        proc = subprocess.Popen(
            [sys.executable, '-S', str(SERVER), '--no-browser'],
            cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )
        try:
            wait(port, proc)
            pin_file = project / 'nutzer-einstellungen' / 'ERSTSTART_PIN_EINMAL.txt'
            pin_line = next(line for line in pin_file.read_text(encoding='utf-8').splitlines() if line.startswith('PIN: '))
            pin = pin_line.split(':', 1)[1].strip()

            status, _, raw = request(port, 'GET', '/api/memos', pin)
            assert status == 200, status
            assert decoded(raw)['data'] == [], decoded(raw)
            print('PASS authenticated baseline is empty')

            oversized = json.dumps({'title': 'oversized', 'body': 'X' * (LIMIT + 512)}).encode('utf-8')
            assert len(oversized) > LIMIT
            status, headers, raw = request(port, 'POST', '/api/memos', pin, oversized)
            payload = decoded(raw)
            assert status == 413, (status, payload)
            assert payload.get('code') == 'REQUEST_BODY_TOO_LARGE', payload
            assert 'no-store' in headers.get('cache-control', ''), headers
            print('PASS oversized JSON mutation is rejected before product body parsing')

            status, _, raw = request(port, 'GET', '/api/memos', pin)
            assert status == 200, status
            assert decoded(raw)['data'] == [], decoded(raw)
            print('PASS rejected oversized request creates no memo mutation')

            normal = json.dumps({'title': 'bounded', 'body': 'ok', 'tags': []}).encode('utf-8')
            status, _, raw = request(port, 'POST', '/api/memos', pin, normal)
            assert status == 200, (status, raw)
            assert decoded(raw).get('ok') is True, decoded(raw)
            print('PASS normal bounded JSON mutation still succeeds')

            status, _, raw = request(port, 'GET', '/api/memos', pin)
            memos = decoded(raw)['data']
            assert len(memos) == 1 and memos[0]['title'] == 'bounded', memos
            print('PASS server remains healthy after 413 and persists only valid mutation')

            print('SUMMARY total=5 passed=5 failed=0')
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill(); proc.wait(timeout=5)


if __name__ == '__main__':
    main()
