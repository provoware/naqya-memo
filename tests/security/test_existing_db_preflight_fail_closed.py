#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import os
import socket
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
SERVER = ROOT / 'app' / 'secure_response_server.py'


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


def run_until_exit(project: Path, timeout: float = 8) -> tuple[int, str]:
    env = os.environ.copy()
    env['PROVOWARE_PROJECT_PATH'] = str(project)
    env['PROVOWARE_PORT'] = str(free_port())
    env['PYTHONPATH'] = str(ROOT / 'core' / 'reference_python')
    proc = subprocess.run(
        [sys.executable, '-S', str(SERVER), '--no-browser'],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
    )
    return proc.returncode, proc.stdout


def main() -> None:
    with tempfile.TemporaryDirectory(prefix='provoware-existing-db-corrupt-') as td:
        project = Path(td) / 'project'
        db = project / 'daten' / 'core.sqlite3'
        db.parent.mkdir(parents=True)
        original = b'NOT-A-SQLITE-DATABASE\x00KEEP-EXACTLY\n'
        db.write_bytes(original)

        rc, out = run_until_exit(project)
        assert rc != 0, out
        assert 'EXISTING_PROJECT_DB_PREFLIGHT_UNREADABLE' in out, out[-1600:]
        print('PASS corrupt existing project database is rejected before product bootstrap')

        assert db.read_bytes() == original
        print('PASS corrupt existing database remains byte-for-byte unchanged')

        pin = project / 'nutzer-einstellungen' / 'ERSTSTART_PIN_EINMAL.txt'
        assert not pin.exists(), 'bootstrap PIN file must not be created after DB preflight failure'
        print('PASS failed database preflight creates no first-start credential file')

    with tempfile.TemporaryDirectory(prefix='provoware-existing-db-wrong-type-') as td:
        project = Path(td) / 'project'
        db = project / 'daten' / 'core.sqlite3'
        db.mkdir(parents=True)

        rc, out = run_until_exit(project)
        assert rc != 0, out
        assert 'EXISTING_PROJECT_DB_PREFLIGHT_UNSAFE' in out, out[-1600:]
        print('PASS non-file database path is rejected before product bootstrap')

        pin = project / 'nutzer-einstellungen' / 'ERSTSTART_PIN_EINMAL.txt'
        assert not pin.exists(), 'wrong-type DB path must not trigger first-start credential creation'
        print('PASS wrong-type database path causes no bootstrap-side credential mutation')

    print('SUMMARY total=5 passed=5 failed=0')


if __name__ == '__main__':
    main()
