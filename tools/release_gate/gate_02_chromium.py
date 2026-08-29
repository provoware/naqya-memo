from pathlib import Path
import datetime, json, os, shutil, signal, socket, subprocess, sys, tempfile, time, urllib.request
ROOT=Path(__file__).resolve().parents[2]; E=ROOT/'registry/evidence/v0.12.2/gates/GATE_02_CHROMIUM.json'
def port():
 s=socket.socket();s.bind(('127.0.0.1',0));p=s.getsockname()[1];s.close();return p
exe=shutil.which('chromium') or shutil.which('chromium-browser')
out={'gate':'GATE_02_CHROMIUM','status':'BLOCKED','browser':exe,'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
if exe:
 with tempfile.TemporaryDirectory() as td:
  pnum=port(); env=os.environ.copy(); env['PROVOWARE_PORT']=str(pnum); env['PROVOWARE_PROJECT_PATH']=str(Path(td)/'project')
  srv=subprocess.Popen([sys.executable,'-S',str(ROOT/'app/server.py'),'--no-browser'],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
  try:
   ready=False
   for _ in range(100):
    try: urllib.request.urlopen(f'http://127.0.0.1:{pnum}/api/health',timeout=.2).read();ready=True;break
    except: time.sleep(.05)
   out['service_ready']=ready
   if ready:
    shot=ROOT/'registry/evidence/v0.12.2/chromium_1366x768.png'
    cmd=[exe,'--headless','--no-sandbox','--disable-dev-shm-usage','--disable-gpu','--window-size=1366,768',f'--screenshot={shot}',f'http://127.0.0.1:{pnum}/index.html']
    try:
     cp=subprocess.run(cmd,text=True,capture_output=True,timeout=12)
     out['return_code']=cp.returncode; out['stderr_tail']=cp.stderr[-2000:]
     if cp.returncode==0 and shot.exists() and shot.stat().st_size>1000:
      out['status']='PASS';out['screenshot']=shot.name
     else: out['reason']='Chromium returned without valid screenshot'
    except subprocess.TimeoutExpired as exc:
     out['reason']='Chromium headless timed out in this execution environment'; out['timeout_seconds']=12
  finally:
   try: os.killpg(srv.pid,signal.SIGTERM)
   except: pass
   try:srv.wait(timeout=3)
   except: 
    try:os.killpg(srv.pid,signal.SIGKILL)
    except:pass
out['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();E.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False))
raise SystemExit(0 if out['status']=='PASS' else 2)
