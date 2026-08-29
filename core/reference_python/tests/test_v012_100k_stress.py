from pathlib import Path
import tempfile, hashlib, datetime, uuid, time, resource, sys, json
ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(ROOT/'core/reference_python'))
from provoware_core.store import CoreStore, canonical_json
SCHEMA=ROOT/'schemas'/'core_schema_v2.sql'; N=100_000
with tempfile.TemporaryDirectory() as td:
    db=Path(td)/'core.sqlite3'; s=CoreStore(db,SCHEMA); pid=s.create_profile('Stress','hash'); now=datetime.datetime.now(datetime.timezone.utc).isoformat(); rows=[]; t0=time.perf_counter()
    sql='''INSERT INTO entities (id,profile_id,entity_type,schema_version,revision,status,title,payload_json,checksum_sha256,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)'''
    for i in range(N):
        payload={'body':f'Stress memo {i}','tags':['stress',str(i%20)],'pinned':False,'archived':False}; pj=canonical_json(payload)
        rows.append((str(uuid.uuid4()),pid,'memo',1,1,'ACTIVE',f'Memo {i}',pj,hashlib.sha256(pj.encode()).hexdigest(),now,now))
        if len(rows)>=5000:
            with s.conn:s.conn.executemany(sql,rows)
            rows.clear()
    if rows:
        with s.conn:s.conn.executemany(sql,rows)
    insert_s=time.perf_counter()-t0; t1=time.perf_counter(); count=s.conn.execute("SELECT COUNT(*) FROM entities WHERE profile_id=? AND entity_type='memo'",(pid,)).fetchone()[0]; count_ms=(time.perf_counter()-t1)*1000
    t2=time.perf_counter(); s.conn.execute("SELECT id,title FROM entities WHERE profile_id=? AND entity_type='memo' ORDER BY updated_at DESC LIMIT 100",(pid,)).fetchall(); latest_ms=(time.perf_counter()-t2)*1000
    integ=s.integrity_check(); rss_kb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    result={'records':count,'insert_seconds':round(insert_s,3),'count_query_ms':round(count_ms,3),'latest100_query_ms':round(latest_ms,3),'integrity':integ,'db_bytes':db.stat().st_size,'max_rss_kb':rss_kb,'pass':count==N and integ=='ok' and insert_s<30 and count_ms<1000 and latest_ms<2000 and rss_kb<450000}
    print(json.dumps(result)); s.close(); raise SystemExit(0 if result['pass'] else 1)
