#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import base64
import http.client
import os
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time

from provoware_core.pin import hash_pin

ROOT = Path(__file__).resolve().parents[2]
SERVER = ROOT / 'app' / 'secure_response_server.py'


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


def auth(pin: str) -> dict[str, str]:
    token = base64.b64encode(f'provoware:{pin}'.encode()).decode()
    return {'Authorization': f'Basic {token}'}


def request(port: int, pin: str | None = None) -> tuple[int, bytes]:
    conn = http.client.HTTPConnection('127.0.0.1', port, timeout=4)
    headers = auth(pin) if pin is not None else {}
    conn.request('GET', '/api/state', headers=headers)
    response = conn.getresponse()
    body = response.read()
    status = response.status
    conn.close()
    return status, body


def wait_ready(port: int, proc: subprocess.Popen[str]) -> None:
    deadline = time.time() + 12
    while time.time() < deadline:
        if proc.poll() is not None:
            raise AssertionError(f'server exited rc={proc.returncode}: {proc.stdout.read()}')
        try:
            status, _ = request(port)
            if status == 401:
                return
        except OSError:
            pass
        time.sleep(0.1)
    raise AssertionError('secure server did not become ready')


def read_first_pin(project: Path) -> str:
    path = project / 'nutzer-einstellungen' / 'ERSTSTART_PIN_EINMAL.txt'
    deadline = time.time() + 5
    while time.time() < deadline and not path.is_file():
        time.sleep(0.05)
    assert path.is_file(), 'one-time PIN file missing'
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.startswith('PIN:'):
            pin = line.split(':', 1)[1].strip()
            assert pin.isdigit() and len(pin) == 4 and pin != '0000'
            return pin
    raise AssertionError('PIN line missing')


def choose_new_pin(old_pin: str) -> str:
    for candidate in ('9876', '8765', '7654', '6543'):
        if candidate != old_pin:
            return candidate
    raise AssertionError('could not choose replacement PIN')


def replace_pin(project: Path, new_pin: str) -> tuple[int, int]:
    db = project / 'daten' / 'core.sqlite3'
    con = sqlite3.connect(db, timeout=3)
    try:
        row = con.execute("SELECT id, revision FROM profiles WHERE status='ACTIVE' LIMIT 1").fetchone()
        assert row is not None, 'active profile missing'
        profile_id, revision_before = row
        with con:
            con.execute(
                "UPDATE profiles SET pin_hash=?, revision=revision+1 WHERE id=?",
                (hash_pin(new_pin), profile_id),
            )
        revision_after = con.execute("SELECT revision FROM profiles WHERE id=?", (profile_id,)).fetchone()[0]
        return int(revision_before), int(revision_after)
    finally:
        con.close()


def main() -> None:
    port = free_port()
    with tempfile.TemporaryDirectory(prefix='provoware-auth-cache-revision-') as td:
        project = Path(td) / 'project'
        env = os.environ.copy()
        env['PROVOWARE_PROJECT_PATH'] = str(project)
        env['PROVOWARE_PORT'] = str(port)
        env['PYTHONPATH'] = str(ROOT / 'core' / 'reference_python')
        env['PROVOWARE_AUTH_CACHE_TTL'] = '300'
        env['PROVOWARE_AUTH_MAX_FAILURES'] = '20'

        proc = subprocess.Popen(
            [sys.executable, '-S', str(SERVER), '--no-browser'],
            cwd=ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        try:
            wait_ready(port, proc)
            first_pin = read_first_pin(project)

            status, body = request(port, first_pin)
            assert status == 200, (status, body[:160])
            print('PASS initial PIN authenticates and warms the auth cache')

            status, body = request(port, first_pin)
            assert status == 200, (status, body[:160])
            print('PASS cached credential is accepted while profile revision is unchanged')

            new_pin = choose_new_pin(first_pin)
            revision_before, revision_after = replace_pin(project, new_pin)
            assert revision_after == revision_before + 1, (revision_before, revision_after)
            print('PASS profile PIN replacement increments the profile revision')

            status, _ = request(port, first_pin)
            assert status == 401, status
            print('PASS stale cached old PIN is rejected immediately after profile revision changes')

            status, body = request(port, new_pin)
            assert status == 200, (status, body[:160])
            print('PASS new PIN authenticates immediately after cache invalidation')

            status, body = request(port, new_pin)
            assert status == 200, (status, body[:160])
            print('PASS replacement PIN can be cached under the new profile revision')

            print('SUMMARY total=6 passed=6 failed=0')
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)


if __name__ == '__main__':
    main()
