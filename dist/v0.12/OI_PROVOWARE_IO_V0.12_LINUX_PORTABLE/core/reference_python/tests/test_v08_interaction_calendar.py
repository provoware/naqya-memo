from pathlib import Path
import tempfile, os, sys, subprocess, time, json, urllib.request, urllib.error, socket, shutil
ROOT=Path(__file__).resolve().parents[3]
CORE=ROOT/"core"/"reference_python"
sys.path.insert(0,str(CORE))
from provoware_core import CoreStore, MutationQueue, MemoService, TodoService, CalendarService
SCHEMA=ROOT/"schemas"/"core_schema_v2.sql"

def setup(td):
    s=CoreStore(Path(td)/"core.sqlite3",SCHEMA); pid=s.create_profile("V08","hash"); q=MutationQueue();q.start();return s,pid,q
def test_edit_memo_todo_event_and_revisions():
    with tempfile.TemporaryDirectory() as td:
        s,p,q=setup(td); m=MemoService(s,q); t=TodoService(s,q); c=CalendarService(s,q)
        mid,r=m.create(p,"M","eins"); m.edit(mid,p,r,"M2","zwei"); assert s.get_entity(mid)["title"]=="M2"
        tid,r=t.create(p,"T"); t.edit(tid,p,r,"T2","desc"); assert s.get_entity(tid)["title"]=="T2"
        eid,r=c.create_event(p,"E","2026-09-01T10:00:00+00:00"); c.edit_event(eid,p,r,"E2","2026-09-01T11:00:00+00:00"); assert s.get_entity(eid)["title"]=="E2"
        q.stop();s.close()
def test_restore_entity_after_trash():
    with tempfile.TemporaryDirectory() as td:
        s,p,q=setup(td); m=MemoService(s,q); eid,r=m.create(p,"M","x"); nr=m.trash(eid,p,r); assert s.get_entity(eid)["status"]=="TRASHED"; rr=s.restore_entity(eid,nr); assert s.get_entity(eid)["status"]=="ACTIVE" and rr>nr; q.stop();s.close()
def test_calendar_day_color_update_is_revision_safe():
    with tempfile.TemporaryDirectory() as td:
        s,p,q=setup(td); c=CalendarService(s,q); ids=c.set_color_legend(p,[("A","#11ffff"),("B","#bb44ff"),("C","#ffee22"),("D","#ff7733"),("E","#44ee99")]); eid,r=c.set_day_color(p,"2026-09-02",ids[0]); obj=s.get_entity(eid); s.upsert_entity(profile_id=p,entity_type="calendar_day_color",title="2026-09-02",payload={"day":"2026-09-02","color_id":ids[1]},entity_id=eid,expected_revision=obj["revision"]); assert s.get_entity(eid)["payload"]["color_id"]==ids[1];q.stop();s.close()
def test_ui_contains_real_month_calendar_and_edit_controls():
    h=(ROOT/"ui/reference_web/index.html").read_text(encoding="utf-8"); j=(ROOT/"ui/reference_web/app.js").read_text(encoding="utf-8"); c=(ROOT/"ui/reference_web/styles.css").read_text(encoding="utf-8")
    assert "month-grid" in j and "data-edit-memo" in j and "data-edit-todo" in j and "data-edit-event" in j
    assert "data-restore" in j and "/api/diagnostics/preview" in j and "@media(max-width:390px)" in c
    assert "stylesheet" in h and "app.js" in h
def test_diagnostic_privacy_contract_static():
    s=(ROOT/"app/server.py").read_text(encoding="utf-8")
    assert "'memo_contents':'NICHT ENTHALTEN'" in s and "'pin':'NICHT ENTHALTEN'" in s and "DIAG_CONFIRM_REQUIRED" in s
def test_no_direct_sqlite_from_ui():
    j=(ROOT/"ui/reference_web/app.js").read_text(encoding="utf-8").lower()
    assert "sqlite3" not in j and "corestore" not in j

if __name__=="__main__":
    tests=[v for k,v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    bad=[]
    for t in tests:
        try:t();print("PASS",t.__name__)
        except Exception as e:bad.append((t.__name__,repr(e)));print("FAIL",t.__name__,repr(e))
    print(f"SUMMARY total={len(tests)} passed={len(tests)-len(bad)} failed={len(bad)}")
    if bad:raise SystemExit(1)
