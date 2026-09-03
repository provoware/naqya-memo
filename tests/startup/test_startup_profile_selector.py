from __future__ import annotations
import importlib.util
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
CORE=ROOT/'core'/'reference_python'
sys.path.insert(0,str(CORE))
from provoware_core import CoreStore
from provoware_core.profile import ProfileService

spec=importlib.util.spec_from_file_location('startup_profile_selector', ROOT/'tools'/'startup_profile_selector.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

class FakeUI:
    interactive=True
    def __init__(self, choose=None, texts=None, pins=None):
        self.choose_value=choose; self.texts=list(texts or []); self.pins=list(pins or []); self.errors=[]
    def choose(self,*_): return self.choose_value
    def text(self,*_): return self.texts.pop(0) if self.texts else None
    def pin(self,*_): return self.pins.pop(0) if self.pins else None
    def error(self,_title,message): self.errors.append(message)

def make_store(tmp):
    return CoreStore(Path(tmp)/'core.sqlite3', ROOT/'schemas'/'core_schema_v2.sql')

def test_existing_profile_can_be_selected():
    with tempfile.TemporaryDirectory() as tmp:
        store=make_store(tmp)
        try:
            pid=ProfileService(store).create('Vorhanden','1234')
            assert mod.select_or_create(store,ProfileService(store),FakeUI(choose=pid))==pid
        finally: store.close()

def test_new_profile_is_created_with_existing_profile_service():
    with tempfile.TemporaryDirectory() as tmp:
        store=make_store(tmp)
        try:
            ui=FakeUI(choose=mod.NEW_PROFILE,texts=['Neues Profil'],pins=['2468','2468'])
            pid=mod.select_or_create(store,ProfileService(store),ui)
            row=store.conn.execute("SELECT display_name FROM profiles WHERE id=? AND status='ACTIVE'",(pid,)).fetchone()
            assert row and row[0]=='Neues Profil'
            assert ProfileService(store).verify_access(pid,'2468',source='TEST') is True
        finally: store.close()

def test_mismatched_pin_is_rejected_before_retry():
    with tempfile.TemporaryDirectory() as tmp:
        store=make_store(tmp)
        try:
            ui=FakeUI(choose=mod.NEW_PROFILE,texts=['Profil A','Profil A'],pins=['1234','4321','5678','5678'])
            pid=mod.select_or_create(store,ProfileService(store),ui)
            assert pid and ui.errors==['Die beiden PIN-Eingaben stimmen nicht überein.']
            assert ProfileService(store).verify_access(pid,'5678',source='TEST') is True
        finally: store.close()

def test_headless_mode_preserves_existing_first_profile_fallback():
    with tempfile.TemporaryDirectory() as tmp:
        store=make_store(tmp)
        try:
            first=ProfileService(store).create('Erstes','1234')
            ProfileService(store).create('Zweites','5678')
            ui=FakeUI(); ui.interactive=False
            assert mod.select_or_create(store,ProfileService(store),ui)==first
        finally: store.close()

if __name__=='__main__':
    tests=[v for k,v in sorted(globals().items()) if k.startswith('test_') and callable(v)]
    for test in tests: test()
    print(f'{len(tests)}/{len(tests)} PASS')
