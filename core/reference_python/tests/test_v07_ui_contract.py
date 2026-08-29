from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
h=(ROOT/'ui/reference_web/index.html').read_text(encoding='utf-8');j=(ROOT/'ui/reference_web/app.js').read_text(encoding='utf-8');c=(ROOT/'ui/reference_web/styles.css').read_text(encoding='utf-8')
checks={
'api binding':'/api/state' in j and 'fetch(' in j,
'memo':'memoForm' in j and '/api/memos' in j,
'todo':'todoForm' in j and '/api/todos' in j,
'calendar':'eventForm' in j and '/api/events' in j,
'quick note':'quickSave' in h and '/api/quick-note' in j,
'undo redo':'undoBtn' in h and '/api/undo' in j and '/api/redo' in j,
'responsive':'@media(max-width:720px)' in c,
'accessibility':'skip-link' in h and 'aria-live' in h,
'no sqlite in UI':'sqlite3' not in j and 'CoreStore' not in j,
}
for k,v in checks.items():
    assert v,k;print('PASS',k)
print(f'SUMMARY total={len(checks)} passed={len(checks)} failed=0')
