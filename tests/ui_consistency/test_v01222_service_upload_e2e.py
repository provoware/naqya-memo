from pathlib import Path
import os,sys,socket,tempfile,subprocess,time,json,urllib.request,urllib.parse
ROOT=Path(__file__).resolve().parents[2]
EXPECTED_VERSION=json.loads((ROOT/"registry/VERSION.json").read_text(encoding="utf-8"))["version"]

def free_port():
    s=socket.socket();s.bind(("127.0.0.1",0));p=s.getsockname()[1];s.close();return p

def get(url):
    with urllib.request.urlopen(url,timeout=3) as r:return json.loads(r.read())

with tempfile.TemporaryDirectory() as td:
    pnum=free_port(); env=os.environ.copy()
    env["PROVOWARE_PORT"]=str(pnum)
    env["PROVOWARE_PROJECT_PATH"]=str(Path(td)/"project")
    proc=subprocess.Popen([sys.executable,"-S",str(ROOT/"app/server.py"),"--no-browser"],
                          cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    base=f"http://127.0.0.1:{pnum}"
    try:
        health=None
        for _ in range(100):
            try:
                health=get(base+"/api/health")["data"];break
            except Exception:time.sleep(.05)
        assert health and health["version"]==EXPECTED_VERSION
        state=get(base+"/api/state")["data"]
        assert state["version"]==health["version"]
        assert state["backup"]["generations"]==0 and state["backup"]["label"]=="Noch keine"

        payload=b"%PDF-1.4\nrelease-ui-consistency\n%%EOF\n"
        q=urllib.parse.urlencode({"filename":"beispiel.pdf","kind":"document","title":"Beispiel PDF"})
        req=urllib.request.Request(base+"/api/assets/upload?"+q,data=payload,method="POST",
                                   headers={"Content-Type":"application/octet-stream"})
        with urllib.request.urlopen(req,timeout=5) as r:
            response=json.loads(r.read())
        assert response["ok"] is True
        aid=response["data"]["asset_id"]
        assert response["data"]["original_name"]=="beispiel.pdf"

        with urllib.request.urlopen(base+f"/asset-file/{aid}",timeout=5) as r:
            raw=r.read()
        assert raw==payload
        assets=get(base+"/api/assets/list")["data"]
        assert len(assets)==1 and assets[0]["asset_id"]==aid
        print(json.dumps({"status":"PASS","version":state["version"],"backup":state["backup"],
                          "uploaded_asset":aid,"bytes":len(raw)},ensure_ascii=False))
    finally:
        proc.terminate()
        try:proc.wait(timeout=5)
        except:proc.kill()
