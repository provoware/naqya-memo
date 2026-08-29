from pathlib import Path
import os, sys
ROOT=Path(sys.argv[1]); PROJECT=Path(sys.argv[2]); SOURCE=Path(sys.argv[3]); PHASE=sys.argv[4]
sys.path.insert(0,str(ROOT/'core/reference_python'))
from provoware_core.assets import AssetManager
am=AssetManager(PROJECT); codes={'journal_created':81,'staged':82,'file_committed':83,'manifest_committed':84}
def hook(phase):
    if phase==PHASE: os._exit(codes.get(phase,89))
am.import_asset(SOURCE,'audio','Kill Test',_phase_hook=hook)
