from pathlib import Path
import datetime,json,shutil,subprocess
ROOT=Path(__file__).resolve().parents[2];E=ROOT/'registry/evidence/v0.12.2/gates/GATE_03_FIREFOX.json'
# Invalidate any previous PASS before checking browser availability or launching it.
# A cancelled version probe is not a new Firefox end-to-end acceptance.
E.parent.mkdir(parents=True,exist_ok=True)
out={'gate':'GATE_03_FIREFOX','status':'BLOCKED','executable':None,'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reason':'New Firefox check started; real browser E2E still required.'}
E.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
exe=shutil.which('firefox');out['executable']=exe
if not exe: out['reason']='Firefox executable is not installed in this runner.'
else:
 try:
  cp=subprocess.run([exe,'--version'],text=True,capture_output=True,timeout=5);out['version']=(cp.stdout+cp.stderr).strip();out['reason']='Firefox executable detected; full app E2E still required by gate harness on a browser-capable runner.'
 except Exception as e: out['reason']=repr(e)
E.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False));raise SystemExit(2)
