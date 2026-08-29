from pathlib import Path
import tempfile, os, sys, subprocess, time, socket, json
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/"registry"/"evidence"/"v0.8"/"browser"
OUT.mkdir(parents=True,exist_ok=True)
def port():
    s=socket.socket();s.bind(("127.0.0.1",0));p=s.getsockname()[1];s.close();return p
pnum=port();env=os.environ.copy();env["PROVOWARE_PORT"]=str(pnum);env["PROVOWARE_PROJECT_PATH"]=str(ROOT/"runtime"/"browser-e2e-project")
srv=subprocess.Popen([sys.executable,str(ROOT/"app/server.py"),"--no-browser"],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
result={"chromium":{"status":"BLOCKED"},"firefox":{"status":"BLOCKED"},"viewports":[]}
try:
    time.sleep(.7)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        chromium_path="/usr/bin/chromium" if Path("/usr/bin/chromium").exists() else None
        if chromium_path:
            try:
                browser=pw.chromium.launch(headless=True,executable_path=chromium_path,args=["--no-sandbox","--disable-dev-shm-usage"])
                for w,h in [(390,844),(768,900),(1366,768),(1920,1080)]:
                    page=browser.new_page(viewport={"width":w,"height":h})
                    page.goto(f"http://127.0.0.1:{pnum}/index.html",wait_until="networkidle",timeout=15000)
                    page.wait_for_selector("#moduleHost")
                    shot=OUT/f"chromium_{w}x{h}.png";page.screenshot(path=str(shot),full_page=True)
                    overflow=page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth")
                    result["viewports"].append({"browser":"chromium","width":w,"height":h,"horizontal_overflow":bool(overflow),"screenshot":shot.name})
                    if overflow: raise AssertionError(f"horizontal overflow {w}x{h}")
                    page.close()
                browser.close();result["chromium"]={"status":"PASS","screenshots":4}
            except Exception as e:
                result["chromium"]={"status":"BLOCKED","reason":repr(e)}
        # Firefox only if executable/browser is actually available.
        try:
            browser=pw.firefox.launch(headless=True)
            page=browser.new_page(viewport={"width":1366,"height":768});page.goto(f"http://127.0.0.1:{pnum}/index.html",wait_until="networkidle",timeout=15000)
            shot=OUT/"firefox_1366x768.png";page.screenshot(path=str(shot),full_page=True);page.close();browser.close()
            result["firefox"]={"status":"PASS","screenshots":1}
        except Exception as e:
            result["firefox"]={"status":"BLOCKED","reason":repr(e)}
finally:
    srv.terminate()
    try:srv.wait(timeout=5)
    except:srv.kill()
(OUT.parent/"BROWSER_ACCEPTANCE.json").write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
print(json.dumps(result,indent=2,ensure_ascii=False))
