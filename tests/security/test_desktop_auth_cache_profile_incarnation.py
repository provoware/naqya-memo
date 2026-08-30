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
    conn.request('GET', '/api/state', headers=auth(pin) if pin is not None else {})
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


def replace_profile_incarnation_without_revision_change(project: Path, new_pin: str) -> tuple[int, str, str]:
    db = project / 'daten' / 'core.sqlite3'
    con = sqlite3.connect(db, timeout=3)
    try:
        row = con.execute(
            "SELECT id, revision, created_at FROM profiles WHERE status='ACTIVE' LIMIT 1"
        ).fetchone()
        assert row is not None, 'active profile missing'
        profile_id, revision, created_at = row
        replacement_created_at = f'{created_at}#replacement'
        with con:
            con.execute(
                "UPDATE profiles SET pin_hash=?, created_at=? WHERE id=?",
                (hash_pin(new_pin), replacement_created_at, profile_id),
            )
        row_after = con.execute(
            "SELECT revision, created_at FROM profiles WHERE id=?", (profile_id,)
        ).fetchone()
        assert row_after is not None
        assert int(row_after[0]) == int(revision), row_after
        assert str(row_after[1]) == replacement_created_at, row_after
        return int(revision), str(created_at), replacement_created_at
    finally:
        con.close()


def main() -> None:
    port = free_port()
    with tempfile.TemporaryDirectory(prefix='provoware-auth-cache-incarnation-') as td:
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
            print('PASS cached credential is accepted for the unchanged profile incarnation')

            new_pin = choose_new_pin(first_pin)
            revision, created_before, created_after = replace_profile_incarnation_without_revision_change(
                project, new_pin
            )
            assert created_after != created_before
            print(f'PASS replacement fixture preserves revision={revision} while changing profile incarnation')

            status, _ = request(port, first_pin)
            assert status == 401, status
            print('PASS predecessor cached PIN is rejected despite identical profile id and revision')

            status, body = request(port, new_pin)
            assert status == 200, (status, body[:160])
            print('PASS replacement profile PIN authenticates under the new incarnation cache epoch')

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
