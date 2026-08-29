from pathlib import Path
import datetime,json,os,platform,shutil,subprocess,time,re
ROOT=Path(__file__).resolve().parents[2]
E=ROOT/'registry/evidence/v0.12.2/gates/GATE_07_IOS_IPHONE_X.json';E.parent.mkdir(parents=True,exist_ok=True)
xcrun=shutil.which('xcrun');xcodebuild=shutil.which('xcodebuild');app_env=os.environ.get('PROVOWARE_IOS_APP');app=Path(app_env).expanduser() if app_env else None
udid=os.environ.get('PROVOWARE_IOS_DEVICE_ID');required=os.environ.get('PROVOWARE_IOS_REQUIRED_VERSION','16.7.16');bundle='de.provoware.naqya'
out={'gate':'GATE_07_IOS_IPHONE_X','status':'BLOCKED','host_platform':platform.system(),'xcrun':xcrun,'xcodebuild':xcodebuild,'app_bundle':str(app) if app else None,'device_id':udid,'target':f'iPhone X / iOS {required}','runtime_source':'V0.12.2','timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat()}
def save(code=2):
 E.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False));raise SystemExit(code)
def run(args,timeout=30):return subprocess.run(args,text=True,capture_output=True,timeout=timeout)
def parse_acceptance(text,mode):
 for line in reversed(text.splitlines()):
  if 'ProvowareAcceptance' not in line or '{' not in line:continue
  raw=line[line.find('{'):]
  try:
   d=json.loads(raw)
   if d.get('mode')==mode:return d
  except Exception:pass
 return None
def launch_console(mode,seconds):
 args=[xcrun,'devicectl','device','process','launch','--device',udid,'--console',bundle,'--','-ProvowareAcceptance',mode]
 p=subprocess.Popen(args,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 try:
  text,_=p.communicate(timeout=seconds)
 except subprocess.TimeoutExpired:
  p.terminate()
  try:text,_=p.communicate(timeout=3)
  except subprocess.TimeoutExpired:p.kill();text,_=p.communicate()
 return p.returncode,text
if platform.system()!='Darwin':out['reason']='Native iOS build/sign/install requires macOS/Xcode; current runner is not macOS.';save()
if not xcrun or not xcodebuild:out['reason']='Xcode command line tools missing.';save()
if not app or not app.is_dir():out['reason']='V0.12.2 Xcode runtime source exists, but no signed .app supplied. Set PROVOWARE_IOS_APP.';save()
if not udid:out['reason']='Set PROVOWARE_IOS_DEVICE_ID to the physical iPhone X UDID.';save()
# Strong target identity check from Xcode device listing.
listing=run([xcrun,'xctrace','list','devices'],20);out['device_list_tail']=(listing.stdout+listing.stderr)[-6000:]
line=next((l for l in (listing.stdout+listing.stderr).splitlines() if udid in l),None);out['matched_device_line']=line
if not line or 'iPhone X' not in line:out['reason']='Selected physical device is not reported as iPhone X.';save()
if required not in line:out['reason']=f'iPhone X found, but required iOS {required} is not reported.';save()
install=run([xcrun,'devicectl','device','install','app','--device',udid,str(app)],90);out['install_output']=(install.stdout+install.stderr)[-5000:]
if install.returncode!=0:out['reason']='Signed app installation failed.';save()
# User must approve microphone/notification prompts if the device has not granted them before.
rc,text=launch_console('run',18);out['run_console_tail']=text[-10000:];run_result=parse_acceptance(text,'run');out['run_result']=run_result;out['reminder_fired']='REMINDER_FIRED:' in text
if not run_result or run_result.get('status')!='PASS' or not out['reminder_fired']:
 out['reason']='iPhone acceptance did not prove native microphone + foreground reminder path. Approve system permission prompts and rerun.';save()
# Terminate app if supported, then verify WebKit/IndexedDB persistence across process lifecycle.
term=run([xcrun,'devicectl','device','process','terminate','--device',udid,'--bundle-id',bundle],20);out['terminate_output']=(term.stdout+term.stderr)[-2000:]
time.sleep(1)
rc2,text2=launch_console('verify',10);out['verify_console_tail']=text2[-8000:];verify=parse_acceptance(text2,'verify');out['verify_result']=verify
if verify and verify.get('status')=='PASS':
 out['status']='PASS';out['reason']='Real iPhone X/iOS device acceptance passed: install, native microphone, reminder callback, and persistence after relaunch.';save(0)
out['reason']='Initial iPhone run passed, but persistence verification after relaunch failed.';save()
