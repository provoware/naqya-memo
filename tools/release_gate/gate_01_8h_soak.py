from pathlib import Path
import argparse, datetime, json, os, random, resource, sys, tempfile, time
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'core/reference_python'))
from provoware_core import CoreStore, MutationQueue, MemoService, TodoService
SCHEMA=ROOT/'schemas/core_schema_v2.sql'
E=ROOT/'registry/evidence/v0.12.2/gates/GATE_01_8H_SOAK.json'

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
p=argparse.ArgumentParser(); p.add_argument('--hours',type=float,default=8.0); p.add_argument('--preflight-seconds',type=float,default=0); args=p.parse_args()
required=8*3600
requested=args.hours*3600
actual_target=args.preflight_seconds if args.preflight_seconds>0 else requested
qualification='PRECHECK_ONLY' if actual_target < required else 'FULL_8H'
start_wall=now(); start=time.monotonic(); ops=0; errors=[]; checkpoints=[]
with tempfile.TemporaryDirectory() as td:
    store=CoreStore(Path(td)/'core.sqlite3',SCHEMA); pid=store.create_profile('8h Soak','hash'); q=MutationQueue();q.start(); memo=MemoService(store,q); todo=TodoService(store,q); ids=[]
    next_cp=time.monotonic()+min(60,max(1,actual_target/4))
    try:
        while time.monotonic()-start<actual_target:
            try:
                if not ids or random.random()<.58:
                    eid,_=memo.create(pid,f'M{ops}',f'body-{ops}',[f't{ops%25}']); ids.append(eid)
                else:
                    eid=random.choice(ids); obj=store.get_entity(eid)
                    if obj and obj['status']=='ACTIVE': memo.edit(eid,pid,obj['revision'],obj['title'],obj['payload'].get('body','')+'x',obj['payload'].get('tags',[]))
                if ops%40==0: todo.create(pid,f'T{ops}')
                if ops%100==0 and store.integrity_check()!='ok': raise RuntimeError('INTEGRITY_NOT_OK')
                ops+=1
            except Exception as exc:
                errors.append(repr(exc)); break
            if time.monotonic()>=next_cp:
                checkpoints.append({'at_seconds':round(time.monotonic()-start,1),'ops':ops,'integrity':store.integrity_check(),'rss_kb':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
                partial={'gate':'GATE_01_8H_SOAK','status':'RUNNING' if qualification=='FULL_8H' else 'PRECHECK_RUNNING','qualification':qualification,'required_seconds':required,'executed_seconds':round(time.monotonic()-start,2),'operations':ops,'integrity':checkpoints[-1]['integrity'],'errors':errors,'checkpoints':checkpoints,'started_at':start_wall,'last_checkpoint_at':now()}
                E.write_text(json.dumps(partial,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
                next_cp=time.monotonic()+60
        integrity=store.integrity_check()
    finally:
        q.stop(); store.close()
duration=time.monotonic()-start
passed=(qualification=='FULL_8H' and duration>=required and integrity=='ok' and not errors)
status='PASS' if passed else ('PRECHECK_PASS' if qualification=='PRECHECK_ONLY' and integrity=='ok' and not errors else 'FAIL')
out={'gate':'GATE_01_8H_SOAK','status':status,'qualification':qualification,'required_seconds':required,'executed_seconds':round(duration,2),'operations':ops,'integrity':integrity,'errors':errors,'max_rss_kb':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'checkpoints':checkpoints,'started_at':start_wall,'finished_at':now()}
E.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8'); print(json.dumps(out,ensure_ascii=False))
raise SystemExit(0 if status in ('PASS','PRECHECK_PASS') else 1)
