from pathlib import Path
import json, os, socket, subprocess, sys, tempfile, threading
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT=Path(__file__).resolve().parents[2]
GUARD=ROOT/"tools/startup_port_guard.py"

def free_port():
    s=socket.socket();s.bind(("127.0.0.1",0));p=s.getsockname()[1];s.close();return p

def run_guard(port,maxp=None,env=None):
    cmd=[sys.executable,"-S",str(GUARD),"--root",str(ROOT),"--requested",str(port)]
    if maxp: cmd += ["--max",str(maxp)]
    p=subprocess.run(cmd,text=True,capture_output=True,env=env)
    return p.returncode,json.loads(p.stdout.strip())

def test_free_requested_port():
    p=free_port()
    rc,j=run_guard(p,p+3)
    assert rc==0 and j["action"]=="START" and j["selected_port"]==p

def test_foreign_listener_uses_fallback_without_kill():
    p=free_port()
    s=socket.socket();s.bind(("127.0.0.1",p));s.listen(1)
    try:
        rc,j=run_guard(p,p+5)
        assert rc==0 and j["action"]=="START" and j["selected_port"]>p
    finally:s.close()


def test_same_app_same_project_is_reused():
    p=free_port()
    expected=(ROOT/"runtime"/"projektordner").resolve()
    version=json.loads((ROOT/"registry/VERSION.json").read_text())["version"]
    class H(BaseHTTPRequestHandler):
        def log_message(self,*a): pass
        def do_GET(self):
            if self.path!="/api/health":
                self.send_response(404);self.end_headers();return
            body=json.dumps({"ok":True,"data":{"version":version,"project":str(expected)}}).encode()
            self.send_response(200);self.send_header("Content-Type","application/json")
            self.send_header("Content-Length",str(len(body)));self.end_headers();self.wfile.write(body)
    srv=HTTPServer(("127.0.0.1",p),H)
    th=threading.Thread(target=srv.serve_forever,daemon=True);th.start()
    try:
        rc,j=run_guard(p,p+3)
        assert rc==0 and j["action"]=="REUSE" and j["selected_port"]==p
    finally:
        srv.shutdown();srv.server_close();th.join(timeout=2)

def test_strict_mode_refuses_occupied_port():
    p=free_port();s=socket.socket();s.bind(("127.0.0.1",p));s.listen(1)
    env=os.environ.copy();env["PROVOWARE_PORT_STRICT"]="1"
    try:
        rc,j=run_guard(p,p+5,env)
        assert rc==98 and j["action"]=="ERROR"
    finally:s.close()

if __name__=="__main__":
    tests=[v for k,v in sorted(globals().items()) if k.startswith("test_")]
    bad=[]
    for t in tests:
        try:t();print("PASS",t.__name__)
        except Exception as e:bad.append((t.__name__,repr(e)));print("FAIL",t.__name__,repr(e))
    print(f"SUMMARY total={len(tests)} passed={len(tests)-len(bad)} failed={len(bad)}")
    raise SystemExit(1 if bad else 0)
