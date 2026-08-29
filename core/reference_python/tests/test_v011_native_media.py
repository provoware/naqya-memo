from pathlib import Path
import tempfile, sys, shutil
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'core/reference_python'))
from provoware_core.assets import AssetManager, AssetError
from provoware_core.media import LinuxAudioRecorder, create_synthetic_recording

def test_synthetic_ffmpeg_recording_commits_asset():
    if not shutil.which('ffmpeg'): return
    with tempfile.TemporaryDirectory() as td:
        am=AssetManager(Path(td)/'project'); m=create_synthetic_recording(am)
        assert m['kind']=='audio' and m['size_bytes']>44 and am.validate_asset(m['asset_id'])['sha256']==m['sha256']

def test_linux_recorder_command_is_native_capture_contract():
    with tempfile.TemporaryDirectory() as td:
        am=AssetManager(Path(td)/'project'); r=LinuxAudioRecorder(am)
        if r.ffmpeg:
            cmd=r.build_command(am.temp/'x.wav','pulse','default')
            assert '-f' in cmd and 'pulse' in cmd and 'pcm_s16le' in cmd

if __name__=='__main__':
    tests=[v for k,v in sorted(globals().items()) if k.startswith('test_')]
    bad=[]
    for t in tests:
        try:t();print('PASS',t.__name__)
        except Exception as e:bad.append((t.__name__,repr(e)));print('FAIL',t.__name__,repr(e))
    print(f'SUMMARY total={len(tests)} passed={len(tests)-len(bad)} failed={len(bad)}')
    if bad:raise SystemExit(1)
