from pathlib import Path
import datetime,json,shutil,subprocess
ROOT=Path(__file__).resolve().parents[2];E=ROOT/'registry/evidence/v0.12.2/gates/GATE_03_FIREFOX.json'
exe=shutil.which('firefox');out={'gate':'GATE_03_FIREFOX','status':'BLOCKED','executable':exe,'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat()}
if not exe: out['reason']='Firefox executable is not installed in this runner.'
else:
 try:
  cp=subprocess.run([exe,'--version'],text=True,capture_output=True,timeout=5);out['version']=(cp.stdout+cp.stderr).strip();out['reason']='Firefox executable detected; full app E2E still required by gate harness on a browser-capable runner.'
 except Exception as e: out['reason']=repr(e)
E.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False));raise SystemExit(2)
