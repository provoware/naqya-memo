from pathlib import Path
import datetime,json,os,shutil,subprocess,time,re
ROOT=Path(__file__).resolve().parents[2]
E=ROOT/'registry/evidence/v0.12.2/gates/GATE_06_ANDROID_DEVICE.json';E.parent.mkdir(parents=True,exist_ok=True)
adb=shutil.which('adb'); apk_env=os.environ.get('PROVOWARE_ANDROID_ACCEPTANCE_APK') or os.environ.get('PROVOWARE_ANDROID_APK'); apk=Path(apk_env).expanduser() if apk_env else None; rel_env=os.environ.get('PROVOWARE_ANDROID_RELEASE_APK'); release_apk=Path(rel_env).expanduser() if rel_env else None
pkg='de.provoware.naqya'
out={'gate':'GATE_06_ANDROID_DEVICE','status':'BLOCKED','adb':adb,'acceptance_apk':str(apk) if apk else None,'release_apk':str(release_apk) if release_apk else None,'package':pkg,'runtime_source':'V0.12.2','timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat()}
def save(code=2):
 E.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False));raise SystemExit(code)
def parse_acceptance(logs,mode):
 found=[]
 for line in logs.splitlines():
  if 'ProvowareAcceptance' not in line or '{' not in line: continue
  raw=line[line.find('{'):]
  try:
   d=json.loads(raw)
   if d.get('mode')==mode:found.append(d)
  except Exception:pass
 return found[-1] if found else None
if not adb:
 out['reason']='ADB is not installed in this runner. Runtime source is complete, but native device evidence is impossible here.';save()
if not apk or not apk.is_file():
 out['reason']='No debuggable acceptance APK supplied. Set PROVOWARE_ANDROID_ACCEPTANCE_APK.';save()
if not release_apk or not release_apk.is_file():
 out['reason']='No signed release APK supplied. Set PROVOWARE_ANDROID_RELEASE_APK.';save()
cp=subprocess.run([adb,'devices'],text=True,capture_output=True,timeout=8)
dev=[l.split()[0] for l in cp.stdout.splitlines()[1:] if l.strip().endswith('\tdevice')]
out['devices']=dev
if len(dev)!=1:out['reason']='Exactly one authorized Android device is required.';save()
serial=dev[0]
def cmd(args,timeout=30):return subprocess.run([adb,'-s',serial,*args],text=True,capture_output=True,timeout=timeout)
out['serial']=serial;out['model']=cmd(['shell','getprop','ro.product.model']).stdout.strip();sdk=cmd(['shell','getprop','ro.build.version.sdk']).stdout.strip();out['sdk']=sdk
ins=cmd(['install','-r',str(apk)],60);out['install_output']=(ins.stdout+ins.stderr)[-2000:]
if ins.returncode!=0:out['reason']='APK install failed.';save()
# Clean application data, then grant only permissions explicitly required by the acceptance run.
cmd(['shell','pm','clear',pkg])
rec=cmd(['shell','pm','grant',pkg,'android.permission.RECORD_AUDIO']);notif=None
if int(sdk or 0)>=33:notif=cmd(['shell','pm','grant',pkg,'android.permission.POST_NOTIFICATIONS'])
out['record_audio_grant_rc']=rec.returncode;out['notification_grant_rc']=None if notif is None else notif.returncode
if rec.returncode!=0 or (notif is not None and notif.returncode!=0):out['reason']='Required runtime permissions could not be granted for acceptance.';save()
info=cmd(['shell','dumpsys','package',pkg]).stdout
vm=re.search(r'versionName=([^\s]+)',info);out['version_name']=vm.group(1) if vm else None
if out['version_name']!='0.12.2':out['reason']='Installed APK is not V0.12.2.';save()
# Real run: persistent data, real microphone, real AlarmManager/Receiver notification path.
cmd(['logcat','-c'])
launch=cmd(['shell','am','start','-W','-n',f'{pkg}/.MainActivity','--es','provoware_acceptance','run']);out['run_launch_output']=(launch.stdout+launch.stderr)[-1500:]
time.sleep(8)
logs=cmd(['logcat','-d','-s','ProvowareAcceptance:I','*:S']).stdout
out['run_log_tail']=logs[-6000:]
run_result=parse_acceptance(logs,'run');out['run_result']=run_result;out['reminder_fired']='REMINDER_FIRED:' in logs
if launch.returncode!=0 or not run_result or run_result.get('status')!='PASS' or not out['reminder_fired']:
 out['reason']='Native run did not prove microphone + reminder + mobile core acceptance.';save()
# Process restart must retain IndexedDB data and audio metadata.
cmd(['shell','am','force-stop',pkg]);cmd(['logcat','-c']);time.sleep(.5)
verify_launch=cmd(['shell','am','start','-W','-n',f'{pkg}/.MainActivity','--es','provoware_acceptance','verify']);out['verify_launch_output']=(verify_launch.stdout+verify_launch.stderr)[-1500:]
time.sleep(5)
verify_logs=cmd(['logcat','-d','-s','ProvowareAcceptance:I','*:S']).stdout
out['verify_log_tail']=verify_logs[-5000:];verify=parse_acceptance(verify_logs,'verify');out['verify_result']=verify
if not (verify_launch.returncode==0 and verify and verify.get('status')=='PASS'):
 out['reason']='Initial Android run passed, but persistence verification after process restart failed.';save()
# Acceptance hooks are deliberately disabled in non-debuggable release. Uninstall debug APK, then prove signed release installs and launches normally.
cmd(['uninstall',pkg],60)
rel=cmd(['install','-r',str(release_apk)],60);out['release_install_output']=(rel.stdout+rel.stderr)[-2000:]
if rel.returncode!=0:out['reason']='Acceptance APK passed, but signed release APK install failed.';save()
release_info=cmd(['shell','dumpsys','package',pkg]).stdout;rv=re.search(r'versionName=([^\s]+)',release_info);out['release_version_name']=rv.group(1) if rv else None
normal=cmd(['shell','am','start','-W','-n',f'{pkg}/.MainActivity']);out['release_launch_output']=(normal.stdout+normal.stderr)[-1600:]
time.sleep(2);pid=cmd(['shell','pidof',pkg]).stdout.strip();out['release_pid']=pid
if rel.returncode==0 and normal.returncode==0 and pid and out['release_version_name']=='0.12.2':
 out['status']='PASS';out['reason']='Android gate passed: debug-only device acceptance proved microphone/reminder/persistence; signed non-debuggable V0.12.2 release APK then installed and launched.';save(0)
out['reason']='Acceptance run passed, but normal release APK launch/version verification failed.';save()
