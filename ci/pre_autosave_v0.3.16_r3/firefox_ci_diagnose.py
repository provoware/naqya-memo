#!/usr/bin/env python3
from __future__ import annotations
import hashlib, http.server, json, os, re, shutil, socketserver, subprocess, tempfile, threading, time, urllib.request
from pathlib import Path

VERSION='0.3.16'
KIT_FOLDER='Provoware_Naqya_CROSS_PLATFORM_ACCEPTANCE_KIT_v0.3.16'
MODULE='/BASIS_RELEASE/basis/skripte/transaktion_FERTIG_v0.3.16.js'
HARNESS='ENTWICKLUNG_LOKAL_NICHT_INS_REPO/tests/firefox_acceptance_harness_FERTIG_v0.3.16.html'


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def check_inline_module_syntax(script: str) -> dict:
    fd, raw_path=tempfile.mkstemp(prefix='naqya_firefox_harness_',suffix='.mjs')
    os.close(fd)
    path=Path(raw_path)
    try:
        path.write_text(script,encoding='utf-8')
        p=subprocess.run(['node','--check',str(path)],text=True,capture_output=True,timeout=15)
        return {
            'sha256':sha256_text(script),
            'bytes':len(script.encode('utf-8')),
            'returncode':p.returncode,
            'ok':p.returncode==0,
            'stdout':p.stdout[-4000:],
            'stderr':p.stderr[-8000:],
        }
    finally:
        path.unlink(missing_ok=True)


def static_harness_evidence(kit: Path) -> dict:
    path=kit/HARNESS
    assert path.is_file(), f'Firefox acceptance harness missing: {path}'
    text=path.read_text(encoding='utf-8')
    script_tags=re.findall(r'<script\b[^>]*>(.*?)</script\s*>',text,flags=re.I|re.S)
    opening_tags=re.findall(r'<script\b[^>]*>',text,flags=re.I|re.S)
    srcs=[]
    for tag in opening_tags:
        m=re.search(r'\bsrc\s*=\s*["\']([^"\']+)["\']',tag,flags=re.I)
        if m: srcs.append(m.group(1))
    syntax=[check_inline_module_syntax(s) for s in script_tags]
    return {
        'path':HARNESS,
        'bytes':len(text.encode('utf-8')),
        'sha256':sha256_text(text),
        'scriptTagCount':len(opening_tags),
        'scriptSrcs':srcs,
        'hasModuleScript':any(re.search(r'\btype\s*=\s*["\']module["\']',tag,flags=re.I) for tag in opening_tags),
        'mentionsTransactionModule':('transaktion_FERTIG_v0.3.16.js' in text),
        'mentionsStateEndpoint':('/__state__' in text),
        'mentionsPhase':('phase' in text),
        'openingScriptTags':opening_tags[:12],
        'inlineScriptSyntax':syntax,
        'inlineScriptPreviews':[s.strip()[:1200] for s in script_tags[:8]],
        'headPreview':text[:2400],
    }


def main():
    rt=Path(os.environ['RUNNER_TEMP'])
    kit=rt/'naqya-kit-r3'/KIT_FOLDER
    assert kit.is_dir(), kit
    ff=shutil.which('firefox') or shutil.which('firefox.exe')
    assert ff, 'Firefox not found'
    events=[]; requests=[]; lock=threading.Lock()
    static=static_harness_evidence(kit)
    print(json.dumps({'staticHarness':static},indent=2,ensure_ascii=False),flush=True)
    probe=kit/'__ci_firefox_probe__.html'
    probe.write_text('''<!doctype html><meta charset="utf-8"><title>Naqya Firefox CI Diagnose</title><pre id="o">boot</pre><script type="module">\nconst post=async(stage,extra={})=>{try{await fetch('/__diag__',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({stage,ua:navigator.userAgent,...extra})})}catch(e){}};\nawait post('boot',{href:location.href});\ntry{const m=await import("'''+MODULE+'''" ); await post('module',{exports:Object.keys(m)});}catch(e){await post('module_error',{error:String(e?.stack||e)}); throw e;}\ntry{const name='naqya_ci_diag_'+Date.now(); const db=await new Promise((res,rej)=>{const r=indexedDB.open(name,1);r.onupgradeneeded=()=>r.result.createObjectStore('kv');r.onsuccess=()=>res(r.result);r.onerror=()=>rej(r.error)}); await new Promise((res,rej)=>{const t=db.transaction('kv','readwrite');t.objectStore('kv').put('ok','k');t.oncomplete=res;t.onerror=()=>rej(t.error)}); const v=await new Promise((res,rej)=>{const t=db.transaction('kv','readonly'),r=t.objectStore('kv').get('k');r.onsuccess=()=>res(r.result);r.onerror=()=>rej(r.error)}); db.close(); await post('idb',{value:v,indexedDB:'indexedDB' in globalThis,localStorage:'localStorage' in globalThis});}catch(e){await post('idb_error',{error:String(e?.stack||e)});}\n</script>''',encoding='utf-8')

    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(self,*a,**kw): super().__init__(*a,directory=str(kit),**kw)
        def log_message(self,fmt,*args):
            with lock: requests.append(fmt%args)
        def do_POST(self):
            n=int(self.headers.get('content-length','0')); raw=self.rfile.read(n) if n else b'{}'
            try: data=json.loads(raw)
            except Exception: data={'stage':'invalid_json','raw':raw.decode('utf-8','replace')}
            with lock: events.append(data)
            self.send_response(204); self.end_headers()
    class S(socketserver.ThreadingTCPServer): allow_reuse_address=True
    srv=S(('127.0.0.1',0),H); port=srv.server_address[1]
    threading.Thread(target=srv.serve_forever,daemon=True).start()
    url=f'http://127.0.0.1:{port}/__ci_firefox_probe__.html'
    module_url=f'http://127.0.0.1:{port}{MODULE}'
    http_checks={}
    for name,u in [('probe',url),('module',module_url)]:
        with urllib.request.urlopen(u,timeout=5) as r:
            body=r.read(); http_checks[name]={'status':r.status,'contentType':r.headers.get('content-type'),'bytes':len(body)}
    profile=Path(tempfile.mkdtemp(prefix='naqya_ff_ci_diag_'))
    cmd=[ff,'-headless','-profile',str(profile),url]
    env=os.environ.copy(); env['MOZ_CRASHREPORTER_DISABLE']='1'
    p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,env=env,start_new_session=(os.name!='nt'))
    deadline=time.time()+25
    while time.time()<deadline:
        stages={x.get('stage') for x in events}
        if 'idb' in stages or 'idb_error' in stages or 'module_error' in stages: break
        if p.poll() is not None: break
        time.sleep(.2)
    if p.poll() is None:
        p.terminate()
        try:p.wait(timeout=5)
        except subprocess.TimeoutExpired:p.kill();p.wait(timeout=5)
    output=(p.stdout.read() if p.stdout else '')[-12000:]
    srv.shutdown();srv.server_close();shutil.rmtree(profile,ignore_errors=True)
    with lock:
        data={'firefox':ff,'cmd':cmd,'returncode':p.returncode,'staticHarness':static,'httpChecks':http_checks,'events':events,'requests':requests,'browserOutputTail':output}
    out=rt/'naqya-firefox-diag.json';out.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(data,indent=2,ensure_ascii=False))
    stages={x.get('stage') for x in events}
    assert 'boot' in stages, 'Firefox did not execute probe page JavaScript'
    assert 'module' in stages, f'Firefox module import did not pass: {stages}'
    assert 'idb' in stages, f'Firefox IndexedDB probe did not pass: {stages}'
    return 0
if __name__=='__main__': raise SystemExit(main())
