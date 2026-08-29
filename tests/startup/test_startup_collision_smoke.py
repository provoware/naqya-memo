from pathlib import Path
import json, os, socket, subprocess, sys, tempfile, time, urllib.request

ROOT=Path(__file__).resolve().parents[2]

def free_port():
    s=socket.socket();s.bind(("127.0.0.1",0));p=s.getsockname()[1];s.close();return p

requested=free_port()
ev=ROOT/"runtime/startup/LAST_START_PORT.json"
ev.unlink(missing_ok=True)
blocker=socket.socket();blocker.bind(("127.0.0.1",requested));blocker.listen(1)
with tempfile.TemporaryDirectory() as td:
    env=os.environ.copy()
    env["PROVOWARE_PORT"]=str(requested)
    env["PROVOWARE_PORT_MAX"]=str(requested+10)
    env["PROVOWARE_PROJECT_PATH"]=str(Path(td)/"project")
    env["PROVOWARE_NO_BROWSER"]="1"
    p=subprocess.Popen(["bash",str(ROOT/"STARTEN_OHNE_BROWSER.sh")],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    try:
        ev=ROOT/"runtime/startup/LAST_START_PORT.json"
        chosen=None
        for _ in range(100):
            if ev.exists():
                try:
                    data=json.loads(ev.read_text());chosen=data.get("selected_port")
                    if chosen and chosen!=requested: break
                except Exception:pass
            time.sleep(.05)
        assert chosen and chosen!=requested, "fallback port not selected"
        ok=False
        for _ in range(100):
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{chosen}/api/health",timeout=.3) as r:
                    h=json.loads(r.read())["data"];ok=h.get("version")=="0.12.2.1-STARTUP-PORT-GUARD"
                    if ok: break
            except Exception: time.sleep(.05)
        assert ok, "health did not become ready"
        print(json.dumps({"status":"PASS","requested":requested,"selected":chosen,"health_version":h.get("version")}))
    finally:
        p.terminate()
        try:p.wait(timeout=5)
        except: p.kill()
blocker.close()
