from __future__ import annotations
from .base import PlatformAdapter, CapabilityReport, PermissionReport

class AndroidAdapter(PlatformAdapter):
    platform_id="android"
    def scan_capabilities(self):
        return CapabilityReport(
            platform_id="android", os_name="Android", os_version="RUNTIME_NATIVE_REQUIRED",
            architecture="RUNTIME_NATIVE_REQUIRED", python_version="REFERENCE_ONLY",
            display_width=None, display_height=None,
            capabilities={
                "filesystem_project_folder":"SCOPED_STORAGE_ADAPTER_REQUIRED",
                "open_standard_editor":"INTENT_ADAPTER_REQUIRED",
                "desktop_notifications":True,
                "share_sheet":True,
                "audio_capture":"RUNTIME_PERMISSION_REQUIRED",
                "background_reminders":"OS_POLICY_ACCEPTANCE_REQUIRED",
            },
            notes=["Keine native Android-Freigabe aus der Python-Referenz behaupten."],
        )
    def scan_permissions(self):
        return PermissionReport(
            platform_id="android",
            permissions={"project_folder":"USER_ACTION_REQUIRED","notifications":"USER_ACTION_REQUIRED","microphone":"USER_ACTION_REQUIRED","external_paths":"USER_ACTION_REQUIRED"},
            notes=["Scoped Storage und Runtime Permissions müssen im nativen Adapter bestätigt werden."],
        )
