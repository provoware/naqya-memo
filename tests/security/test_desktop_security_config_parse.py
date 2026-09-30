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


def probe(json_limit: str | None, timeout: str | None) -> tuple[int, int]:
    with tempfile.TemporaryDirectory(prefix='provoware-config-parse-') as td:
        env = os.environ.copy()
        env['PROVOWARE_PROJECT_PATH'] = str(Path(td) / 'project')
        env['PYTHONPATH'] = os.pathsep.join([str(APP), str(ROOT / 'core' / 'reference_python')])
        if json_limit is None:
            env.pop('PROVOWARE_JSON_POST_MAX_BYTES', None)
        else:
            env['PROVOWARE_JSON_POST_MAX_BYTES'] = json_limit
        if timeout is None:
            env.pop('PROVOWARE_REQUEST_IO_TIMEOUT_SECONDS', None)
        else:
            env['PROVOWARE_REQUEST_IO_TIMEOUT_SECONDS'] = timeout
        code = (
            "import json, secure_response_server as s; "
            "print(json.dumps([s.JSON_POST_MAX_BYTES, s.REQUEST_IO_TIMEOUT_SECONDS]))"
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
            raise AssertionError(f'import failed rc={proc.returncode}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}')
        line = next((line for line in reversed(proc.stdout.splitlines()) if line.startswith('[')), None)
        if line is None:
            raise AssertionError(f'no probe result in output: {proc.stdout!r}')
        values = json.loads(line)
        return int(values[0]), int(values[1])


def main() -> None:
    assert probe(None, None) == (1024 * 1024, 30)
    print('PASS missing security env uses documented safe defaults')

    assert probe('not-a-number', 'thirty') == (1024 * 1024, 30)
    print('PASS malformed security env no longer aborts desktop startup')

    assert probe('   ', '   ') == (1024 * 1024, 30)
    print('PASS empty or whitespace security env uses safe defaults')

    assert probe('1', '0') == (4096, 1)
    print('PASS numeric values below safety envelope are clamped upward')

    assert probe(str(64 * 1024 * 1024), '9999') == (16 * 1024 * 1024, 120)
    print('PASS numeric values above safety envelope are clamped downward')

    assert probe('8192', '7') == (8192, 7)
    print('PASS valid in-range operator values remain unchanged')

    print('SUMMARY total=6 passed=6 failed=0')


if __name__ == '__main__':
    main()
