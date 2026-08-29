
from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parents[2]
H=(ROOT/"ui/reference_web/index.html").read_text(encoding="utf-8")
J=(ROOT/"ui/reference_web/app.js").read_text(encoding="utf-8")
C=(ROOT/"ui/reference_web/styles.css").read_text(encoding="utf-8")

def test_exactly_one_visible_version_location():
    version_ids=re.findall(r'id="([^"]*Version[^"]*)"',H)
    assert version_ids==["toolVersion"], version_ids
    for stale in ("buildVersion","brandVersion","checkpointVersion","devVersion"):
        assert stale not in H
    assert "Service-Pfad</h3><strong>V" not in J
    assert "document.title='OI - PROVOWARE - IO'" in J

def test_input_palette_is_not_brand_palette():
    assert "--input-contrast:#b7c1cc" in C
    assert "--input-focus:#f4f7fb" in C
    # final input contract may not use the three brand colors as its border/focus.
    final=C[C.index("V0.12.2.3 UI SIMPLIFICATION & INPUT GUIDANCE"):]
    input_block=final[final.index("input,textarea,select"):final.index(".field-hint")]
    for brand in ("#19f4f2","#bd42ff","#ffe53b"):
        assert brand not in input_block.lower()

def test_all_user_input_categories_have_optional_guidance():
    # Hidden technical IDs are intentionally excluded.
    expected={"title","body","tags","description","due_at","reminder_at","start_at","end_at",
              "priority","color_id","all_day","file","source_path","help_mode"}
    for name in expected:
        assert re.search(rf"\b{name}:\s*\{{",J), name
    assert "title\\d+" in J and "token\\d+" in J
    assert "quickTitle" in J and "quickInput" in J and "docEditor" in J
    assert "applyFieldGuidance(host)" in J
    assert 'className=\'field-hint\'' in J

def test_complexity_is_reduced_not_shifted():
    assert H.count('class="status-chip')==3
    assert "simplified-dashboard" in J
    dash=J[J.index("function dash()"):J.index("async function memoView")]
    assert dash.count('class="dash-card')==4
    assert "Service-Pfad" not in dash
    assert "BUILD" not in H[H.index('status-strip'):H.index('next-items')]
    settings=J[J.index("function settingsView()"):J.index("function bindModule")]
    assert "Aktuelle Darstellung" not in settings

def test_display_controls_stay_top_and_unique():
    assert H.index('class="display-strip"') < H.index('class="quickbar"')
    for ident in ("themeBtn","fontDown","fontUp","zoomOut","zoomIn","zoomReset"):
        assert H.count(f'id="{ident}"')==1

def test_left_nav_and_zoom_have_hard_overflow_guards():
    final=C[C.index("V0.12.2.3 UI SIMPLIFICATION & INPUT GUIDANCE"):]
    assert "overflow-x:hidden" in final
    assert ".nav-item{" in final and "min-height:49px" in final
    assert 'data-zoom-tier="large"' in C and 'data-zoom-tier="xl"' in C
    assert ".module-host[data-zoom-tier=\"xl\"] .form-grid" in final
    assert "@media(max-width:720px)" in final

def test_version_registry_matches_generated_mobile_build_info():
    v=json.loads((ROOT/"registry/VERSION.json").read_text(encoding="utf-8"))["version"]
    build=(ROOT/"ui/reference_web/build_info.js").read_text(encoding="utf-8")
    assert v in build

if __name__=="__main__":
    tests=[v for k,v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    bad=[]
    for t in tests:
        try:t();print("PASS",t.__name__)
        except Exception as e:bad.append((t.__name__,repr(e)));print("FAIL",t.__name__,repr(e))
    print(f"SUMMARY total={len(tests)} passed={len(tests)-len(bad)} failed={len(bad)}")
    raise SystemExit(1 if bad else 0)
