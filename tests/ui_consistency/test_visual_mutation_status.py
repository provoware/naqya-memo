from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
E=(ROOT/'ui/reference_web/error_status_ui.js').read_text(encoding='utf-8')
J=(ROOT/'ui/reference_web/mutation_status_ui.js').read_text(encoding='utf-8')
C=(ROOT/'ui/reference_web/mutation_status_ui.css').read_text(encoding='utf-8')
APP=(ROOT/'ui/reference_web/app.js').read_text(encoding='utf-8')

def test_runtime_activation_and_existing_app_isolation():
    assert "import('./mutation_status_ui.js')" in E
    assert "import('./form_feedback_ui.js')" in E
    assert "toast(e.message,true)" in APP
    assert "mutation_status_ui.css" in J and "document.head.appendChild(link)" in J

def test_only_local_post_mutations_are_wrapped():
    assert "url.origin!==location.origin" in J
    assert "!url.pathname.startsWith('/api/')" in J
    assert "if(!meta||meta.method!=='POST')return previousFetch" in J

def test_duplicate_identical_post_reuses_one_inflight_response():
    assert "const inFlight=new Map()" in J
    assert "const existing=inFlight.get(key)" in J
    assert "existing.snapshot.then(responseFromSnapshot)" in J
    assert "new Response(body" in J
    assert "inFlight.set(key,{source,snapshot})" in J

def test_busy_state_is_accessible_and_always_restored():
    assert "owner.setAttribute?.('aria-busy','true')" in J
    assert "trigger.setAttribute?.('aria-disabled','true')" in J
    assert "trigger.disabled=true" in J
    assert "return source.finally" in J
    assert "releaseBusy()" in J
    assert "trigger.disabled=original.disabled" in J
    assert "owner.removeAttribute?.('aria-busy')" in J

def test_human_busy_labels_cover_save_and_import():
    for text in (
        'Wird gespeichert …','Wird importiert …','Wird erstellt …',
        'Wird verschoben …','Wird wiederhergestellt …','Wird ausgeführt …'
    ):
        assert text in J

def test_binary_uploads_get_stable_duplicate_descriptor():
    assert "body instanceof Blob" in J
    assert "body.name||''" in J
    assert "body.size||0" in J
    assert "body.lastModified||0" in J
    assert "body.type||''" in J

def test_visual_and_reduced_motion_contract():
    assert 'button.mutation-busy' in C
    assert 'cursor:progress' in C
    assert 'form[aria-busy="true"]' in C
    assert '@media(prefers-reduced-motion:reduce)' in C
    assert '@keyframes provoware-mutation-spin' in C

def main():
    tests=[v for k,v in globals().items() if k.startswith('test_') and callable(v)]
    failures=[]
    for test in tests:
        try:test();print('PASS',test.__name__)
        except Exception as exc:failures.append((test.__name__,exc));print('FAIL',test.__name__,exc)
    print(f'SUMMARY total={len(tests)} passed={len(tests)-len(failures)} failed={len(failures)}')
    if failures:raise SystemExit(1)
if __name__=='__main__':main()
