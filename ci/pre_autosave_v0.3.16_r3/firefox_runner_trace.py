#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, os, platform, subprocess, time
from pathlib import Path
KIT_FOLDER='Provoware_Naqya_CROSS_PLATFORM_ACCEPTANCE_KIT_v0.3.16'

def main():
    rt=Path(os.environ['RUNNER_TEMP']); kit=rt/'naqya-kit-r3'/KIT_FOLDER
    runner_path=kit/'ENTWICKLUNG_LOKAL_NICHT_INS_REPO/werkzeuge/cross_platform_runner_FERTIG_v0.3.16.py'
    spec=importlib.util.spec_from_file_location('naqya_runner_trace_target',runner_path); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    ff=m.find_firefox(); assert ff, 'Firefox not found'
    trace=[]; current={'url':None,'proc':None}
    def rec(kind,**kw):
        item={'t':round(time.time(),3),'kind':kind,**kw};trace.append(item);print(json.dumps(item,ensure_ascii=False),flush=True)
    def log_message(self,fmt,*args): rec('http',message=fmt%args,path=getattr(self,'path',None))
    m.Handler.log_message=log_message
    def spawn(ffx,profile,url):
        cmd=[ffx,'-headless','-profile',str(profile),url];rec('spawn',url=url,cmd=cmd)
        kwargs={'stdout':subprocess.PIPE,'stderr':subprocess.STDOUT,'text':True}
        if platform.system()=='Windows': kwargs['creationflags']=subprocess.CREATE_NEW_PROCESS_GROUP
        else: kwargs['start_new_session']=True
        p=subprocess.Popen(cmd,**kwargs);current['url']=url;current['proc']=p;return p
    m.spawn_firefox=spawn
    orig_wait=m.wait_state
    def wait(state,want,timeout):
        rec('wait_begin',want=want,url=current['url'],timeout=timeout)
        try:
            r=orig_wait(state,want,timeout);rec('wait_pass',want=want,url=current['url'],value=r);return r
        except Exception as e:
            p=current.get('proc');out=''
            if p and p.poll() is None:m.kill_tree(p)
            if p and p.stdout:
                try:out=p.stdout.read()[-12000:]
                except Exception:pass
            rec('wait_fail',want=want,url=current['url'],error=repr(e),browserOutputTail=out)
            raise
    m.wait_state=wait
    try:
        result=m.firefox_tests(ff);rec('firefox_tests_pass',result=result);status='PASS'
    except Exception as e:
        rec('firefox_tests_fail',error=repr(e));status='FAIL'
    out=rt/'naqya-firefox-runner-trace.json';out.write_text(json.dumps({'status':status,'firefox':ff,'trace':trace},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('TRACE_FILE',out)
    return 0 if status=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
