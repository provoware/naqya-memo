from __future__ import annotations
import os, shutil, sys, platform, json
from pathlib import Path

def linux_capability_probe():
    return {
        "platform":"linux",
        "runtime":sys.platform,
        "kernel":platform.release(),
        "xdg_open":bool(shutil.which("xdg-open")),
        "xdg_email":bool(shutil.which("xdg-email")),
        "notify_send":bool(shutil.which("notify-send")),
        "ffmpeg":bool(shutil.which("ffmpeg")),
        "ffprobe":bool(shutil.which("ffprobe")),
        "filesystem_write_test":None,
        "evidence_type":"NATIVE_RUNTIME_PROBE",
    }

def write_probe(project_dir: Path):
    project_dir=Path(project_dir)
    target=project_dir/"temp"/"capability_probe.txt"
    target.parent.mkdir(parents=True,exist_ok=True)
    try:
        target.write_text("probe",encoding="utf-8")
        ok=target.read_text(encoding="utf-8")=="probe"
        target.unlink(missing_ok=True)
        return ok
    except Exception:
        return False

def android_contract():
    return {
        "platform":"android",
        "notifications":"RUNTIME_PERMISSION_REQUIRED",
        "storage":"SCOPED_STORAGE",
        "background":"OS_RESTRICTED",
        "microphone":"RUNTIME_PERMISSION_REQUIRED",
        "share":"INTENT_ADAPTER",
        "evidence_type":"CONTRACT_ONLY",
        "native_device_tested":False,
    }

def ios_contract():
    return {
        "platform":"ios",
        "notifications":"USER_AUTHORIZATION_REQUIRED",
        "storage":"APP_SANDBOX_DOCUMENT_PICKER",
        "background":"STRICTLY_RESTRICTED",
        "microphone":"USER_AUTHORIZATION_REQUIRED",
        "share":"SHARE_SHEET",
        "evidence_type":"CONTRACT_ONLY",
        "native_device_tested":False,
    }
