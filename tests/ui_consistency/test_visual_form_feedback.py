from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
J=(ROOT/'ui/reference_web/form_feedback_ui.js').read_text(encoding='utf-8')
C=(ROOT/'ui/reference_web/form_feedback_ui.css').read_text(encoding='utf-8')
E=(ROOT/'ui/reference_web/error_status_ui.js').read_text(encoding='utf-8')
APP=(ROOT/'ui/reference_web/app.js').read_text(encoding='utf-8')
STYLES=(ROOT/'ui/reference_web/styles.css').read_text(encoding='utf-8')

def test_structured_event_bridge_and_isolation():
    assert "provoware:api-error" in E and "new CustomEvent" in E
    assert "requestMeta?.path" in E and "requestMeta?.method" in E
    assert "import('./form_feedback_ui.js')" in E
    assert "window.addEventListener('provoware:api-error'" in J
    assert "toast(e.message,true)" in APP

def test_native_required_and_format_feedback():
    assert "document.addEventListener('invalid'" in J
    assert "event.preventDefault()" in J
    assert "field.validity?.valueMissing" in J
    assert "field.validity?.typeMismatch" in J
    assert "field.validity?.patternMismatch" in J
    assert "aria-invalid" in J and "aria-describedby" in J
    assert "CLIENT_VALIDATION" in J

def test_server_code_to_field_mapping_and_focus():
    for code in (
        'MEMO_TITLE_REQUIRED','TODO_TITLE_REQUIRED','EVENT_TITLE_REQUIRED','TITLE_TOO_LONG',
        'REMINDER_REQUIRES_DUE_DATE','EVENT_END_BEFORE_START','DATETIME_REQUIRED',
        'INVALID_DATETIME','COLOR_TITLE_REQUIRED','UPLOAD_FILENAME_REQUIRED'
    ):
        assert code in J
    assert "focus({preventScroll:true})" in J
    assert "scrollIntoView({block:'center',behavior:'auto'})" in J

def test_conflict_is_form_level_not_fake_field_error():
    assert "REVISION_CONFLICT" in J and "ASSET_REVISION_CONFLICT" in J
    assert "showFormSummary" in J
    assert "Inhalt inzwischen geändert" in J
    assert "className=SUMMARY_CLASS" in J
    assert "summary.tabIndex=-1" in J

def test_error_clears_after_correction():
    assert "document.addEventListener('input'" in J
    assert "document.addEventListener('change'" in J
    assert "field.validity?.valid" in J
    assert "clearField(field)" in J

def test_accessibility_zoom_and_visual_contract():
    assert '.form-grid [aria-invalid="true"]' in C
    assert ':focus-visible' in C
    assert 'overflow-wrap:anywhere' in C
    assert 'html[data-font-tier="xl"] .form-field-error' in C
    assert '@media(max-width:720px)' in C
    assert '@media(prefers-reduced-motion:reduce)' in C
    assert STYLES.count('.form-field-error') == 0

def main():
    tests=[v for k,v in globals().items() if k.startswith('test_') and callable(v)]
    failures=[]
    for test in tests:
        try:test();print('PASS',test.__name__)
        except Exception as exc:failures.append((test.__name__,exc));print('FAIL',test.__name__,exc)
    print(f'SUMMARY total={len(tests)} passed={len(tests)-len(failures)} failed={len(failures)}')
    if failures:raise SystemExit(1)
if __name__=='__main__':main()
