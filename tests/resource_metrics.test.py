#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEASURER = ROOT / 'tools/measure_process_resources.py'


def main() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        output = Path(temp_dir) / 'RESOURCE_METRICS.json'
        child_code = "import time; payload=bytearray(8*1024*1024); time.sleep(0.7)"
        parent_code = (
            "import subprocess,sys,time; "
            "payload=bytearray(8*1024*1024); "
            f"p=subprocess.Popen([sys.executable,'-c',{child_code!r}]); "
            "time.sleep(0.8); p.wait()"
        )
        result = subprocess.run(
            [
                sys.executable, str(MEASURER),
                '--interval-ms', '100',
                '--output', str(output),
                '--command', sys.executable, '-c', parent_code,
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        assert result.returncode == 0, result.stdout
        record = json.loads(output.read_text(encoding='utf-8'))
        assert record['schema_version'] == 1
        assert record['peak_processes'] >= 2, record
        assert record['peak_ram_mb'] > 8, record
        assert record['duration_seconds'] >= 0.5, record
        assert record['sample_interval_ms'] == 100
        assert record['cpu_avg_pct'] >= 0
        assert record['cpu_max_pct'] >= record['cpu_avg_pct']
        assert record['command_exit_code'] == 0

        invalid = subprocess.run(
            [sys.executable, str(MEASURER), '--pid', str(sys.maxsize), '--interval-ms', '10', '--output', str(output)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        assert invalid.returncode != 0
        assert '--interval-ms muss zwischen 50 und 5000 liegen' in invalid.stdout

    print('NAQYA Prozessressourcen-Regression: PASS')


if __name__ == '__main__':
    main()
