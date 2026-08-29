from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def test_calendar_modes_present():
    j=(ROOT/"ui/reference_web/app.js").read_text(encoding="utf-8")
    for token in ["dayCalendar","weekCalendar","monthCalendar","yearCalendar","data-cal-mode"]:
        assert token in j
def test_accessibility_and_responsive_css():
    h=(ROOT/"ui/reference_web/index.html").read_text(encoding="utf-8")
    c=(ROOT/"ui/reference_web/styles.css").read_text(encoding="utf-8")
    assert "skip-link" in h and 'aria-live="polite"' in h
    assert "@media(max-width:720px)" in c and "@media(prefers-reduced-motion:reduce)" in c
    assert ".calendar-week" in c and ".year-grid" in c
if __name__=="__main__":
    tests=[v for k,v in sorted(globals().items()) if k.startswith("test_")]
    bad=[]
    for t in tests:
        try:t();print("PASS",t.__name__)
        except Exception as e:bad.append((t.__name__,repr(e)));print("FAIL",t.__name__,repr(e))
    print(f"SUMMARY total={len(tests)} passed={len(tests)-len(bad)} failed={len(bad)}")
    if bad:raise SystemExit(1)
