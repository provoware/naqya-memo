
from pathlib import Path
import subprocess, os, sys, socket, tempfile, time, json, urllib.request, traceback

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"registry/evidence/v0.12.2.2/browser"
OUT.mkdir(parents=True,exist_ok=True)

def free_port():
    s=socket.socket();s.bind(("127.0.0.1",0));p=s.getsockname()[1];s.close();return p

port=free_port()
tmp=tempfile.TemporaryDirectory()
env=os.environ.copy()
env["PROVOWARE_PORT"]=str(port)
env["PROVOWARE_PROJECT_PATH"]=str(Path(tmp.name)/"project")
server=subprocess.Popen([sys.executable,"-S",str(ROOT/"app/server.py"),"--no-browser"],
                        cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
result={"status":"BLOCKED","viewports":[]}
try:
    ready=False
    for _ in range(100):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health",timeout=.2) as r:
                ready=json.loads(r.read()).get("ok",False)
                if ready: break
        except Exception:
            time.sleep(.05)
    if not ready: raise RuntimeError("server not ready")

    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path="/usr/bin/chromium",
                                   args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu"])
        cases=[
            ("desktop_1600x900",1600,900,1.0,1.0),
            ("desktop_1366x768",1366,768,1.0,1.0),
            ("desktop_font150_zoom150",1600,900,1.5,1.5),
            ("desktop_font200_zoom200",1600,900,2.0,2.0),
            ("mobile_390x844",390,844,1.0,1.0),
        ]
        for name,w,h,font,zoom in cases:
            page=browser.new_page(viewport={"width":w,"height":h})
            page.goto(f"http://127.0.0.1:{port}/index.html",wait_until="networkidle",timeout=10000)
            if font>1:
                for _ in range(round((font-1)/.1)): page.locator("#fontUp").click(timeout=1500)
                page.wait_for_timeout(100)
            if zoom>1:
                for _ in range(round((zoom-1)/.1)): page.locator("#zoomIn").click(timeout=1500)
            page.wait_for_timeout(200)
            metrics=page.evaluate("""() => {
              const sel=['.app-shell','.topbar','.display-strip','.quickbar','.workspace','.module-host','.nav-panel'];
              const boxes={};
              for(const s of sel){
                const e=document.querySelector(s); if(!e) continue;
                const r=e.getBoundingClientRect();
                boxes[s]={clientWidth:e.clientWidth,scrollWidth:e.scrollWidth,clientHeight:e.clientHeight,scrollHeight:e.scrollHeight,
                  left:r.left,right:r.right,top:r.top,bottom:r.bottom,
                  horizontalOverflow:e.scrollWidth>e.clientWidth+2,
                  outsideViewport:r.left<-2||r.right>innerWidth+2};
              }
              const controls=[...document.querySelectorAll('.display-strip button,.display-strip output')].map(e=>{
                const r=e.getBoundingClientRect();return {id:e.id,left:r.left,right:r.right,top:r.top,bottom:r.bottom,
                  outside:r.left<-2||r.right>innerWidth+2||r.top<-2||r.bottom>innerHeight+2};
              });
              return {innerWidth,innerHeight,boxes,controls,
                bodyHorizontal:document.documentElement.scrollWidth>document.documentElement.clientWidth+2};
            }""")
            shot=OUT/f"{name}.png";page.screenshot(path=str(shot),full_page=True)
            result["viewports"].append({"case":name,"font":font,"zoom":zoom,"metrics":metrics,"screenshot":shot.name})
            page.close()
        browser.close()
        hard=[]
        for case in result["viewports"][:4]:
            m=case["metrics"]
            if m["bodyHorizontal"]: hard.append(f"{case['case']}: body horizontal overflow")
            for sel in [".app-shell",".topbar",".display-strip",".workspace"]:
                if m["boxes"].get(sel,{}).get("horizontalOverflow"):
                    hard.append(f"{case['case']}: {sel} overflow")
                if m["boxes"].get(sel,{}).get("outsideViewport"):
                    hard.append(f"{case['case']}: {sel} outside viewport")
        result["status"]="PASS" if not hard else "FAIL"
        result["hard_failures"]=hard
except Exception as e:
    result["status"]="BLOCKED"
    result["reason"]=repr(e)
    result["trace"]=traceback.format_exc()[-3000:]
finally:
    server.terminate()
    try:server.wait(timeout=5)
    except:server.kill()
    tmp.cleanup()

(OUT/"VISUAL_LAYOUT_ACCEPTANCE.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps(result,ensure_ascii=False))
raise SystemExit(0 if result["status"]=="PASS" else 2)
