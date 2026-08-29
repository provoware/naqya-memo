from pathlib import Path
import datetime,json
ROOT=Path(__file__).resolve().parents[2];GD=ROOT/'registry/evidence/v0.12.2/gates';OUT=ROOT/'registry/evidence/v0.12.2/RELEASE_GATE_CLOSURE.json'
gates=[('01','8H_SOAK'),('02','CHROMIUM'),('03','FIREFOX'),('04','LINUX_MICROPHONE'),('05','STORAGE_FAILURE'),('06','ANDROID_DEVICE'),('07','IOS_IPHONE_X')]
items=[]
for no,name in gates:
 matches=sorted(GD.glob(f'GATE_{no}_*.json'))
 if not matches:items.append({'gate':f'GATE_{no}_{name}','status':'NOT_RUN'});continue
 try:d=json.loads(matches[-1].read_text(encoding='utf-8'))
 except Exception as e:d={'gate':f'GATE_{no}_{name}','status':'INVALID_EVIDENCE','error':repr(e)}
 items.append(d)
pass_count=sum(x.get('status')=='PASS' for x in items);all_pass=pass_count==7
source_evidence=ROOT/'registry/evidence/v0.12.2/MOBILE_RUNTIME_SOURCE_ACCEPTANCE.json'
mobile_source=json.loads(source_evidence.read_text(encoding='utf-8')) if source_evidence.exists() else {'status':'NOT_RUN'}
source_pass=mobile_source.get('status')=='PASS'
out={'version':'0.12.2-MOBILE-RUNTIME-COMPLETION','generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'feature_freeze':True,'freeze_exception':'platform parity completion only','mobile_runtime_source_status':mobile_source.get('status'),'required_real_gates':7,'passed_real_gates':pass_count,'all_required_real_gates_pass':all_pass,'release_status':'GO' if all_pass and source_pass else 'NO-GO','v1_rc_allowed':bool(all_pass and source_pass),'gates':items}
OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print(json.dumps(out,indent=2,ensure_ascii=False));raise SystemExit(0 if out['v1_rc_allowed'] else 2)
