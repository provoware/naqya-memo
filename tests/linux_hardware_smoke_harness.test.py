#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/run_linux_hardware_smoke.py"


def load_module():
    spec = importlib.util.spec_from_file_location("naqya_e7_smoke", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("Smoke-Harness konnte nicht geladen werden")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sample_args(**overrides):
    values = dict(
        package=Path("/tmp/naqya.deb"),
        model=Path("/tmp/model.bin"),
        microphone="USB Mic",
        runtime_metrics=Path("/tmp/runtime.json"),
        resource_metrics=Path("/tmp/resources.json"),
        profile="smoke",
        output=Path("/tmp/acceptance.json"),
    )
    values.update(overrides)
    return SimpleNamespace(**values)


def test_command(module) -> None:
    args = sample_args()
    all_flags = [f"--{flag}" for flag, _ in module.CONFIRMATIONS]
    command = module.build_collector_command(args, all_flags)
    assert command[command.index("--result") + 1] == "PASS"
    assert "--runtime-metrics" in command
    assert "--resource-metrics" in command
    assert "--live-dictation-ok" in command

    partial = module.build_collector_command(args, all_flags[:-1])
    assert partial[partial.index("--result") + 1] == "FAIL"


def test_fail_closed_confirmation(module) -> None:
    original_input = __builtins__["input"] if isinstance(__builtins__, dict) else __builtins__.input
    try:
        if isinstance(__builtins__, dict):
            __builtins__["input"] = lambda _: "nein"
        else:
            __builtins__.input = lambda _: "nein"
        assert module.ask_confirmation("Test?") is False
    finally:
        if isinstance(__builtins__, dict):
            __builtins__["input"] = original_input
        else:
            __builtins__.input = original_input


def test_self_check_needs_no_realtest_artifacts(module) -> None:
    module.validate_harness()


def test_realtest_requires_inputs(module) -> None:
    try:
        module.validate_realtest_inputs(sample_args(package=None))
    except SystemExit as error:
        assert "Installationspaket wurde nicht angegeben" in str(error)
    else:
        raise AssertionError("Fehlendes Installationspaket muss fail-closed abgelehnt werden")


def main() -> None:
    module = load_module()
    assert len(module.CONFIRMATIONS) == 7
    test_command(module)
    test_fail_closed_confirmation(module)
    test_self_check_needs_no_realtest_artifacts(module)
    test_realtest_requires_inputs(module)
    print("Linux hardware smoke harness regression: OK")


if __name__ == "__main__":
    main()
