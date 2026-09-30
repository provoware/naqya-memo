#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / 'app'

NAMES = (
    'PROVOWARE_AUTH_CACHE_TTL',
    'PROVOWARE_AUTH_MAX_FAILURES',
    'PROVOWARE_AUTH_FAILURE_WINDOW',
    'PROVOWARE_AUTH_LOCKOUT_SECONDS',
)


def probe(values: tuple[str | None, str | None, str | None, str | None]) -> tuple[int, int, int, int]:
    with tempfile.TemporaryDirectory(prefix='provoware-auth-config-') as td:
        env = os.environ.copy()
        env['PROVOWARE_PROJECT_PATH'] = str(Path(td) / 'project')
        env['PYTHONPATH'] = os.pathsep.join([str(APP), str(ROOT / 'core' / 'reference_python')])
        for name, value in zip(NAMES, values):
            if value is None:
                env.pop(name, None)
            else:
                env[name] = value
        code = (
            "import json, secure_response_server as s; "
            "print(json.dumps([s.secure.AUTH_CACHE_TTL_SECONDS, "
            "s.secure.AUTH_MAX_DISTINCT_FAILURES, "
            "s.secure.AUTH_FAILURE_WINDOW_SECONDS, s.secure.AUTH_LOCKOUT_SECONDS]))"
        )
        proc = subprocess.run(
            [sys.executable, '-S', '-c', code],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=15,
        )
        if proc.returncode != 0:
            raise AssertionError(
                f'import failed rc={proc.returncode}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}'
            )
        line = next((line for line in reversed(proc.stdout.splitlines()) if line.startswith('[')), None)
        if line is None:
            raise AssertionError(f'no probe result in output: {proc.stdout!r}')
        parsed = json.loads(line)
        return tuple(int(value) for value in parsed)  # type: ignore[return-value]


def main() -> None:
    defaults = (300, 5, 120, 30)
    assert probe((None, None, None, None)) == defaults
    print('PASS missing auth security env uses documented safe defaults')

    assert probe(('oops', 'five', 'two-minutes', 'later')) == defaults
    print('PASS malformed auth security env no longer aborts official desktop startup')

    assert probe(('   ', ' ', '\t', '')) == defaults
    print('PASS empty auth security env uses safe defaults')

    assert probe(('0', '1', '0', '0')) == (5, 3, 5, 1)
    print('PASS auth values below safety envelope are clamped upward')

    assert probe(('99999', '999', '99999', '99999')) == (3600, 20, 3600, 3600)
    print('PASS auth values above safety envelope are clamped downward')

    assert probe(('600', '7', '180', '45')) == (600, 7, 180, 45)
    print('PASS valid in-range auth values remain unchanged')

    print('SUMMARY total=6 passed=6 failed=0')


if __name__ == '__main__':
    main()
