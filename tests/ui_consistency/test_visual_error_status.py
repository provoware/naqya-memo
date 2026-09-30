from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
H=(ROOT/'ui/reference_web/index.html').read_text(encoding='utf-8')
J=(ROOT/'ui/reference_web/error_status_ui.js').read_text(encoding='utf-8')
C=(ROOT/'ui/reference_web/error_status_ui.css').read_text(encoding='utf-8')
APP=(ROOT/'ui/reference_web/app.js').read_text(encoding='utf-8')

def test_accessible_semantics_and_loading_order():
    assert 'id="statusNotice"' in H and 'role="alert"' in H
    assert 'aria-live="assertive"' in H and 'aria-atomic="true"' in H
    assert 'aria-labelledby="statusNoticeMessage"' in H
    assert 'aria-describedby="statusNoticeRecovery statusNoticeCode"' in H
    assert 'id="statusNoticeIcon" aria-hidden="true"' in H
    assert '<b>Lösung:</b>' in H and 'id="statusNoticeCode"' in H
    assert H.index('error_status_ui.js') < H.index('app.js')
    assert 'error_status_ui.css' in H

def test_structured_error_fields_survive_without_rewriting_app_logic():
    assert 'payload?.recovery_hint' in J and 'payload?.degraded_mode' in J
    assert 'response.clone()' in J and 'MutationObserver' in J
    assert "window.fetch=async function" in J
    assert "toast(e.message,true)" in APP  # existing app stays untouched; adapter consumes its error toast

def test_degraded_mode_is_textual_persistent_and_reload_safe():
    assert 'SICHERER NUR-LESE-MODUS' in J and "degraded?'⛔':'⚠'" in J
    assert "statusNoticeClose').hidden=degraded" in J
    assert "dataStatus.textContent='Nur Lesen'" in J
    assert "nativeFetch('/api/health'" in J and "mutation_mode==='DEGRADED'" in J
    assert 'MUTATION_DEGRADED_MODE' in J
    assert '.status-chip.degraded' in C and '.status-notice[data-level="degraded"]' in C

def test_error_is_not_color_only():
    assert 'AKTION NICHT ABGESCHLOSSEN' in J and 'Fehlercode:' in J
    assert '<b>Lösung:</b>' in H and 'status-notice-icon' in C

def test_keyboard_zoom_and_small_viewport_contract():
    assert '.status-notice-close:focus-visible' in C
    assert 'overflow-wrap:anywhere' in C and 'max-width:100%' in C
    assert 'html[data-font-tier="xl"] .status-notice' in C
    assert 'grid-template-columns:40px minmax(0,1fr)' in C
    assert '@media(max-width:720px)' in C and 'grid-template-columns:34px minmax(0,1fr)' in C

def main():
    tests=[v for k,v in globals().items() if k.startswith('test_') and callable(v)]
    failures=[]
    for test in tests:
        try:test();print('PASS',test.__name__)
        except Exception as exc:failures.append((test.__name__,exc));print('FAIL',test.__name__,exc)
    print(f'SUMMARY total={len(tests)} passed={len(tests)-len(failures)} failed={len(failures)}')
    if failures:raise SystemExit(1)
if __name__=='__main__':main()
