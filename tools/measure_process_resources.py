#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ctypes
import json
import os
import subprocess
import sys
import time
from pathlib import Path

SCHEMA_VERSION = 1


def linux_process_table() -> dict[int, int]:
    table: dict[int, int] = {}
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit():
            continue
        try:
            stat = (entry / 'stat').read_text(encoding='utf-8', errors='replace')
            tail = stat.rsplit(')', 1)[1].strip().split()
            table[int(entry.name)] = int(tail[1])
        except (OSError, ValueError, IndexError):
            continue
    return table


def windows_process_table() -> dict[int, int]:
    TH32CS_SNAPPROCESS = 0x00000002
    INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value

    class PROCESSENTRY32W(ctypes.Structure):
        _fields_ = [
            ('dwSize', ctypes.c_ulong), ('cntUsage', ctypes.c_ulong), ('th32ProcessID', ctypes.c_ulong),
            ('th32DefaultHeapID', ctypes.c_void_p), ('th32ModuleID', ctypes.c_ulong), ('cntThreads', ctypes.c_ulong),
            ('th32ParentProcessID', ctypes.c_ulong), ('pcPriClassBase', ctypes.c_long), ('dwFlags', ctypes.c_ulong),
            ('szExeFile', ctypes.c_wchar * 260),
        ]

    kernel32 = ctypes.windll.kernel32
    snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if snapshot == INVALID_HANDLE_VALUE:
        return {}
    table: dict[int, int] = {}
    try:
        item = PROCESSENTRY32W()
        item.dwSize = ctypes.sizeof(item)
        ok = kernel32.Process32FirstW(snapshot, ctypes.byref(item))
        while ok:
            table[int(item.th32ProcessID)] = int(item.th32ParentProcessID)
            ok = kernel32.Process32NextW(snapshot, ctypes.byref(item))
    finally:
        kernel32.CloseHandle(snapshot)
    return table


def process_table() -> dict[int, int]:
    if sys.platform.startswith('linux'):
        return linux_process_table()
    if os.name == 'nt':
        return windows_process_table()
    raise SystemExit('FEHLER: Ressourcenmessung unterstützt derzeit Linux und Windows.')


def process_family(root_pid: int) -> set[int]:
    table = process_table()
    family = {root_pid}
    changed = True
    while changed:
        changed = False
        for pid, ppid in table.items():
            if ppid in family and pid not in family:
                family.add(pid)
                changed = True
    return family


def linux_sample(pid: int) -> tuple[int, float] | None:
    try:
        status = (Path('/proc') / str(pid) / 'status').read_text(encoding='utf-8', errors='replace')
        stat = (Path('/proc') / str(pid) / 'stat').read_text(encoding='utf-8', errors='replace')
        rss_kb = 0
        for line in status.splitlines():
            if line.startswith('VmRSS:'):
                rss_kb = int(line.split()[1])
                break
        tail = stat.rsplit(')', 1)[1].strip().split()
        ticks = float(tail[11]) + float(tail[12])
        cpu_seconds = ticks / float(os.sysconf('SC_CLK_TCK'))
        return rss_kb * 1024, cpu_seconds
    except (OSError, ValueError, IndexError):
        return None


def windows_sample(pid: int) -> tuple[int, float] | None:
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    PROCESS_VM_READ = 0x0010

    class FILETIME(ctypes.Structure):
        _fields_ = [('dwLowDateTime', ctypes.c_ulong), ('dwHighDateTime', ctypes.c_ulong)]

    class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
        _fields_ = [
            ('cb', ctypes.c_ulong), ('PageFaultCount', ctypes.c_ulong), ('PeakWorkingSetSize', ctypes.c_size_t),
            ('WorkingSetSize', ctypes.c_size_t), ('QuotaPeakPagedPoolUsage', ctypes.c_size_t),
            ('QuotaPagedPoolUsage', ctypes.c_size_t), ('QuotaPeakNonPagedPoolUsage', ctypes.c_size_t),
            ('QuotaNonPagedPoolUsage', ctypes.c_size_t), ('PagefileUsage', ctypes.c_size_t), ('PeakPagefileUsage', ctypes.c_size_t),
        ]

    kernel32 = ctypes.windll.kernel32
    psapi = ctypes.windll.psapi
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION | PROCESS_VM_READ, False, pid)
    if not handle:
        return None
    try:
        counters = PROCESS_MEMORY_COUNTERS()
        counters.cb = ctypes.sizeof(counters)
        if not psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
            return None
        creation, exit_time, kernel, user = FILETIME(), FILETIME(), FILETIME(), FILETIME()
        if not kernel32.GetProcessTimes(handle, ctypes.byref(creation), ctypes.byref(exit_time), ctypes.byref(kernel), ctypes.byref(user)):
            return None
        def ft_seconds(value: FILETIME) -> float:
            ticks = (int(value.dwHighDateTime) << 32) | int(value.dwLowDateTime)
            return ticks / 10_000_000.0
        return int(counters.WorkingSetSize), ft_seconds(kernel) + ft_seconds(user)
    finally:
        kernel32.CloseHandle(handle)


def sample(pid: int) -> tuple[int, float] | None:
    return linux_sample(pid) if sys.platform.startswith('linux') else windows_sample(pid)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Misst Peak-RAM und CPU einer NAQYA-Prozessfamilie ohne Zusatzabhängigkeiten.')
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument('--pid', type=int, help='PID einer bereits laufenden NAQYA-Anwendung')
    target.add_argument('--command', nargs=argparse.REMAINDER, help='Befehl starten und dessen Prozessfamilie messen')
    parser.add_argument('--interval-ms', type=int, default=250, help='Messintervall in Millisekunden (Standard: 250)')
    parser.add_argument('--output', type=Path, default=Path('RESOURCE_METRICS.json'))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.interval_ms < 50 or args.interval_ms > 5000:
        raise SystemExit('FEHLER: --interval-ms muss zwischen 50 und 5000 liegen.')

    child: subprocess.Popen[str] | None = None
    if args.command is not None:
        command = args.command
        if command and command[0] == '--':
            command = command[1:]
        if not command:
            raise SystemExit('FEHLER: --command benötigt einen Befehl.')
        child = subprocess.Popen(command, text=True)
        root_pid = child.pid
    else:
        root_pid = int(args.pid)

    started = time.monotonic()
    peak_bytes = 0
    peak_processes = 0
    cpu_samples: list[float] = []
    previous_cpu: float | None = None
    previous_time: float | None = None
    cpu_count = max(1, os.cpu_count() or 1)

    while True:
        family = process_family(root_pid)
        total_rss = 0
        total_cpu = 0.0
        alive = 0
        for pid in family:
            point = sample(pid)
            if point is None:
                continue
            rss, cpu_seconds = point
            total_rss += rss
            total_cpu += cpu_seconds
            alive += 1

        now = time.monotonic()
        if alive:
            peak_bytes = max(peak_bytes, total_rss)
            peak_processes = max(peak_processes, alive)
            if previous_cpu is not None and previous_time is not None and now > previous_time:
                cpu_pct = max(0.0, (total_cpu - previous_cpu) / (now - previous_time) * 100.0 / cpu_count)
                cpu_samples.append(cpu_pct)
            previous_cpu, previous_time = total_cpu, now
        else:
            if child is None or child.poll() is not None:
                break

        if child is not None and child.poll() is not None and not alive:
            break
        time.sleep(args.interval_ms / 1000.0)

    if child is not None:
        return_code = child.wait()
    else:
        return_code = None

    if peak_bytes <= 0:
        raise SystemExit('FEHLER: Für die Prozessfamilie konnten keine Ressourcenmesswerte erfasst werden.')

    record = {
        'schema_version': SCHEMA_VERSION,
        'root_pid': root_pid,
        'duration_seconds': round(time.monotonic() - started, 3),
        'sample_interval_ms': args.interval_ms,
        'peak_processes': peak_processes,
        'peak_ram_mb': round(peak_bytes / (1024 * 1024), 3),
        'cpu_avg_pct': round(sum(cpu_samples) / len(cpu_samples), 3) if cpu_samples else 0.0,
        'cpu_max_pct': round(max(cpu_samples), 3) if cpu_samples else 0.0,
        'command_exit_code': return_code,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"Ressourcenmessung geschrieben: {args.output}")
    print(f"Peak-RAM: {record['peak_ram_mb']:.3f} MB | CPU Ø/max: {record['cpu_avg_pct']:.2f}/{record['cpu_max_pct']:.2f} %")
    if return_code not in (None, 0):
        raise SystemExit(return_code)


if __name__ == '__main__':
    main()
