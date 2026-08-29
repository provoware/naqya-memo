from pathlib import Path
import tempfile, subprocess, sys, os, socket, time, json, urllib.request
ROOT=Path(__file__).resolve().parents[3]
def port():
    s=socket.socket();s.bind(('127.0.0.1',0));p=s.getsockname()[1];s.close();return p
def req(base,path,method='GET',body=None,raw=False):
    data=None if body is None else json.dumps(body).encode();r=urllib.request.Request(base+path,data=data,method=method,headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(r,timeout=5) as x:
        if raw:return x.read(),x.headers.get_content_type()
        j=json.loads(x.read());return j['data']
if __name__=='__main__':
    with tempfile.TemporaryDirectory() as td:
        b=Path(td);pdf=b/'a.pdf';pdf.write_bytes(b'%PDF-1.4\n%%EOF');txt=b/'a.txt';txt.write_text('eins',encoding='utf-8')
        pnum=port();env=os.environ.copy();env['PROVOWARE_PORT']=str(pnum);env['PROVOWARE_PROJECT_PATH']=str(b/'project')
        p=subprocess.Popen([sys.executable,str(ROOT/'app/server.py'),'--no-browser'],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        base=f'http://127.0.0.1:{pnum}'
        try:
            for _ in range(70):
                try:req(base,'/api/health');break
                except:time.sleep(.1)
            pm=req(base,'/api/assets/import','POST',{'source_path':str(pdf),'kind':'document','title':'PDF'})
            raw,ctype=req(base,f"/asset-file/{pm['asset_id']}",raw=True);assert raw.startswith(b'%PDF') and ctype=='application/pdf'
            tm=req(base,'/api/assets/import','POST',{'source_path':str(txt),'kind':'document','title':'Text'})
            tx=req(base,f"/api/assets/{tm['asset_id']}/text");assert tx['text']=='eins'
            ed=req(base,'/api/assets/edit-text','POST',{'asset_id':tm['asset_id'],'text':'zwei','revision':1});assert ed['revision']==2
            print('PASS service_pdf_view_text_revision')
        finally:
            p.terminate();
            try:p.wait(timeout=5)
            except:p.kill()
