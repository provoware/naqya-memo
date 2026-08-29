from pathlib import Path
import tempfile
from provoware_core import CoreStore,MutationQueue,MemoService,TodoService,CalendarService
ROOT=Path(__file__).resolve().parents[3]; SCHEMA=ROOT/"schemas/core_schema_v1.sql"
def setup(td):
 s=CoreStore(Path(td)/"core.sqlite3",SCHEMA); p=s.create_profile("D","hash"); q=MutationQueue(); q.start(); return s,p,q
def test_memo_crud_undo_redo():
 with tempfile.TemporaryDirectory() as td:
  s,p,q=setup(td); m=MemoService(s,q); eid,r=m.create(p,"A","one"); _,r=m.edit(eid,p,r,"B","two"); s.undo_last(p); assert s.get_entity(eid)["title"]=="A"; s.redo_last(p); assert s.get_entity(eid)["title"]=="B"; cur=s.get_entity(eid); m.trash(eid,p,cur["revision"]); assert s.get_entity(eid)["status"]=="TRASHED"; s.undo_last(p); assert s.get_entity(eid)["status"]=="ACTIVE"; q.stop(); s.close()
def test_todo_complete_and_rule():
 with tempfile.TemporaryDirectory() as td:
  s,p,q=setup(td); t=TodoService(s,q); eid,r=t.create(p,"T","","2026-09-01T10:00:00+00:00","2026-09-01T09:00:00+00:00"); t.complete(eid,p,r); assert s.get_entity(eid)["payload"]["completed"]; s.undo_last(p); assert not s.get_entity(eid)["payload"]["completed"];
  try: t.create(p,"X","",None,"2026-09-01T09:00:00+00:00"); raise AssertionError()
  except ValueError as e: assert str(e)=="REMINDER_REQUIRES_DUE_DATE"
  q.stop(); s.close()
def test_calendar_colors_day_and_next10():
 with tempfile.TemporaryDirectory() as td:
  s,p,q=setup(td); c=CalendarService(s,q); ids=c.set_color_legend(p,[("A","cyan"),("B","purple"),("C","yellow"),("D","orange"),("E","green")]); assert len(ids)==5; deid,_=c.set_day_color(p,"2026-09-02",ids[0]); assert s.get_entity(deid)["payload"]["day"]=="2026-09-02"; c.create_event(p,"Event","2026-09-02T12:00:00+00:00",color_id=ids[0]); t=TodoService(s,q); [t.create(p,f"T{i}") for i in range(12)]; assert len(c.next_items(p,10))==10; q.stop(); s.close()
def test_revision_conflict_domain():
 with tempfile.TemporaryDirectory() as td:
  s,p,q=setup(td); m=MemoService(s,q); eid,r=m.create(p,"A","x")
  try: m.edit(eid,p,999,"B","y"); raise AssertionError()
  except RuntimeError as e: assert str(e)=="REVISION_CONFLICT"
  assert s.get_entity(eid)["title"]=="A"; q.stop(); s.close()
if __name__=="__main__":
 tests=[v for k,v in sorted(globals().items()) if k.startswith("test_") and callable(v)]; failed=[]
 for t in tests:
  try:t();print("PASS",t.__name__)
  except Exception as e:failed.append((t.__name__,repr(e)));print("FAIL",t.__name__,repr(e))
 print(f"SUMMARY total={len(tests)} passed={len(tests)-len(failed)} failed={len(failed)}")
 raise SystemExit(1 if failed else 0)
