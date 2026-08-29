#!/usr/bin/env python3
from pathlib import Path
import sys
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here))
sys.path.insert(0, str(here / "provoware_core"))
# tests expect package parent on path
sys.path.insert(0, str(here))
exec((here/"tests"/"test_persistence_contract.py").read_text(encoding="utf-8"), {"__name__":"__main__","__file__":str(here/"tests"/"test_persistence_contract.py")})
