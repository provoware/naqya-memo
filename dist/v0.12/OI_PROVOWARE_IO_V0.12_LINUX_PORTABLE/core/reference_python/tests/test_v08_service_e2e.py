from pathlib import Path
import tempfile, os, sys, subprocess, time, json, urllib.request, socket
ROOT=Path(__file__).resolve().parents[3]
def free_port():
    s=socket.socket();s.bind(("127.0.0.1",0));p=s.getsockname()[1];s.close();return p
def req(base,path,method="GET",body=None):
    data=None if body is None else json.dumps(body).encode()
    r=urllib.request.Request(base+path,data=data,method=method,headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(r,timeout=4) as x:return json.loads(x.read())["data"]
if __name__=="__main__":
    with tempfile.TemporaryDirectory() as td:
        port=free_port();env=os.environ.copy();env["PROVOWARE_PORT"]=str(port);env["PROVOWARE_PROJECT_PATH"]=str(Path(td)/"project")
        p=subprocess.Popen([sys.executable,str(ROOT/"app/server.py"),"--no-browser"],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        base=f"http://127.0.0.1:{port}"
        try:
            for _ in range(60):
                try:req(base,"/api/health");break
                except Exception:time.sleep(.1)
            m=req(base,"/api/memos","POST",{"title":"M","body":"eins","tags":[]})
            m2=req(base,f"/api/memos/{m['id']}/edit","POST",{"revision":m["revision"],"title":"M2","body":"zwei","tags":["x"]});assert m2["title"]=="M2"
            t=req(base,"/api/todos","POST",{"title":"T","description":"","priority":"NORMAL"})
            t2=req(base,f"/api/todos/{t['id']}/edit","POST",{"revision":t["revision"],"title":"T2","description":"d","priority":"HOCH"});assert t2["title"]=="T2"
            st=req(base,"/api/state");cid=st["colors"][0]["id"]
            e=req(base,"/api/events","POST",{"title":"E","start_at":"2026-09-01T10:00:00+00:00","color_id":cid})
            e2=req(base,f"/api/events/{e['id']}/edit","POST",{"revision":e["revision"],"title":"E2","start_at":"2026-09-01T11:00:00+00:00","color_id":cid});assert e2["title"]=="E2"
            req(base,"/api/calendar/day-color","POST",{"day":"2026-09-02","color_id":cid});assert "2026-09-02" in req(base,"/api/calendar/day-colors")
            req(base,f"/api/memos/{m2['id']}/trash","POST",{"revision":m2["revision"]});tr=req(base,"/api/trash");x=next(x for x in tr if x["id"]==m2["id"]);req(base,f"/api/trash/{x['id']}/restore","POST",{"revision":x["revision"]})
            prev=req(base,"/api/diagnostics/preview");assert prev["privacy"]["memo_contents"]=="NICHT ENTHALTEN"
            diag=req(base,"/api/diagnostics/create","POST",{"confirmed":True});assert diag["name"].endswith(".txt")
            print("PASS service_edit_restore_calendar_diagnostics")
        finally:
            p.terminate()
            try:p.wait(timeout=5)
            except:p.kill()
