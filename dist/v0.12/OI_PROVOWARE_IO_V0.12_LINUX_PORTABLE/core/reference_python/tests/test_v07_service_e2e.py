from pathlib import Path
import subprocess, sys, os, time, json, urllib.request, urllib.error, tempfile, signal
ROOT=Path(__file__).resolve().parents[3]
SERVER=ROOT/'app'/'server.py'
PORT='18765'
def req(path,method='GET',body=None):
    data=None if body is None else json.dumps(body).encode()
    r=urllib.request.Request(f'http://127.0.0.1:{PORT}{path}',data=data,method=method,headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(r,timeout=3) as x:return json.loads(x.read())
def wait():
    for _ in range(50):
        try:
            if req('/api/health')['ok']:return
        except Exception: time.sleep(.1)
    raise RuntimeError('server not ready')
def run():
    env=os.environ.copy();env['PROVOWARE_PORT']=PORT
    tmp=tempfile.TemporaryDirectory(); env['PROVOWARE_PROJECT_PATH']=str(Path(tmp.name)/'projekt')
    p=subprocess.Popen([sys.executable,str(SERVER),'--no-browser'],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        wait()
        s=req('/api/state');assert s['ok'] and s['data']['integrity']=='ok'
        m=req('/api/memos','POST',{'title':'E2E Memo','body':'Hallo','tags':['test']});assert m['ok']
        t=req('/api/todos','POST',{'title':'E2E Todo','description':'x'});assert t['ok']
        c=s['data']['colors'][0]['id'];e=req('/api/events','POST',{'title':'E2E Termin','start_at':'2026-09-01T12:00:00+00:00','color_id':c});assert e['ok']
        n=req('/api/quick-note','POST',{'title':'E2E','text':'Testzeile'});assert n['ok'] and Path(n['data']['path']).exists()
        st=req('/api/state')['data'];assert st['counts']['memos']>=1 and st['counts']['todos']>=1 and st['counts']['events']>=1
        print('PASS api_state');print('PASS memo_ui_service_path');print('PASS todo_ui_service_path');print('PASS calendar_ui_service_path');print('PASS quick_note_file_path');print('SUMMARY total=5 passed=5 failed=0')
    finally:
        p.terminate()
        try:p.wait(timeout=3)
        except:p.kill()
        tmp.cleanup()
if __name__=='__main__':run()
