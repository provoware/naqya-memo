
from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parents[2]
H=(ROOT/"ui/reference_web/index.html").read_text(encoding="utf-8")
J=(ROOT/"ui/reference_web/app.js").read_text(encoding="utf-8")
C=(ROOT/"ui/reference_web/styles.css").read_text(encoding="utf-8")

def test_nav_has_real_desktop_width_and_collapse_mode():
    final=C[C.index("V0.12.2.5 REAL VIEWPORT UX FIX"):]
    assert "--nav-w:168px" in final
    assert ".app-shell.nav-collapsed{--nav-w:68px}" in final
    assert 'id="navCollapseBtn"' in H
    assert "setNavCollapsed(" in J
    assert "v012-nav-collapsed" in J

def test_nav_labels_do_not_character_wrap():
    final=C[C.index("V0.12.2.5 REAL VIEWPORT UX FIX"):]
    block=final[final.index(".nav-label{"):final.index(".app-shell.nav-collapsed .nav-head")]
    assert "word-break:keep-all" in block
    assert "overflow-wrap:normal" in block
    assert "hyphens:none" in block

def test_view_controls_get_full_width_header_row():
    final=C[C.index("V0.12.2.5 REAL VIEWPORT UX FIX"):]
    assert ".display-strip{" in final
    block=final[final.index(".display-strip{"):final.index(".display-strip-head{")]
    assert "grid-column:2/4" in block
    assert "grid-row:3" in block
    assert 'class="display-strip"' in H
    assert H.index('class="display-strip"') < H.index('class="nav-panel"')

def test_technical_details_are_drawer_not_footer_overlay():
    footer=H[H.index('<footer class="footerbar">'):H.index('</footer>')+9]
    assert 'id="devPanel"' not in footer
    assert 'class="tech-drawer"' in H
    assert 'id="devCloseBtn"' in H
    final=C[C.index("V0.12.2.5 REAL VIEWPORT UX FIX"):]
    assert ".tech-drawer{" in final and "position:fixed" in final

def test_technical_toggle_opens_drawer():
    assert "function setTechOpen(open)" in J
    assert "$('devToggle').onclick=()=>setTechOpen(true)" in J
    assert "$('devToggle').setAttribute('aria-expanded',String(open))" in J

def test_right_info_panel_is_compact_and_collapsible():
    assert H.count('class="panel-card')==1
    assert 'id="sideToggle"' in H
    assert 'id="sideCloseBtn"' in H
    assert "setSideVisible(" in J
    assert "v012-side-visible" in J
    assert "quote-card" not in H

def test_dashboard_geometry_is_compact():
    final=C[C.index("V0.12.2.5 REAL VIEWPORT UX FIX"):]
    assert ".simplified-dashboard .dash-card{" in final
    dash=J[J.index("function dash()"):J.index("async function memoView")]
    assert 'data-dashboard-card="memo"' in dash
    assert 'data-dashboard-card="safety"' in dash
    assert "min-height:96px" in final

def test_viewport_breakpoints_are_explicit():
    final=C[C.index("V0.12.2.5 REAL VIEWPORT UX FIX"):]
    for width in ("1450px","1280px","1100px","900px","720px","460px"):
        assert f"@media(max-width:{width})" in final

def test_scrim_coordinates_all_drawers():
    assert "function updateScrim()" in J
    assert "navOpen" in J and "sideOverlay" in J and "techOpen" in J
    assert "scrim.onclick" in J

def test_xl_side_overlay_scrim_and_escape_close_contract():
    """XL/high-magnification uses an overlay even above 1280px; both close paths must honor it."""
    close_block=J[J.index("scrim.onclick"):J.index("function clamp")]
    xl_close=re.compile(
        r"if\s*\(\s*innerWidth\s*<\s*1280\s*\|\|\s*root\.dataset\.fontTier\s*===\s*'xl'\s*\)\s*setSideVisible\(false,false\)"
    )
    matches=xl_close.findall(close_block)
    assert len(matches)==2, "Scrim und Escape müssen den XL-Overlay-Info-Bereich auch oberhalb 1280px schließen"

def test_removed_sidebar_fields_are_guarded():
    assert "if($('integrity'))" in J
    assert "$('layoutMode').textContent" not in J

def test_xl_status_remains_single_row():
    final=C[C.index("V0.12.2.5 REAL VIEWPORT UX FIX"):]
    assert 'html[data-font-tier="xl"] .status-strip.simplified' in final
    assert 'grid-template-columns:repeat(3,minmax(0,1fr))' in final

def test_version_still_only_one_visible_location():
    ids=re.findall(r'id="([^"]*Version[^"]*)"',H)
    assert ids==["toolVersion"],ids

def test_mobile_keeps_menu_labels():
    final=C[C.index("V0.12.2.5 REAL VIEWPORT UX FIX"):]
    mobile=final[final.index("@media(max-width:720px)"):]
    assert ".nav-head b,.nav-label{display:block!important}" in mobile

if __name__=="__main__":
    tests=[v for k,v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    bad=[]
    for fn in tests:
        try:
            fn();print("PASS",fn.__name__)
        except Exception as e:
            bad.append((fn.__name__,repr(e)));print("FAIL",fn.__name__,repr(e))
    print(f"SUMMARY total={len(tests)} passed={len(tests)-len(bad)} failed={len(bad)}")
    raise SystemExit(1 if bad else 0)
