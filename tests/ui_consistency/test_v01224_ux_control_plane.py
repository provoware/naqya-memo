
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[2]
H=(ROOT/"ui/reference_web/index.html").read_text(encoding="utf-8")
J=(ROOT/"ui/reference_web/app.js").read_text(encoding="utf-8")
C=(ROOT/"ui/reference_web/styles.css").read_text(encoding="utf-8")

def test_nav_has_separate_icons_labels_and_aria_current():
    assert H.count('class="nav-icon"') >= 12
    assert H.count('class="nav-label"') >= 12
    assert 'aria-current="page"' in H
    assert "setAttribute('aria-current','page')" in J

def test_workspace_has_context_specific_guidance():
    assert "const VIEW_META=" in J
    for key in ("dashboard","memo","todo","calendar","diagnostics","voice","docs","settings","help"):
        assert re.search(rf"\b{key}:\{{title:",J)
    assert "updateWorkspaceMeta(view)" in J

def test_help_hints_are_contextual():
    assert "applyHelpModeUi" in J
    assert 'root.dataset.helpMode' in J
    assert 'html[data-help-mode="1"] label:focus-within>.field-hint' in C
    assert 'html[data-help-mode="2"] .field-hint' in C
    assert 'html[data-help-mode="3"] .field-hint' in C

def test_footer_complexity_reduced():
    assert '<b>SYSTEM</b>' in H
    visible_footer=H[H.index('<footer class="footerbar">'):H.index('</footer>')+9]
    assert '<b>LOG</b>' not in visible_footer
    assert 'id="logState"' not in visible_footer and 'id="debugState"' not in visible_footer
    assert 'id="devPanel"' in H and 'Technische Details' in H
    assert 'id="logState"' in H and 'id="debugState"' in H

def test_accessibility_and_motion_contract():
    assert "--touch:44px" in C
    assert "@media(prefers-reduced-motion:reduce)" in C
    assert "button:focus-visible" in C
    assert ".workspace-toolbar{" in C and "position:sticky" in C

def test_repo_control_plane_present():
    for rel in (
        ".gitignore",".gitattributes",".editorconfig",
        ".github/workflows/quality.yml","CONTRIBUTING.md","LAIENANLEITUNG.md",
        "docs/history/GITHUB_MAIN_0.5.1_E7_PRESERVATION.md",
    ):
        assert (ROOT/rel).exists(), rel

def test_workflow_does_not_fake_real_release_gates():
    w=(ROOT/".github/workflows/quality.yml").read_text(encoding="utf-8")
    assert "source contracts only" in w
    assert "does NOT turn real device/browser/microphone release gates green" in w
    assert "gate_06_android_device.py" not in w
    assert "gate_07_ios_iphone_x.py" not in w

def test_no_duplicate_settings_form_binding():
    assert J.count("const sf=$('settingsForm')")==1

def test_version_remains_single_visible_location():
    ids=re.findall(r'id="([^"]*Version[^"]*)"',H)
    assert ids==["toolVersion"],ids

if __name__=="__main__":
    tests=[v for k,v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    bad=[]
    for t in tests:
        try:
            t();print("PASS",t.__name__)
        except Exception as e:
            bad.append((t.__name__,repr(e)));print("FAIL",t.__name__,repr(e))
    print(f"SUMMARY total={len(tests)} passed={len(tests)-len(bad)} failed={len(bad)}")
    raise SystemExit(1 if bad else 0)
