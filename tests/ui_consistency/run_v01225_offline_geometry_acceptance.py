
from pathlib import Path
import json,re,traceback

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"registry/evidence/v0.12.2.5/offline-geometry"
OUT.mkdir(parents=True,exist_ok=True)

HTML=(ROOT/"ui/reference_web/index.html").read_text(encoding="utf-8")
CSS=(ROOT/"ui/reference_web/styles.css").read_text(encoding="utf-8")

HTML=re.sub(r'<link rel="stylesheet" href="styles.css">',f'<style>{CSS}</style>',HTML)
HTML=re.sub(r'<script[^>]*>.*?</script>','',HTML,flags=re.S)
HTML=re.sub(r'<script[^>]*/?>','',HTML)
HTML=HTML.replace(
    '<section class="module-host" id="moduleHost"></section>',
    """<section class="module-host" id="moduleHost">
      <div class="dashboard-grid simplified-dashboard">
        <article class="dash-card"><div><h3>Textmemos</h3><p>Notizen schreiben und wiederfinden.</p></div><strong>12</strong></article>
        <article class="dash-card"><div><h3>Todos</h3><p>Aufgaben und Erinnerungen.</p></div><strong>8</strong></article>
        <article class="dash-card"><div><h3>Kalender</h3><p>Termine und Tagesmarkierungen.</p></div><strong>4</strong></article>
        <article class="dash-card safety-card"><div><h3>Sicherheit</h3><p>Papierkorb 0 · Backup 4 Gen.</p></div><strong>OK</strong></article>
      </div>
    </section>"""
)

CASES=[
  {"name":"desktop_1920","w":1920,"h":1080,"font":1.0,"zoom":1.0,"tier":"normal"},
  {"name":"desktop_1600","w":1600,"h":900,"font":1.0,"zoom":1.0,"tier":"normal"},
  {"name":"desktop_1366","w":1366,"h":768,"font":1.0,"zoom":1.0,"tier":"normal"},
  {"name":"desktop_150","w":1600,"h":900,"font":1.5,"zoom":1.5,"tier":"large"},
  {"name":"desktop_200","w":1920,"h":1080,"font":2.0,"zoom":2.0,"tier":"xl"},
  {"name":"compact_1100","w":1100,"h":800,"font":1.0,"zoom":1.0,"tier":"normal"},
  {"name":"compact_900","w":900,"h":760,"font":1.0,"zoom":1.0,"tier":"normal"},
  {"name":"mobile_390","w":390,"h":844,"font":1.0,"zoom":1.0,"tier":"normal"},
]

def rect_intersection(a,b):
    x=max(0,min(a["right"],b["right"])-max(a["left"],b["left"]))
    y=max(0,min(a["bottom"],b["bottom"])-max(a["top"],b["top"]))
    return x*y

result={"status":"BLOCKED","cases":[]}
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser=pw.chromium.launch(
            headless=True,
            executable_path="/usr/bin/chromium",
            args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu"]
        )
        failures=[]
        for case in CASES:
            page=browser.new_page(viewport={"width":case["w"],"height":case["h"]})
            page.set_content(HTML,wait_until="domcontentloaded",timeout=10000)
            page.evaluate("""(c)=>{
              document.documentElement.style.setProperty('--font-scale',String(c.font));
              document.documentElement.dataset.fontTier=c.font>=1.6?'xl':c.font>=1.3?'large':'normal';
              document.documentElement.dataset.viewport=c.w<=720?'mobile':c.w<1280?'compact':'desktop';
              const host=document.querySelector('#moduleHost');
              document.documentElement.style.setProperty('--area-zoom',String(c.zoom));
              host.dataset.zoomTier=c.tier;
              document.querySelector('#devPanel').hidden=true;
              document.querySelector('.side-panel')?.classList.remove('overlay-open');
            }""",case)
            page.wait_for_timeout(80)
            metrics=page.evaluate("""() => {
              const selectors=['.app-shell','.topbar','.nav-panel','.quickbar','.workspace','.display-strip','.status-strip','.next-items','.side-panel','.footerbar'];
              const boxes={};
              for(const s of selectors){
                const e=document.querySelector(s); if(!e)continue;
                const cs=getComputedStyle(e); const r=e.getBoundingClientRect();
                boxes[s]={
                  display:cs.display,visibility:cs.visibility,
                  left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height,
                  clientWidth:e.clientWidth,scrollWidth:e.scrollWidth,clientHeight:e.clientHeight,scrollHeight:e.scrollHeight,
                  horizontal:e.scrollWidth>e.clientWidth+3,
                  vertical:e.scrollHeight>e.clientHeight+3,
                  outside:r.left<-3||r.right>innerWidth+3
                };
              }
              const navLabels=[...document.querySelectorAll('.nav-label')].map(e=>{
                const r=e.getBoundingClientRect(),lh=parseFloat(getComputedStyle(e).lineHeight)||14;
                return {text:e.textContent.trim(),width:r.width,height:r.height,lines:Math.round(r.height/lh)};
              });
              const displayControls=[...document.querySelectorAll('.display-strip button,.display-strip output')].map(e=>{
                const r=e.getBoundingClientRect();
                return {id:e.id,left:r.left,right:r.right,top:r.top,bottom:r.bottom,
                        outside:r.left<-2||r.right>innerWidth+2||r.top<-2||r.bottom>innerHeight+2};
              });
              return {
                vw:innerWidth,vh:innerHeight,
                docHorizontal:document.documentElement.scrollWidth>document.documentElement.clientWidth+3,
                boxes,navLabels,displayControls
              };
            }""")
            issues=[]
            if metrics["docHorizontal"]: issues.append("document-horizontal-overflow")
            for sel in (".app-shell",".topbar",".quickbar",".workspace",".display-strip"):
                b=metrics["boxes"].get(sel)
                if b and b["display"]!="none":
                    if b["horizontal"]:issues.append(f"{sel}-horizontal-overflow")
                    if b["outside"]:issues.append(f"{sel}-outside-viewport")
            if case["w"]>900:
                for n in metrics["navLabels"]:
                    if n["width"]>0 and n["lines"]>2:
                        issues.append(f"nav-label-too-many-lines:{n['text']}:{n['lines']}")
            if any(x["outside"] for x in metrics["displayControls"]):
                issues.append("display-control-outside-viewport")

            top=metrics["boxes"].get(".topbar")
            if top and top.get("vertical"):
                issues.append("topbar-vertical-overflow")
            if case["w"]<=720:
                for critical in (".status-strip",".next-items",".display-strip"):
                    b=metrics["boxes"].get(critical)
                    if not b or b["display"]=="none" or b["height"]<20:
                        issues.append(f"mobile-critical-hidden:{critical}")
                    elif top and (b["top"]<top["top"]-2 or b["bottom"]>top["bottom"]+2):
                        issues.append(f"mobile-critical-outside-topbar:{critical}")

            major=[".nav-panel",".topbar",".quickbar",".workspace",".side-panel",".footerbar"]
            visible=[]
            for s in major:
                b=metrics["boxes"].get(s)
                if b and b["display"]!="none" and b["width"]>2 and b["height"]>2:
                    visible.append((s,b))
            for i in range(len(visible)):
                for k in range(i+1,len(visible)):
                    s1,a=visible[i];s2,b=visible[k]
                    if rect_intersection(a,b)>10:
                        issues.append(f"major-overlap:{s1}:{s2}")

            shot=OUT/f"{case['name']}.png"
            page.screenshot(path=str(shot),full_page=True)
            result["cases"].append({"case":case,"metrics":metrics,"issues":issues,"screenshot":shot.name})
            failures.extend([f"{case['name']}: {x}" for x in issues])
            page.close()
        browser.close()
        result["failures"]=failures
        result["status"]="PASS" if not failures else "FAIL"
except Exception as e:
    result["status"]="BLOCKED"
    result["reason"]=repr(e)
    result["trace"]=traceback.format_exc()[-4000:]

(OUT/"OFFLINE_GEOMETRY_ACCEPTANCE.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps({"status":result["status"],"failures":result.get("failures",[])[:40],"reason":result.get("reason")},ensure_ascii=False))
raise SystemExit(0 if result["status"]=="PASS" else 2)
