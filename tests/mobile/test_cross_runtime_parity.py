from pathlib import Path
import tempfile, subprocess, json, sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'core/reference_python'))
from provoware_core import CoreStore, MutationQueue, MemoService, TodoService, CalendarService
SCHEMA=ROOT/'schemas/core_schema_v2.sql'
with tempfile.TemporaryDirectory() as td:
    s=CoreStore(Path(td)/'db.sqlite3',SCHEMA);pid=s.create_profile('Parity','hash');q=MutationQueue();q.start();memos=MemoService(s,q);todos=TodoService(s,q);cal=CalendarService(s,q)
    mid,mr=memos.create(pid,'M','one',[]);mid,mr=memos.edit(mid,pid,mr,'M2','two',['a']);m=s.get_entity(mid)
    tid,tr=todos.create(pid,'T','d','2026-09-01T12:00:00+00:00','2026-09-01T11:00:00+00:00','NORMAL');tid,tr=todos.complete(tid,pid,tr);t=s.get_entity(tid)
    eid,er=cal.create_event(pid,'E','2026-09-02T10:00:00+00:00','2026-09-02T11:00:00+00:00');e=s.get_entity(eid)
    colors=cal.set_color_legend(pid,[('Arbeit','neon-tuerkis'),('Privat','lila'),('Wichtig','knallgelb'),('Info','orange'),('Frei','gruen')]);cal.set_day_color(pid,'2026-09-02',colors[0])
    py={'memo':{'title':m['title'],'body':m['payload']['body'],'revision':m['revision'],'status':m['status']},'todo':{'completed':t['payload']['completed'],'revision':t['revision'],'status':t['status']},'event':{'title':e['title'],'revision':e['revision'],'status':e['status']},'colors':s.conn.execute('SELECT COUNT(*) FROM calendar_colors WHERE profile_id=?',(pid,)).fetchone()[0],'day_color':s.conn.execute("SELECT COUNT(*) FROM entities WHERE profile_id=? AND entity_type='calendar_day_color' AND status='ACTIVE'",(pid,)).fetchone()[0]==1}
    q.stop();s.close()
node=json.loads(subprocess.check_output(['node',str(ROOT/'tests/mobile/mobile_parity_node.mjs')],text=True))
assert py==node,(py,node)
print(json.dumps({'status':'PASS','python':py,'mobile':node},ensure_ascii=False))
