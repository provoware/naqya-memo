from pathlib import Path
import tempfile, subprocess, sys, os, socket, time, urllib.request, json
ROOT=Path(__file__).resolve().parents[3]
def port():
    s=socket.socket();s.bind(('127.0.0.1',0));p=s.getsockname()[1];s.close();return p
with tempfile.TemporaryDirectory() as td:
    pnum=port();env=os.environ.copy();env['PROVOWARE_PORT']=str(pnum);env['PROVOWARE_PROJECT_PATH']=str(Path(td)/'project');t0=time.perf_counter();proc=subprocess.Popen([sys.executable,str(ROOT/'app/server.py'),'--no-browser'],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);ready=False
    try:
        for _ in range(100):
            try:
                with urllib.request.urlopen(f'http://127.0.0.1:{pnum}/api/health',timeout=.3): ready=True;break
            except Exception:time.sleep(.05)
        startup=time.perf_counter()-t0;result={'ready':ready,'startup_seconds':round(startup,3),'budget_seconds':5.0,'pass':ready and startup<5};print(json.dumps(result));raise SystemExit(0 if result['pass'] else 1)
    finally:
        proc.terminate()
        try:proc.wait(timeout=5)
        except:proc.kill()
