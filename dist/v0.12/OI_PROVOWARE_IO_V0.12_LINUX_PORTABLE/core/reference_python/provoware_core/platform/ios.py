from __future__ import annotations
from .base import PlatformAdapter, CapabilityReport, PermissionReport

class IOSAdapter(PlatformAdapter):
    platform_id="ios"
    def scan_capabilities(self):
        return CapabilityReport(
            platform_id="ios", os_name="iOS", os_version="RUNTIME_NATIVE_REQUIRED",
            architecture="RUNTIME_NATIVE_REQUIRED", python_version="REFERENCE_ONLY",
            display_width=None, display_height=None,
            capabilities={
                "filesystem_project_folder":"APP_SANDBOX_DOCUMENT_PICKER",
                "open_standard_editor":"SHARE_OR_DOCUMENT_INTERACTION_REQUIRED",
                "desktop_notifications":True,
                "share_sheet":True,
                "audio_capture":"RUNTIME_PERMISSION_REQUIRED",
                "background_reminders":"OS_POLICY_ACCEPTANCE_REQUIRED",
            },
            notes=["Self-Repair bleibt auf Sandbox und erlaubte iOS APIs begrenzt."],
        )
    def scan_permissions(self):
        return PermissionReport(
            platform_id="ios",
            permissions={"project_folder":"USER_ACTION_REQUIRED","notifications":"USER_ACTION_REQUIRED","microphone":"USER_ACTION_REQUIRED","external_paths":"USER_ACTION_REQUIRED"},
            notes=["iOS-Dateizugriff außerhalb der Sandbox erfolgt nur über erlaubte Systemdialoge."],
        )
