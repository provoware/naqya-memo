from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
R=(ROOT/'ui/reference_web/read_only_ui.js').read_text(encoding='utf-8')
C=(ROOT/'ui/reference_web/read_only_ui.css').read_text(encoding='utf-8')
M=(ROOT/'ui/reference_web/mutation_status_ui.js').read_text(encoding='utf-8')
E=(ROOT/'ui/reference_web/error_status_ui.js').read_text(encoding='utf-8')
APP=(ROOT/'ui/reference_web/app.js').read_text(encoding='utf-8')
STYLES=(ROOT/'ui/reference_web/styles.css').read_text(encoding='utf-8')

def test_degraded_mode_event_bridge_and_runtime_import():
    assert "provoware:mutation-mode" in E
    assert "new CustomEvent('provoware:mutation-mode'" in E
    assert "import('./read_only_ui.js')" in E
    assert "payload?.data?.mutation_mode==='DEGRADED'" in E
    assert "setMutationUi(degraded)" in E

def test_all_known_mutation_controls_lock_but_navigation_is_not_selected():
    for token in (
        "form button[type=\"submit\"]","#quickSave","#quickOpen","#quickShare",
        "#undoBtn","#redoBtn","#themeBtn","#fontDown","#fontUp",
        "#recordStart","#recordStop","#diagCreate","#docSave",
        "[data-trash-memo]","[data-trash-todo]","[data-trash-event]",
        "[data-restore]","[data-complete-todo]","[data-day]"
    ):
        assert token in R
    assert ".nav-item" not in R
    assert "[data-view-doc]" not in R
    assert "[data-edit-memo]" not in R
    assert "#zoomIn" not in R and "#zoomOut" not in R and "#zoomReset" not in R

def test_accessible_visible_lock_and_reason():
    assert "aria-disabled" in R
    assert "Nur-Lese-Modus:" in R
    assert "readOnlyToolbarHint" in R
    assert "role','status'" in R
    assert "aria-live','polite'" in R
    assert "focusSafetyNotice" in R
    assert "[data-readonly-locked=\"1\"]" in C
    assert ":focus-visible" in C
    assert "overflow-wrap:anywhere" in C

def test_dynamic_views_and_restart_restore():
    assert "new MutationObserver" in R
    assert "record.addedNodes" in R
    assert "const originalState=new WeakMap()" in R
    assert "control.disabled=Boolean(original.disabled)" in R
    assert "delete control.dataset.readonlyLocked" in R
    assert "originalState.delete(control)" in R
    assert "setMode(Boolean(event.detail?.degraded" in R

def test_client_transport_fail_closed_for_post_only():
    assert "meta.method!=='POST'" in M
    assert "if(mutationLocked())return blockedMutation(meta)" in M
    assert "document.documentElement?.dataset?.mutationMode==='degraded'" in M
    assert "MUTATION_DEGRADED_MODE" in M
    assert "'x-provoware-client-block':'read-only'" in M
    assert "provoware:api-error" in M

def test_degraded_toast_cannot_downgrade_global_status():
    assert "document.documentElement.dataset.mutationMode==='degraded'" in E
    assert "code:'MUTATION_DEGRADED_MODE'" in E
    assert "degraded_mode:true" in E

def test_isolation_from_product_logic_and_dashboard():
    assert "read_only_ui" not in APP
    assert "read-only-toolbar-hint" not in STYLES
    assert "mutationLocked" not in APP

def test_zoom_and_reduced_motion_contract():
    assert 'html[data-font-tier="xl"] .read-only-toolbar-hint' in C
    assert '@media(max-width:720px)' in C
    assert '@media(prefers-reduced-motion:reduce)' in C

def main():
    tests=[v for k,v in globals().items() if k.startswith('test_') and callable(v)]
    failures=[]
    for test in tests:
        try:test();print('PASS',test.__name__)
        except Exception as exc:failures.append((test.__name__,exc));print('FAIL',test.__name__,exc)
    print(f'SUMMARY total={len(tests)} passed={len(tests)-len(failures)} failed={len(failures)}')
    if failures:raise SystemExit(1)
if __name__=='__main__':main()
