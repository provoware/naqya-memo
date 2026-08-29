from __future__ import annotations
import os, platform, shutil, sys
from .base import PlatformAdapter, CapabilityReport, PermissionReport

class LinuxAdapter(PlatformAdapter):
    platform_id="linux"
    def scan_capabilities(self):
        display_w = int(os.environ.get("PROVOWARE_TEST_DISPLAY_WIDTH","0")) or None
        display_h = int(os.environ.get("PROVOWARE_TEST_DISPLAY_HEIGHT","0")) or None
        return CapabilityReport(
            platform_id=self.platform_id,
            os_name=platform.system() or "Linux",
            os_version=platform.release(),
            architecture=platform.machine(),
            python_version=platform.python_version(),
            display_width=display_w,
            display_height=display_h,
            capabilities={
                "filesystem_project_folder": True,
                "open_standard_editor": bool(shutil.which("xdg-open")),
                "desktop_notifications": bool(shutil.which("notify-send")),
                "share_sheet": False,
                "audio_capture": "RUNTIME_CHECK_REQUIRED",
                "background_reminders": "DESKTOP_SERVICE_OR_APP_LIFECYCLE_REQUIRED",
            },
            notes=["Displaygröße ist ohne UI-Toolkit ggf. unbekannt und wird später vom Presentation Adapter geliefert."],
        )
    def scan_permissions(self):
        return PermissionReport(
            platform_id=self.platform_id,
            permissions={
                "project_folder": "USER_ACTION_REQUIRED",
                "notifications": "UNKNOWN",
                "microphone": "UNKNOWN",
                "external_paths": "USER_ACTION_REQUIRED",
            },
            notes=["Linux-Rechte werden zusätzlich am konkreten Pfad und beim tatsächlichen Audiozugriff geprüft."],
        )
