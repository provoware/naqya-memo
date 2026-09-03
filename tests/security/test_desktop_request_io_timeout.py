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
TIMEOUT_SECONDS = 1


def free_port() -> int:
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def auth_header(pin: str) -> str:
    token = base64.b64encode(f'provoware:{pin}'.encode()).decode()
    return f'Basic {token}'


def request(port: int, path: str, pin: str | None = None) -> int:
    headers = {'Host': f'127.0.0.1:{port}'}
    if pin is not None:
        headers['Authorization'] = auth_header(pin)
    conn = http.client.HTTPConnection('127.0.0.1', port, timeout=4)
    conn.request('GET', path, headers=headers)
    response = conn.getresponse()
    response.read()
    status = response.status
    conn.close()
    return status


def wait(port: int, proc: subprocess.Popen) -> None:
    deadline = time.time() + 12
    while time.time() < deadline:
        if proc.poll() is not None:
            raise AssertionError(f'server exited rc={proc.returncode}: {proc.stdout.read()}')
        try:
            if request(port, '/index.html') == 401:
                return
        except OSError:
            pass
        time.sleep(.1)
    raise AssertionError('server did not become ready')


def stalled_partial_post(port: int, pin: str) -> bytes:
    sock = socket.create_connection(('127.0.0.1', port), timeout=4)
    sock.settimeout(TIMEOUT_SECONDS + 3)
    request_bytes = (
        'POST /api/memos HTTP/1.1\r\n'
        f'Host: 127.0.0.1:{port}\r\n'
        f'Authorization: {auth_header(pin)}\r\n'
        'Content-Type: application/json\r\n'
        'Content-Length: 128\r\n'
        'Connection: close\r\n'
        '\r\n'
        '{'
    ).encode('utf-8')
    started = time.monotonic()
    sock.sendall(request_bytes)
    chunks: list[bytes] = []
    try:
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)
    except socket.timeout as exc:
        raise AssertionError('stalled request was not released by server I/O timeout') from exc
    finally:
        sock.close()
    elapsed = time.monotonic() - started
    assert elapsed < TIMEOUT_SECONDS + 2.5, elapsed
    return b''.join(chunks)


def main() -> None:
    port = free_port()
    with tempfile.TemporaryDirectory(prefix='provoware-request-timeout-') as td:
        project = Path(td) / 'project'
        env = os.environ.copy()
        env['PROVOWARE_PROJECT_PATH'] = str(project)
        env['PROVOWARE_PORT'] = str(port)
        env['PROVOWARE_REQUEST_IO_TIMEOUT_SECONDS'] = str(TIMEOUT_SECONDS)
        env['PYTHONPATH'] = str(ROOT / 'core' / 'reference_python')
        proc = subprocess.Popen(
            [sys.executable, '-S', str(SERVER), '--no-browser'],
            cwd=ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        try:
            wait(port, proc)
            print('PASS unauthenticated readiness remains normal')

            pin_file = project / 'nutzer-einstellungen' / 'ERSTSTART_PIN_EINMAL.txt'
            pin_line = next(line for line in pin_file.read_text(encoding='utf-8').splitlines() if line.startswith('PIN: '))
            pin = pin_line.split(':', 1)[1].strip()
            assert request(port, '/api/state', pin) == 200
            print('PASS authenticated baseline remains healthy')

            raw = stalled_partial_post(port, pin)
            assert raw == b'' or raw.startswith(b'HTTP/1.'), raw[:80]
            print('PASS partial authenticated POST is released within bounded I/O wait')

            assert request(port, '/api/state', pin) == 200
            print('PASS server remains healthy after stalled-client timeout')

            assert proc.poll() is None
            print('PASS timeout is connection-scoped and does not terminate server')
            print('SUMMARY total=5 passed=5 failed=0')
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)


if __name__ == '__main__':
    main()
