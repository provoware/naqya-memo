from pathlib import Path
import datetime,errno,json,os,tempfile
ROOT=Path(__file__).resolve().parents[2];E=ROOT/'registry/evidence/v0.12.2/gates/GATE_05_STORAGE_FAILURE.json'
out={'gate':'GATE_05_STORAGE_FAILURE','status':'FAIL','timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tests':{}}
# Linux /dev/full is a kernel device that always returns ENOSPC on write.
try:
 with open('/dev/full','wb',buffering=0) as f:f.write(b'provoware-storage-failure')
 out['tests']['dev_full']={'status':'FAIL','reason':'write unexpectedly succeeded'}
except OSError as e:
 out['tests']['dev_full']={'status':'PASS' if e.errno==errno.ENOSPC else 'FAIL','errno':e.errno,'message':str(e)}
# /sys is mounted read-only in this runner. This is a real OS storage permission/mount failure.
try:
 Path('/sys/provoware_rc_write_probe').write_text('x')
 out['tests']['read_only_mount']={'status':'FAIL','reason':'write unexpectedly succeeded'}
except OSError as e:
 out['tests']['read_only_mount']={'status':'PASS' if e.errno in (errno.EROFS,errno.EACCES,errno.EPERM) else 'FAIL','errno':e.errno,'message':str(e)}
# Existing application-level deterministic recovery matrix is part of the combined gate.
prev=ROOT/'registry/evidence/v0.12/FAILURE_MATRIX_RESULTS.json'
app_ok=False
if prev.exists():
 data=json.loads(prev.read_text(encoding='utf-8'))
 app_ok=(data.get('disk_full_deterministic_injection')=='PASS' and data.get('permission_denied_deterministic_injection')=='PASS' and str(data.get('read_only_preflight','')).startswith('PASS'))
out['application_failure_matrix_evidence_present']=prev.exists()
out['application_failure_matrix_pass']=app_ok
out['status']='PASS' if all(x.get('status')=='PASS' for x in out['tests'].values()) and app_ok else 'FAIL'
out['scope']='REAL_LINUX_KERNEL_STORAGE_SIGNALS + V0.12_APPLICATION_RECOVERY_MATRIX'
E.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False));raise SystemExit(0 if out['status']=='PASS' else 1)
