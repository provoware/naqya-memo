from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
H=(ROOT/"ui/reference_web/index.html").read_text(encoding="utf-8")
J=(ROOT/"ui/reference_web/app.js").read_text(encoding="utf-8")
C=(ROOT/"ui/reference_web/styles.css").read_text(encoding="utf-8")
S=(ROOT/"app/server.py").read_text(encoding="utf-8")

def test_no_stale_visible_version_literals():
    assert "0.8.0" not in H
    assert "<b>V0.12</b>" not in H
    assert "Service-Pfad</h3><strong>V0.12.2" not in J
    assert H.count('id="toolVersion"')==1
    assert 'id="buildVersion"' not in H and 'id="brandVersion"' not in H
    assert 'id="checkpointVersion"' not in H and 'id="devVersion"' not in H
    assert "setVersionUi(state.version)" in J

def test_truthful_status_contract():
    assert 'id="backupStatus"' in H
    assert "backup_status()" in S
    assert "'backup':backup_status()" in S
    assert "Recovery aktiv" not in H

def test_desktop_file_picker_primary():
    assert '📂 Datei auswählen' in J
    assert "/api/assets/upload?" in J
    assert "application/octet-stream" in J
    assert "Profi: lokalen Pfad manuell verwenden" in J
    assert "def _asset_upload(self):" in S

def test_voice_technical_details_collapsed():
    assert "<details class=\"tech-details\">" in J
    assert "Technische Details anzeigen" in J
    assert "Mikrofontest" in J

def test_zoom_and_quickbar_contract():
    assert "clamp(zoom+d,.8,2)" in J
    assert "zoomTier" in J
    assert ".quickbar{overflow-x:auto;overflow-y:hidden" in C
    assert 'data-zoom-tier="large"' in C


def test_mobile_build_info_matches_registry():
    import json,re
    version=json.loads((ROOT/"registry/VERSION.json").read_text(encoding="utf-8"))["version"]
    build=(ROOT/"ui/reference_web/build_info.js").read_text(encoding="utf-8")
    mobile=(ROOT/"ui/reference_web/mobile/mobile_core.js").read_text(encoding="utf-8")
    assert version in build
    assert "PROVOWARE_BUILD_INFO" in mobile
    assert "version:global.PROVOWARE_BUILD_INFO?.version" in mobile
    assert '<script src="build_info.js"></script>' in H

def test_server_version_comes_from_registry():
    assert "APP_VERSION = json.loads((ROOT/'registry'/'VERSION.json')" in S
    assert "'version':APP_VERSION" in S


def test_display_controls_moved_to_dashboard_top():
    assert 'class="display-strip"' in H
    assert H.index('class="display-strip"') < H.index('class="quickbar"')
    assert H.count('id="themeBtn"')==1
    assert H.count('id="fontDown"')==1 and H.count('id="fontUp"')==1
    assert H.count('id="zoomOut"')==1 and H.count('id="zoomIn"')==1 and H.count('id="zoomReset"')==1
    quick=H[H.index('class="quickbar"'):H.index('class="workspace"')]
    assert 'id="themeBtn"' not in quick and 'id="zoomOut"' not in quick

def test_input_contrast_contract():
    assert "--input-contrast:#b7c1cc" in C
    assert "--input-focus:#f4f7fb" in C
    assert "caret-color:var(--input-focus)" in C
    assert "border-color:var(--input-contrast)" in C
    assert "input::placeholder" in C

def test_navigation_size_contract():
    assert "--nav-desktop:102px" in C
    assert "min-height:49px" in C
    assert "@media(max-width:1250px)" in C
    assert "@media(max-width:1050px)" in C
    assert "@media(max-width:720px)" in C

def test_zoom_overflow_hardening_contract():
    assert ".module-host{overflow-y:auto;overflow-x:hidden}" in C
    assert 'data-zoom-tier="large"' in C and 'data-zoom-tier="xl"' in C
    assert ".month-grid{grid-template-columns:repeat(7,minmax(0,1fr))" in C
    assert "max-width:100%" in C
    assert "grid-template-columns:1fr" in C

def test_html_ids_are_unique():
    import re
    ids=re.findall(r'id="([^"]+)"',H)
    assert len(ids)==len(set(ids))

def test_theme_and_font_persist_through_settings():
    assert "themeOptions=[" in J
    assert "NEON_TUERKIS" in J and "HOCHKONTRAST" in J
    assert "await api('/api/settings','POST',{theme:opt.service})" in J
    assert "await api('/api/settings','POST',{font_scale:font})" in J
    mobile=(ROOT/"ui/reference_web/mobile/mobile_core.js").read_text(encoding="utf-8")
    assert "settings:await this.settings()" in mobile

if __name__=="__main__":
    ts=[v for k,v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    bad=[]
    for t in ts:
        try:t();print("PASS",t.__name__)
        except Exception as e:bad.append((t.__name__,repr(e)));print("FAIL",t.__name__,repr(e))
    print(f"SUMMARY total={len(ts)} passed={len(ts)-len(bad)} failed={len(bad)}")
    raise SystemExit(1 if bad else 0)
