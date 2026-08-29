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
NAME = 'PROVOWARE_UPLOAD_MAX_BYTES'
DEFAULT = 512 * 1024 * 1024


def probe(value: str | None) -> int:
    with tempfile.TemporaryDirectory(prefix='provoware-upload-config-') as td:
        env = os.environ.copy()
        env['PROVOWARE_PROJECT_PATH'] = str(Path(td) / 'project')
        env['PYTHONPATH'] = os.pathsep.join([str(APP), str(ROOT / 'core' / 'reference_python')])
        if value is None:
            env.pop(NAME, None)
        else:
            env[NAME] = value
        code = (
            "import json, os, secure_response_server as s; "
            "print(json.dumps([s.UPLOAD_MAX_BYTES, int(os.environ['PROVOWARE_UPLOAD_MAX_BYTES'])]))"
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
        assert parsed[0] == parsed[1], 'normalized value must be inherited by the base upload handler'
        return int(parsed[0])


def main() -> None:
    assert probe(None) == DEFAULT
    print('PASS missing upload limit uses established 512 MiB default')

    assert probe('not-a-number') == DEFAULT
    print('PASS malformed upload limit no longer breaks the upload request path')

    assert probe('   ') == DEFAULT
    print('PASS empty upload limit uses established safe default')

    assert probe('0') == DEFAULT
    print('PASS zero upload limit is treated as invalid configuration')

    assert probe('-1') == DEFAULT
    print('PASS negative upload limit is treated as invalid configuration')

    custom = 700 * 1024 * 1024
    assert probe(str(custom)) == custom
    print('PASS valid positive operator override remains unchanged')

    print('SUMMARY total=6 passed=6 failed=0')


if __name__ == '__main__':
    main()
