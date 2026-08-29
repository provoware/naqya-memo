from pathlib import Path
import tempfile, datetime, sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/"core/reference_python"))
from provoware_core import CoreStore, MutationQueue
from provoware_core.modules import TodoService, CalendarService
from provoware_core.reminders import ReminderEngine
SCHEMA=ROOT/"schemas"/"core_schema_v2.sql"

def test_due_reminder_and_dedup():
    with tempfile.TemporaryDirectory() as td:
        s=CoreStore(Path(td)/"db.sqlite3",SCHEMA); pid=s.create_profile("R","hash"); q=MutationQueue();q.start()
        todo=TodoService(s,q); todo.create(pid,"T","", "2026-08-28T12:00:00+00:00","2026-08-28T11:00:00+00:00")
        eng=ReminderEngine(s); now=datetime.datetime(2026,8,28,12,0,tzinfo=datetime.timezone.utc)
        pending=eng.pending_for_platform(pid,"linux",now); assert len(pending)==1
        x=pending[0]; eng.mark_delivered(pid,x["id"],x["payload"]["reminder_at"],"linux")
        assert eng.pending_for_platform(pid,"linux",now)==[]
        q.stop();s.close()

def test_future_reminder_not_due():
    with tempfile.TemporaryDirectory() as td:
        s=CoreStore(Path(td)/"db.sqlite3",SCHEMA); pid=s.create_profile("R","hash"); q=MutationQueue();q.start()
        todo=TodoService(s,q); todo.create(pid,"T","", "2026-08-30T12:00:00+00:00","2026-08-30T11:00:00+00:00")
        eng=ReminderEngine(s); now=datetime.datetime(2026,8,28,12,0,tzinfo=datetime.timezone.utc)
        assert eng.pending_for_platform(pid,"linux",now)==[]
        q.stop();s.close()

if __name__=="__main__":
    tests=[v for k,v in sorted(globals().items()) if k.startswith("test_")]
    bad=[]
    for t in tests:
        try:t();print("PASS",t.__name__)
        except Exception as e:bad.append((t.__name__,repr(e)));print("FAIL",t.__name__,repr(e))
    print(f"SUMMARY total={len(tests)} passed={len(tests)-len(bad)} failed={len(bad)}")
    if bad:raise SystemExit(1)
