from pathlib import Path
import tempfile, sys, time, random, json, os
ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(ROOT/'core/reference_python'))
from provoware_core import CoreStore, MutationQueue, MemoService, TodoService
SCHEMA=ROOT/'schemas'/'core_schema_v2.sql'; DURATION=float(os.environ.get('PROVOWARE_SOAK_SECONDS','10'))
with tempfile.TemporaryDirectory() as td:
    s=CoreStore(Path(td)/'db.sqlite3',SCHEMA); pid=s.create_profile('Soak','hash'); q=MutationQueue();q.start(); memo=MemoService(s,q); todo=TodoService(s,q); ids=[]; ops=0; start=time.monotonic()
    while time.monotonic()-start<DURATION:
        if not ids or random.random()<.6:
            eid,_=memo.create(pid,f'M{ops}',f'body{ops}'); ids.append(eid)
        else:
            eid=random.choice(ids); obj=s.get_entity(eid)
            if obj and obj['status']=='ACTIVE':memo.edit(eid,pid,obj['revision'],obj['title'],obj['payload'].get('body','')+'x',obj['payload'].get('tags',[]))
        if ops%25==0:todo.create(pid,f'T{ops}')
        ops+=1
    integrity=s.integrity_check(); q.stop();s.close(); result={'duration_seconds':round(time.monotonic()-start,2),'operations':ops,'integrity':integrity,'pass':ops>100 and integrity=='ok','qualification':'BOUNDED_CI_SOAK_NOT_LONG_TERM'};print(json.dumps(result));raise SystemExit(0 if result['pass'] else 1)
