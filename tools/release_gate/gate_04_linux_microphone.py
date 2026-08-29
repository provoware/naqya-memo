from pathlib import Path
import datetime,json,os,shutil,sys,tempfile,time
ROOT=Path(__file__).resolve().parents[2];E=ROOT/'registry/evidence/v0.12.2/gates/GATE_04_LINUX_MICROPHONE.json'
sys.path.insert(0,str(ROOT/'core/reference_python'))
from provoware_core.assets import AssetManager
from provoware_core.media import LinuxAudioRecorder, RecordingError
backend=os.environ.get('PROVOWARE_MIC_BACKEND','alsa' if Path('/dev/snd').exists() else 'pulse')
device=os.environ.get('PROVOWARE_MIC_DEVICE','default')
out={'gate':'GATE_04_LINUX_MICROPHONE','status':'BLOCKED','timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ffmpeg':shutil.which('ffmpeg'),'dev_snd_exists':Path('/dev/snd').exists(),'backend':backend,'device':device}
if not out['ffmpeg']:
 out['reason']='ffmpeg unavailable'
elif not out['dev_snd_exists'] and not os.environ.get('PULSE_SERVER') and not Path(os.environ.get('XDG_RUNTIME_DIR','/nonexistent')).joinpath('pulse/native').exists():
 out['reason']='No ALSA/Pulse microphone device/socket is exposed to this runner; physical microphone cannot be evidenced.'
else:
 try:
  with tempfile.TemporaryDirectory() as td:
   am=AssetManager(Path(td)/'project'); rec=LinuxAudioRecorder(am); rec.start(backend,device); time.sleep(2.0); m=rec.stop_and_commit('V0.12.1 physical microphone gate'); am.validate_asset(m['asset_id'])
   out.update({'status':'PASS','asset_id':m['asset_id'],'bytes':m['size_bytes'],'sha256':m['sha256'],'physical_capture_seconds':2.0})
 except Exception as e:
  out['reason']='Physical capture attempt failed: '+repr(e)
E.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False));raise SystemExit(0 if out['status']=='PASS' else 2)
