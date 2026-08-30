#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import os
import socket
import sqlite3
import stat
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
SERVER = ROOT / 'app' / 'secure_response_server.py'


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


def env_for(project: Path, port: int) -> dict[str, str]:
    env = os.environ.copy()
    env['PROVOWARE_PROJECT_PATH'] = str(project)
    env['PROVOWARE_PORT'] = str(port)
    env['PYTHONPATH'] = str(ROOT / 'core' / 'reference_python')
    return env


def run_until_exit(project: Path, timeout: float = 8) -> tuple[int, str]:
    proc = subprocess.Popen(
        [sys.executable, '-S', str(SERVER), '--no-browser'],
        cwd=ROOT,
        env=env_for(project, free_port()),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        out, _ = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.terminate()
        try:
            out, _ = proc.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
            out, _ = proc.communicate(timeout=2)
        raise AssertionError(f'server unexpectedly stayed alive: {out[-1200:]}')
    return proc.returncode, out


def wait_ready(project: Path) -> tuple[subprocess.Popen[str], Path]:
    port = free_port()
    proc = subprocess.Popen(
        [sys.executable, '-S', str(SERVER), '--no-browser'],
        cwd=ROOT,
        env=env_for(project, port),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    pin_file = project / 'nutzer-einstellungen' / 'ERSTSTART_PIN_EINMAL.txt'
    deadline = time.time() + 10
    while time.time() < deadline:
        if proc.poll() is not None:
            raise AssertionError(f'normal server exited rc={proc.returncode}: {proc.stdout.read()}')
        if pin_file.is_file():
            return proc, pin_file
        time.sleep(0.05)
    proc.terminate()
    raise AssertionError('normal first-start PIN file was not created')


def active_profile_accepts_default(project: Path) -> bool:
    db = project / 'daten' / 'core.sqlite3'
    if not db.is_file():
        return False
    con = sqlite3.connect(db, timeout=2)
    try:
        row = con.execute("SELECT pin_hash FROM profiles WHERE status='ACTIVE' LIMIT 1").fetchone()
        assert row is not None
    finally:
        con.close()
    sys.path.insert(0, str(ROOT / 'core' / 'reference_python'))
    from provoware_core.pin import verify_pin
    return verify_pin('0000', str(row[0]))


def wait_until_profile_rotated(project: Path, proc: subprocess.Popen[str], timeout: float = 5) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if proc.poll() is not None:
            raise AssertionError(f'normal server exited before PIN rotation rc={proc.returncode}: {proc.stdout.read()}')
        try:
            if not active_profile_accepts_default(project):
                return
        except (sqlite3.Error, AssertionError):
            pass
        time.sleep(0.05)
    raise AssertionError('normal first-start profile did not rotate away from bootstrap PIN 0000')


def main() -> None:
    if not hasattr(os, 'symlink'):
        print('SKIP symlink support unavailable on this platform')
        return

    with tempfile.TemporaryDirectory(prefix='provoware-first-pin-symlink-') as td:
        root = Path(td)
        project = root / 'project'
        settings = project / 'nutzer-einstellungen'
        settings.mkdir(parents=True)
        victim = root / 'victim.txt'
        victim.write_text('UNVERAENDERT\n', encoding='utf-8')
        pin_path = settings / 'ERSTSTART_PIN_EINMAL.txt'
        pin_path.symlink_to(victim)

        rc, out = run_until_exit(project)
        assert rc != 0, out
        assert pin_path.is_symlink(), 'attacker-controlled symlink was replaced'
        assert victim.read_text(encoding='utf-8') == 'UNVERAENDERT\n'
        print('PASS predictable first-PIN path refuses symlink substitution without touching target')

        assert active_profile_accepts_default(project), 'fixture did not leave bootstrap profile for retry guard'
        print('PASS failed first-start fixture exposes the persisted bootstrap-credential retry condition')

        pin_path.unlink()
        rc2, out2 = run_until_exit(project)
        assert rc2 != 0, out2
        assert 'INSECURE_DEFAULT_PIN_DETECTED' in out2, out2[-1200:]
        print('PASS retry fails closed instead of exposing persisted 0000 bootstrap credential')

    with tempfile.TemporaryDirectory(prefix='provoware-first-pin-normal-') as td:
        project = Path(td) / 'project'
        proc, pin_file = wait_ready(project)
        try:
            assert pin_file.is_file() and not pin_file.is_symlink()
            mode = stat.S_IMODE(pin_file.stat().st_mode)
            assert mode == 0o600, oct(mode)
            text = pin_file.read_text(encoding='utf-8')
            pin_lines = [line for line in text.splitlines() if line.startswith('PIN:')]
            assert len(pin_lines) == 1
            pin = pin_lines[0].split(':', 1)[1].strip()
            assert pin.isdigit() and len(pin) == 4 and pin != '0000'
            print('PASS normal first start creates one regular 0600 PIN file with non-default PIN')
            wait_until_profile_rotated(project, proc)
            print('PASS normal first start rotates the persisted profile away from bootstrap PIN 0000')
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=2)


if __name__ == '__main__':
    main()
