from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json, uuid
from .atomic import atomic_write_bytes
from .store import utc_now, canonical_json
from .platform import get_platform_adapter
from .project_folder import ProjectFolderService
from .settings import SettingsService

class GuidedFirstStart:
    """UI-unabhängige geführte Start-State-Machine.

    Sie repariert nur sichere, lokale Strukturen automatisch. Berechtigungen oder
    externe Pfade werden niemals heimlich erzwungen.
    """
    def __init__(self, store, project_service: ProjectFolderService | None = None):
        self.store=store
        self.project_service=project_service or ProjectFolderService()

    def run(self, *, project_path: Path, profile_id: str | None = None, platform_id: str | None = None) -> dict:
        run_id=str(uuid.uuid4()); started=utc_now(); phases=[]
        adapter=get_platform_adapter(platform_id)

        def phase(name,state,details,message):
            phases.append({"name":name,"state":state,"details":details,"message":message})

        caps=adapter.scan_capabilities(); perms=adapter.scan_permissions()
        phase("SYSTEM_SCAN","GREEN",caps.as_dict(),"System und verfügbare Fähigkeiten wurden erfasst.")
        perm_state="YELLOW" if any(v in ("UNKNOWN","USER_ACTION_REQUIRED") for v in perms.permissions.values()) else "GREEN"
        phase("PERMISSIONS",perm_state,perms.as_dict(),"Berechtigungen werden nur bei Bedarf und sichtbar angefordert.")

        pre=self.project_service.preflight(project_path,create=True)
        phase("PROJECT_FOLDER",pre.traffic,pre.as_dict(),"Projektordner wurde geprüft und sichere Unterordner wurden vorbereitet." if pre.ok else "Projektordner benötigt Hilfe.")

        if not pre.ok:
            final="RED"
        else:
            if profile_id:
                SettingsService(self.store).ensure_defaults(profile_id)
                phase("SETTINGS","GREEN",{"defaults_ready":True},"Nutzereinstellungen sind persistent vorbereitet.")
            else:
                phase("PROFILE","YELLOW",{"profile_required":True},"Als Nächstes Profil wählen oder anlegen.")
            final="YELLOW" if any(p["state"]=="YELLOW" for p in phases) else "GREEN"

        report={
            "run_id":run_id,"started_at":started,"finished_at":utc_now(),"state":final,
            "platform_id":adapter.platform_id,"project_path":pre.project_path,"profile_id":profile_id,
            "phases":phases,
            "next_action":"PROFILE_SELECT_OR_CREATE" if not profile_id and pre.ok else "READY" if pre.ok else "PROJECT_FOLDER_REPAIR",
        }
        with self.store.conn:
            self.store.conn.execute(
                "INSERT INTO startup_runs(run_id,profile_id,platform_id,state,started_at,finished_at,project_path,report_json) VALUES(?,?,?,?,?,?,?,?)",
                (run_id,profile_id,adapter.platform_id,final,started,report["finished_at"],pre.project_path,canonical_json(report)),
            )
            self.store.conn.execute(
                "INSERT INTO capability_snapshots(snapshot_id,startup_run_id,platform_id,capability_json,permission_json,created_at) VALUES(?,?,?,?,?,?)",
                (str(uuid.uuid4()),run_id,adapter.platform_id,canonical_json(caps.as_dict()),canonical_json(perms.as_dict()),utc_now()),
            )
        if pre.ok:
            checkpoint=Path(pre.project_path)/"manifeste"/"START_CHECKPOINT.json"
            atomic_write_bytes(checkpoint,(json.dumps(report,indent=2,ensure_ascii=False)+"\n").encode("utf-8"))
        return report
