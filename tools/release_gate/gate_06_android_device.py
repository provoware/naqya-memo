from pathlib import Path
import datetime,json,os,shutil,subprocess,time,re
ROOT=Path(__file__).resolve().parents[2]
E=ROOT/'registry/evidence/v0.12.2/gates/GATE_06_ANDROID_DEVICE.json';E.parent.mkdir(parents=True,exist_ok=True)
adb=shutil.which('adb'); apk_env=os.environ.get('PROVOWARE_ANDROID_ACCEPTANCE_APK') or os.environ.get('PROVOWARE_ANDROID_APK'); apk=Path(apk_env).expanduser() if apk_env else None; rel_env=os.environ.get('PROVOWARE_ANDROID_RELEASE_APK'); release_apk=Path(rel_env).expanduser() if rel_env else None
pkg='de.provoware.naqya'
out={'gate':'GATE_06_ANDROID_DEVICE','status':'BLOCKED','adb':adb,'acceptance_apk':str(apk) if apk else None,'release_apk':str(release_apk) if release_apk else None,'package':pkg,'runtime_source':'V0.12.2','timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat()}
def save(code=2):
 E.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False));raise SystemExit(code)
# An interrupted acceptance attempt must never leave an earlier device PASS usable.
out['reason']='Android acceptance attempt started; fresh device evidence pending.'
E.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
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
try:
 cp=subprocess.run([adb,'devices'],text=True,capture_output=True,timeout=8)
except (subprocess.TimeoutExpired,OSError) as exc:
 out['reason']=f'ADB device listing failed ({type(exc).__name__}); device acceptance cannot be verified.';save()
if cp.returncode!=0:
 out['reason']=f'ADB device listing failed (exit {cp.returncode}); device acceptance cannot be verified.';save()
dev=[l.split()[0] for l in cp.stdout.splitlines()[1:] if l.strip().endswith('\tdevice')]
out['devices']=dev
if len(dev)!=1:out['reason']='Exactly one authorized Android device is required.';save()
serial=dev[0]
def cmd(args,timeout=30):
 try:
  return subprocess.run([adb,'-s',serial,*args],text=True,capture_output=True,timeout=timeout)
 except (subprocess.TimeoutExpired,OSError) as exc:
  # A failed ADB step cannot count as device acceptance; preserve a usable BLOCKED reason.
  out['failure_class']='TIMEOUT' if isinstance(exc,subprocess.TimeoutExpired) else 'COMMAND_ERROR'
  out['failed_step']=args[0]
  out['reason']=f'ADB {args[0]} failed ({type(exc).__name__}); device acceptance cannot be verified.'
  save()
out['serial']=serial;out['model']=cmd(['shell','getprop','ro.product.model']).stdout.strip()
sdk_result=cmd(['shell','getprop','ro.build.version.sdk'])
sdk=sdk_result.stdout.strip();out['sdk']=sdk
# An unknown SDK version must not bypass Android 13+ notification permission checks.
if sdk_result.returncode!=0 or not sdk.isdecimal() or int(sdk)<=0:
 out['failure_class']='INVALID_DEVICE_METADATA'
 out['failed_step']='shell getprop ro.build.version.sdk'
 out['reason']='Android SDK version could not be verified; required permissions are unknown.'
 save()
ins=cmd(['install','-r',str(apk)],60);out['install_output']=(ins.stdout+ins.stderr)[-2000:]
# ADB can return success exit status with a failure message; do not reuse an older installed APK.
if ins.returncode!=0 or ins.stdout.strip().splitlines()[-1:]!=['Success']:
 out['failure_class']='ACCEPTANCE_APK_INSTALL_FAILED'
 out['failed_step']='install -r'
 out['reason']='Debug acceptance APK installation was not confirmed by ADB Success.'
 save()
# Clean application data, then grant only permissions explicitly required by the acceptance run.
cleared=cmd(['shell','pm','clear',pkg])
# A previous app session must not supply data for this fresh acceptance attempt.
if cleared.returncode!=0 or cleared.stdout.strip()!='Success':
 out['reason']='Android app data could not be cleared; previous data must not count as fresh acceptance.';save()
rec=cmd(['shell','pm','grant',pkg,'android.permission.RECORD_AUDIO']);notif=None
if int(sdk)>=33:notif=cmd(['shell','pm','grant',pkg,'android.permission.POST_NOTIFICATIONS'])
out['record_audio_grant_rc']=rec.returncode;out['notification_grant_rc']=None if notif is None else notif.returncode
if rec.returncode!=0 or (notif is not None and notif.returncode!=0):out['reason']='Required runtime permissions could not be granted for acceptance.';save()
acceptance_info_result=cmd(['shell','dumpsys','package',pkg])
# Partial stdout from a failed ADB query must not certify the debug acceptance APK.
if acceptance_info_result.returncode!=0:
 out['failure_class']='ACCEPTANCE_METADATA_QUERY_FAILED'
 out['failed_step']='shell dumpsys package'
 out['reason']='Debug acceptance package metadata could not be verified.'
 save()
info=acceptance_info_result.stdout
vm=re.search(r'versionName=([^\s]+)',info);out['version_name']=vm.group(1) if vm else None
if out['version_name']!='0.12.2':out['reason']='Installed APK is not V0.12.2.';save()
# Real run: persistent data, real microphone, real AlarmManager/Receiver notification path.
run_log_clear=cmd(['logcat','-c'])
if run_log_clear.returncode!=0:
 out['reason']='Android logcat could not be cleared before acceptance; stale logs must not count as proof.';save()
launch=cmd(['shell','am','start','-W','-n',f'{pkg}/.MainActivity','--es','provoware_acceptance','run']);out['run_launch_output']=(launch.stdout+launch.stderr)[-1500:]
time.sleep(8)
run_log_result=cmd(['logcat','-d','-s','ProvowareAcceptance:I','*:S'])
logs=run_log_result.stdout
out['run_log_tail']=logs[-6000:]
# Even a partial logcat failure may contain plausible but unverified PASS lines.
if run_log_result.returncode!=0:
 out['failure_class']='LOGCAT_READ_FAILED'
 out['failed_step']='logcat -d run'
 out['reason']='Android logcat read failed during initial acceptance; output cannot prove a fresh PASS.'
 save()
run_result=parse_acceptance(logs,'run');out['run_result']=run_result;out['reminder_fired']='REMINDER_FIRED:' in logs
if launch.returncode!=0 or not run_result or run_result.get('status')!='PASS' or not out['reminder_fired']:
 out['reason']='Native run did not prove microphone + reminder + mobile core acceptance.';save()
# Process restart must retain IndexedDB data and audio metadata.
stopped=cmd(['shell','am','force-stop',pkg])
if stopped.returncode!=0:
 out['reason']='Android app could not be force-stopped; persistence after restart cannot be verified.';save()
verify_log_clear=cmd(['logcat','-c'])
if verify_log_clear.returncode!=0:
 out['reason']='Android logcat could not be cleared before persistence verification; stale logs must not count as proof.';save()
time.sleep(.5)
verify_launch=cmd(['shell','am','start','-W','-n',f'{pkg}/.MainActivity','--es','provoware_acceptance','verify']);out['verify_launch_output']=(verify_launch.stdout+verify_launch.stderr)[-1500:]
time.sleep(5)
verify_log_result=cmd(['logcat','-d','-s','ProvowareAcceptance:I','*:S'])
verify_logs=verify_log_result.stdout
out['verify_log_tail']=verify_logs[-5000:]
if verify_log_result.returncode!=0:
 out['failure_class']='LOGCAT_READ_FAILED'
 out['failed_step']='logcat -d verify'
 out['reason']='Android logcat read failed during persistence verification; output cannot prove a fresh PASS.'
 save()
verify=parse_acceptance(verify_logs,'verify');out['verify_result']=verify
if not (verify_launch.returncode==0 and verify and verify.get('status')=='PASS'):
 out['reason']='Initial Android run passed, but persistence verification after process restart failed.';save()
# Acceptance hooks are deliberately disabled in non-debuggable release. Uninstall debug APK, then prove signed release installs and launches normally.
uninstalled=cmd(['uninstall',pkg],60)
# A failed debug removal must never be mistaken for a clean signed-release install.
if uninstalled.returncode!=0 or uninstalled.stdout.strip()!='Success':
 out['failure_class']='DEBUG_APK_UNINSTALL_FAILED'
 out['failed_step']='uninstall'
 out['reason']='Debug acceptance APK could not be removed; signed release verification must not run.'
 save()
rel=cmd(['install','-r',str(release_apk)],60);out['release_install_output']=(rel.stdout+rel.stderr)[-2000:]
# A failed release install must not be certified by a previously installed package.
if rel.returncode!=0 or rel.stdout.strip().splitlines()[-1:]!=['Success']:
 out['failure_class']='RELEASE_APK_INSTALL_FAILED'
 out['failed_step']='install -r'
 out['reason']='Signed release APK installation was not confirmed by ADB Success.'
 save()
release_info_result=cmd(['shell','dumpsys','package',pkg])
# A failed metadata query must not certify the signed release using partial stdout.
if release_info_result.returncode!=0:
 out['failure_class']='RELEASE_METADATA_QUERY_FAILED'
 out['failed_step']='shell dumpsys package'
 out['reason']='Signed release package metadata could not be verified.'
 save()
release_info=release_info_result.stdout;rv=re.search(r'versionName=([^\s]+)',release_info);out['release_version_name']=rv.group(1) if rv else None
normal=cmd(['shell','am','start','-W','-n',f'{pkg}/.MainActivity']);out['release_launch_output']=(normal.stdout+normal.stderr)[-1600:]
time.sleep(2);pid_result=cmd(['shell','pidof',pkg]);pid=pid_result.stdout.strip()
# A failed process query cannot prove the signed release is running.
if pid_result.returncode!=0:
 out['failure_class']='RELEASE_PROCESS_QUERY_FAILED'
 out['failed_step']='shell pidof'
 out['reason']='Signed release process could not be verified.'
 save()
out['release_pid']=pid
if rel.returncode==0 and normal.returncode==0 and pid and out['release_version_name']=='0.12.2':
 out['status']='PASS';out['reason']='Android gate passed: debug-only device acceptance proved microphone/reminder/persistence; signed non-debuggable V0.12.2 release APK then installed and launched.';save(0)
out['reason']='Acceptance run passed, but normal release APK launch/version verification failed.';save()
