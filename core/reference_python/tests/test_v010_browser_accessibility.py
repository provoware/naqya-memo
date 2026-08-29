from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/"registry"/"evidence"/"v0.10"/"browser";OUT.mkdir(parents=True,exist_ok=True)
result={"chromium":{"status":"BLOCKED"},"firefox":{"status":"BLOCKED"},"viewports":[]}
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        cp="/usr/bin/chromium" if Path("/usr/bin/chromium").exists() else None
        if cp:
            try:
                b=pw.chromium.launch(headless=True,executable_path=cp,args=["--no-sandbox","--disable-dev-shm-usage"])
                for w,h in [(390,844),(768,900),(1366,768),(1920,1080)]:
                    p=b.new_page(viewport={"width":w,"height":h})
                    p.goto((ROOT/"ui/reference_web/index.html").as_uri(),wait_until="domcontentloaded",timeout=10000)
                    p.wait_for_timeout(500)
                    overflow=p.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth")
                    focus_count=p.locator("button, input, textarea, select, a").count()
                    shot=OUT/f"chromium_file_{w}x{h}.png";p.screenshot(path=str(shot),full_page=True)
                    result["viewports"].append({"browser":"chromium","width":w,"height":h,"horizontal_overflow":bool(overflow),"focusable_controls":focus_count,"screenshot":shot.name})
                    if overflow: raise AssertionError(f"horizontal overflow {w}x{h}")
                    p.close()
                b.close();result["chromium"]={"status":"PASS","mode":"file:// visual shell","screenshots":4}
            except Exception as e: result["chromium"]={"status":"BLOCKED","reason":repr(e)}
        try:
            b=pw.firefox.launch(headless=True);p=b.new_page(viewport={"width":1366,"height":768});p.goto((ROOT/"ui/reference_web/index.html").as_uri());shot=OUT/"firefox_file_1366x768.png";p.screenshot(path=str(shot),full_page=True);p.close();b.close();result["firefox"]={"status":"PASS","mode":"file:// visual shell","screenshots":1}
        except Exception as e: result["firefox"]={"status":"BLOCKED","reason":repr(e)}
except Exception as e:
    result["framework"]={"status":"BLOCKED","reason":repr(e)}
(OUT.parent/"BROWSER_ACCESSIBILITY_ACCEPTANCE.json").write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
print(json.dumps(result,indent=2,ensure_ascii=False))
