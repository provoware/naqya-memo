
from pathlib import Path
import os,sys,socket,tempfile,subprocess,time,json,urllib.request,traceback

ROOT=Path(__file__).resolve().parents[2]
VERSION=json.loads((ROOT/"registry/VERSION.json").read_text(encoding="utf-8"))["version"]
OUT=ROOT/"registry"/"evidence"/"v0.12.2.3"/"browser"
OUT.mkdir(parents=True,exist_ok=True)

VIEWS=["dashboard","memo","todo","calendar","trash","diagnostics","voice","docs","audio","settings"]
CASES=[
    ("desktop100",1600,900,1.0,1.0),
    ("desktop150",1600,900,1.5,1.5),
    ("desktop200",1920,1080,2.0,2.0),
    ("compact",1366,768,1.0,1.0),
    ("mobile",390,844,1.0,1.0),
]

def port():
    s=socket.socket();s.bind(("127.0.0.1",0));p=s.getsockname()[1];s.close();return p

def overlap_pairs(page):
    return page.evaluate("""() => {
      const els=[...document.querySelectorAll('button,input,textarea,select,a[href]')]
        .filter(e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&r.width>2&&r.height>2});
      const out=[];
      for(let i=0;i<els.length;i++) for(let k=i+1;k<els.length;k++){
        const a=els[i],b=els[k];
        if(a.contains(b)||b.contains(a))continue;
        const r1=a.getBoundingClientRect(),r2=b.getBoundingClientRect();
        const w=Math.min(r1.right,r2.right)-Math.max(r1.left,r2.left);
        const h=Math.min(r1.bottom,r2.bottom)-Math.max(r1.top,r2.top);
        if(w>3&&h>3)out.push([a.id||a.name||a.textContent.trim().slice(0,28),b.id||b.name||b.textContent.trim().slice(0,28)]);
      }
      return out.slice(0,20);
    }""")

pnum=port()
tmp=tempfile.TemporaryDirectory()
env=os.environ.copy()
env["PROVOWARE_PORT"]=str(pnum)
env["PROVOWARE_PROJECT_PATH"]=str(Path(tmp.name)/"project")
proc=subprocess.Popen([sys.executable,"-S",str(ROOT/"app/server.py"),"--no-browser"],
                      cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
result={"version":VERSION,"status":"BLOCKED","cases":[]}
try:
    ready=False
    for _ in range(120):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{pnum}/api/health",timeout=.25) as r:
                ready=json.loads(r.read()).get("ok",False)
            if ready:break
        except Exception:time.sleep(.05)
    if not ready:raise RuntimeError("Backend nicht bereit")

    from playwright.sync_api import sync_playwright
    chromium=os.environ.get("PROVOWARE_CHROMIUM","/usr/bin/chromium")
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=chromium,
            args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu"])
        failures=[]
        for cname,w,h,font,zoom in CASES:
            page=browser.new_page(viewport={"width":w,"height":h})
            page.goto(f"http://127.0.0.1:{pnum}/index.html",wait_until="networkidle",timeout=15000)
            if font>1:
                for _ in range(round((font-1)/.1)):page.locator("#fontUp").click()
            if zoom>1:
                for _ in range(round((zoom-1)/.1)):page.locator("#zoomIn").click()
            for view in VIEWS:
                if view!="dashboard":
                    sel=f'[data-view="{view}"]'
                    if page.locator(sel).count():
                        page.locator(sel).click()
                page.wait_for_timeout(120)
                metrics=page.evaluate("""() => {
                  const host=document.querySelector('.module-host'),work=document.querySelector('.workspace'),
                        nav=document.querySelector('.nav-panel'),disp=document.querySelector('.display-strip');
                  const check=e=>e?{
                    cw:e.clientWidth,sw:e.scrollWidth,ch:e.clientHeight,sh:e.scrollHeight,
                    horizontal:e.scrollWidth>e.clientWidth+3,
                    rect:(()=>{const r=e.getBoundingClientRect();return {l:r.left,r:r.right,t:r.top,b:r.bottom}})()
                  }:null;
                  return {
                    bodyHorizontal:document.documentElement.scrollWidth>document.documentElement.clientWidth+3,
                    host:check(host),workspace:check(work),nav:check(nav),display:check(disp),
                    versionVisible:[...document.querySelectorAll('#toolVersion')].filter(e=>e.offsetParent!==null).length
                  };
                }""")
                overlaps=overlap_pairs(page)
                issue=[]
                if metrics["bodyHorizontal"]:issue.append("body-horizontal-overflow")
                if metrics["workspace"] and metrics["workspace"]["horizontal"]:issue.append("workspace-horizontal-overflow")
                if metrics["host"] and metrics["host"]["horizontal"]:issue.append("module-horizontal-overflow")
                if metrics["versionVisible"]>1:issue.append("multiple-visible-version")
                if overlaps:issue.append(f"interactive-overlap:{overlaps[:3]}")
                shot=OUT/f"{cname}_{view}.png"
                page.screenshot(path=str(shot),full_page=True)
                rec={"case":cname,"view":view,"font":font,"zoom":zoom,"metrics":metrics,
                     "overlaps":overlaps,"issues":issue,"screenshot":shot.name}
                result["cases"].append(rec)
                failures.extend([f"{cname}/{view}: {x}" for x in issue])
            page.close()
        browser.close()
        result["failures"]=failures
        result["status"]="PASS" if not failures else "FAIL"
except Exception as exc:
    result["status"]="BLOCKED"
    result["reason"]=repr(exc)
    result["trace"]=traceback.format_exc()[-3000:]
finally:
    proc.terminate()
    try:proc.wait(timeout=5)
    except:proc.kill()
    tmp.cleanup()

(OUT/"ALL_VIEWS_VISUAL_ACCEPTANCE.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps({"status":result["status"],"failures":result.get("failures",[])[:20],"reason":result.get("reason")},ensure_ascii=False))
raise SystemExit(0 if result["status"]=="PASS" else 2)
