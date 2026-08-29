from __future__ import annotations
from pathlib import Path
import os, shutil, subprocess, signal, time, uuid

class RecordingError(RuntimeError): pass

class LinuxAudioRecorder:
    """Linux native reference recorder using FFmpeg.

    Real microphone capture requires an available PipeWire/PulseAudio/ALSA input.
    The class stages WAV output and commits it through AssetManager only after
    FFmpeg exited cleanly and the file is non-empty.
    """
    def __init__(self, asset_manager):
        self.assets=asset_manager
        self.ffmpeg=shutil.which('ffmpeg')
        self.process=None
        self.staging=None

    def capability(self):
        return {"platform":"linux","ffmpeg":bool(self.ffmpeg),"native_microphone_tested":False,
                "capture_backends":["pulse","alsa"],"status":"AVAILABLE" if self.ffmpeg else "MISSING_FFMPEG"}

    def build_command(self, staging: Path, backend: str='pulse', device: str='default'):
        if not self.ffmpeg: raise RecordingError('FFMPEG_NOT_FOUND')
        if backend not in {'pulse','alsa'}: raise RecordingError('AUDIO_BACKEND_UNSUPPORTED')
        return [self.ffmpeg,'-hide_banner','-loglevel','error','-y','-f',backend,'-i',device,
                '-ac','1','-ar','48000','-c:a','pcm_s16le',str(staging)]

    def start(self, backend='pulse', device='default'):
        if self.process and self.process.poll() is None: raise RecordingError('RECORDING_ALREADY_ACTIVE')
        self.staging=self.assets.temp/f"recording_{uuid.uuid4().hex}.wav"
        cmd=self.build_command(self.staging,backend,device)
        self.process=subprocess.Popen(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
        time.sleep(.12)
        if self.process.poll() is not None:
            err=(self.process.stderr.read() if self.process.stderr else '').strip()
            self.staging.unlink(missing_ok=True)
            raise RecordingError('MICROPHONE_CAPTURE_START_FAILED'+(':'+err[:180] if err else ''))
        return {"status":"RECORDING","staging":self.staging.name,"backend":backend,"device":device}

    def stop_and_commit(self, title='Sprachmemo'):
        if not self.process or self.process.poll() is not None: raise RecordingError('RECORDING_NOT_ACTIVE')
        self.process.send_signal(signal.SIGINT)
        try: rc=self.process.wait(timeout=8)
        except subprocess.TimeoutExpired:
            self.process.terminate(); rc=self.process.wait(timeout=3)
        if rc not in (0,255) or not self.staging.exists() or self.staging.stat().st_size<=44:
            self.staging.unlink(missing_ok=True)
            raise RecordingError('RECORDING_COMMIT_REJECTED')
        manifest=self.assets.import_asset(self.staging,'audio',title)
        self.staging.unlink(missing_ok=True)
        self.process=None
        return manifest

def create_synthetic_recording(asset_manager, title='Acceptance-Signal', duration=.25):
    """Acceptance-only FFmpeg audio generation; not microphone evidence."""
    ffmpeg=shutil.which('ffmpeg')
    if not ffmpeg: raise RecordingError('FFMPEG_NOT_FOUND')
    stage=asset_manager.temp/f"synthetic_{uuid.uuid4().hex}.wav"
    cmd=[ffmpeg,'-hide_banner','-loglevel','error','-y','-f','lavfi','-i',f'sine=frequency=440:duration={duration}',
         '-ac','1','-ar','16000','-c:a','pcm_s16le',str(stage)]
    p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=10)
    if p.returncode!=0 or not stage.exists(): raise RecordingError('SYNTHETIC_RECORDING_FAILED')
    manifest=asset_manager.import_asset(stage,'audio',title)
    stage.unlink(missing_ok=True)
    return manifest
