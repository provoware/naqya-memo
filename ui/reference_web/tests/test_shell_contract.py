from pathlib import Path
import json,re,sys
ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/'index.html').read_text(encoding='utf-8'); css=(ROOT/'styles.css').read_text(encoding='utf-8'); js=(ROOT/'app.js').read_text(encoding='utf-8'); tokens=json.loads((ROOT/'theme_tokens.json').read_text())

def lum(h):
 h=h.lstrip('#'); rgb=[int(h[i:i+2],16)/255 for i in (0,2,4)]; vals=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in rgb]; return .2126*vals[0]+.7152*vals[1]+.0722*vals[2]
def ratio(a,b):
 l1,l2=lum(a),lum(b); return (max(l1,l2)+.05)/(min(l1,l2)+.05)

def test_required_regions():
 for token in ['topbar','mainNav','quickbar','workspace','footerbar','side-panel']:
  assert token in html

def test_four_themes(): assert len(tokens['themes'])==4

def test_text_contrast():
 for name,t in tokens['themes'].items():
  assert ratio(t['text'],t['bg'])>=7, (name,'text/bg',ratio(t['text'],t['bg']))
  assert ratio(t['text'],t['surface'])>=4.5, (name,'text/surface',ratio(t['text'],t['surface']))

def test_responsive_breakpoints():
 assert '@media (max-width:1050px)' in css and '@media (max-width:720px)' in css and '@media (max-width:380px)' in css

def test_mobile_drawer(): assert "classList.toggle('open'" in js and 'aria-expanded' in html

def test_font_scale_range(): assert tokens['font_scale_range']==[0.8,2.0]

def test_area_zoom_range(): assert tokens['area_zoom_range']==[0.8,1.5]

def test_no_domain_imports():
 forbidden=['CoreStore','MemoService','TodoService','CalendarService','sqlite3']
 for x in forbidden: assert x not in js and x not in html

def test_disabled_quick_note_write(): assert 'type="button" disabled' in html

def test_accessibility_basics():
 assert 'skip-link' in html and 'focus-visible' in css and 'prefers-reduced-motion' in css and 'aria-label' in html

if __name__=='__main__':
 tests=[v for k,v in sorted(globals().items()) if k.startswith('test_') and callable(v)]; fail=[]
 for t in tests:
  try:t();print('PASS',t.__name__)
  except Exception as e:fail.append((t.__name__,repr(e)));print('FAIL',t.__name__,repr(e))
 print(f'SUMMARY total={len(tests)} passed={len(tests)-len(fail)} failed={len(fail)}')
 sys.exit(1 if fail else 0)
