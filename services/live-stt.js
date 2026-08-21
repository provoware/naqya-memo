'use strict';

window.NAQYA=window.NAQYA||{};

const LIVE_STT_SEGMENT_MS=4000;
// ENTWICKLERHINWEIS: Die Promise-Kette serialisiert STT-Segmente absichtlich, damit Textreihenfolge und Messwerte stabil bleiben.
const liveState={capture:null,queue:Promise.resolve(),stopping:false,segments:0,audioMs:0,sttMs:0,modelId:null,modelPath:'',transcript:''};

function liveDiagnosticFailure(code,error,detail={}){
  try{return window.NAQYA?.diagnostics?.failure?.(code,error,detail)||null}catch{return null}
}

async function materializePreferredModel(){
  if(!window.NAQYA?.nativeBridge?.available?.())throw new Error('Native Desktop-Brücke ist nicht verfügbar.');
  if(!state.models?.length)throw new Error('Noch kein lokales Sprachmodell importiert. Unter Einstellungen zuerst ein .bin- oder .gguf-Modell hinzufügen.');
  const wanted=window.NAQYA?.stt?.profiles?.[state.modelProfile]?.engineModel||'';
  const model=state.models.find(m=>String(m.name||'').toLowerCase().includes(wanted))||state.models[0];
  if(model.nativePath&&model.materializedSha256===model.sha256){liveState.modelId=model.id;liveState.modelPath=model.nativePath;return model.nativePath}
  if(!model.blob)throw new Error('Die gespeicherte Modelldatei enthält keine lokalen Binärdaten.');
  const status=$('#dictationStatus');
  const result=await window.NAQYA.nativeBridge.materializeModel({
    name:model.name,blob:model.blob,sha256:model.sha256||null,
    onProgress:p=>{if(status&&p.total)status.textContent=`Sprachmodell wird lokal vorbereitet … ${Math.round(p.written/p.total*100)} %`}
  });
  const updated={...model,nativePath:result.path,materializedSha256:result.sha256||model.sha256,status:'native-bereit',materializedAt:new Date().toISOString()};
  await put('models',updated);state.models=await all('models');liveState.modelId=model.id;liveState.modelPath=result.path;
  return result.path;
}

async function invalidateCachedModelPath(){
  if(!liveState.modelId)return;
  const model=await get('models',liveState.modelId);if(!model)return;
  await put('models',{...model,nativePath:null,materializedSha256:null,status:'lokal-importiert'});state.models=await all('models');
}

async function transcribeLiveSegment(segment,sessionId){
  try{
    const result=await window.NAQYA.stt.transcribeNative(segment.blob,{language:'de',modelPath:liveState.modelPath,threads:null});
    const text=String(result?.text||'').trim();
    liveState.segments+=1;liveState.audioMs+=segment.durationMs||0;liveState.sttMs+=Number(result?.elapsedMs||0);
    if(text){liveState.transcript=(liveState.transcript+' '+text).trim();state.dictationFinal=liveState.transcript+' ';state.dictationInterim='';const target=$('#dictationText');if(target)target.textContent=liveState.transcript}
    await updateSession(sessionId,{transcriptDraft:liveState.transcript,nativeSttSegments:liveState.segments,nativeSttAudioMs:liveState.audioMs,nativeSttElapsedMs:liveState.sttMs,nativeModelId:liveState.modelId,nativeModelPath:liveState.modelPath});
    const status=$('#dictationStatus');
    if(status){const factor=liveState.audioMs?liveState.sttMs/liveState.audioMs:0;status.textContent=`Offline-Live-Diktat · ${liveState.segments} Segmente · Echtzeitfaktor ${factor.toFixed(2)}`}
  }catch(err){
    if(String(err?.message||err).includes('Sprachmodell'))await invalidateCachedModelPath();
    liveDiagnosticFailure('NAQYA-STT-4002',err,{where:'liveSTT.transcribeLiveSegment',how:'4-Sekunden-Live-Segment über lokalen STT-Provider',context:{segment_duration_ms:segment.durationMs||0,segment_number:liveState.segments+1},dialog:true});
    throw err;
  }
}

async function startNativeLiveDictation(){
  const status=$('#dictationStatus');
  const capabilities=await window.NAQYA.stt.nativeCapabilities();
  if(!capabilities?.whisper)throw new Error('whisper.cpp wurde lokal nicht gefunden.');
  liveState.modelPath=await materializePreferredModel();
  state.dictationFinal='';state.dictationInterim='';liveState.transcript='';liveState.queue=Promise.resolve();liveState.stopping=false;liveState.segments=0;liveState.audioMs=0;liveState.sttMs=0;
  const active=await startSegmentedRecorder('dictation');
  const Capture=window.NAQYA?.audioNormalizer?.LivePcmCapture;
  if(!Capture){await stopActiveRecorder('');throw new Error('Audio-Normalisierung ist nicht geladen.');}
  liveState.capture=new Capture(active.stream,{segmentMs:LIVE_STT_SEGMENT_MS,onSegment:segment=>{
    liveState.queue=liveState.queue.then(()=>transcribeLiveSegment(segment,active.sessionId)).catch(async err=>{
      console.error('Live-STT Segment:',err);await updateSession(active.sessionId,{nativeSttError:String(err.message||err)});const s=$('#dictationStatus');if(s)s.textContent=`Lokale Transkription: ${err.message||err}`;
    });
    return liveState.queue;
  },onError:err=>{
    liveDiagnosticFailure('NAQYA-STT-4003',err,{where:'liveSTT.LivePcmCapture',how:'Web-Audio-PCM-Erfassung 16 kHz Mono',dialog:true});
    const s=$('#dictationStatus');if(s)s.textContent=`PCM-Erfassung: ${err.message||err}`;
  }});
  await liveState.capture.start();
  if(status)status.textContent='Offline-Live-Diktat läuft · 16 kHz Mono PCM · whisper.cpp';
  render();
}

async function waitForSessionFinalization(sessionId,timeoutMs=12000){
  const started=Date.now();
  while(Date.now()-started<timeoutMs){
    const session=await get('audioSessions',sessionId);
    if(session&&['finalized','recovered','recoverable','empty'].includes(session.status))return session;
    await new Promise(resolve=>setTimeout(resolve,100));
  }
  return get('audioSessions',sessionId);
}

async function stopNativeLiveDictation(){
  if(liveState.stopping)return;liveState.stopping=true;
  const status=$('#dictationStatus');if(status)status.textContent='Aufnahme beendet · letztes Segment wird lokal transkribiert …';
  const active=state.activeRecorder;
  try{
    await liveState.capture?.stop();
    if(active?.recorder?.state==='recording'){
      active.pendingTranscript=liveState.transcript;
      await updateSession(active.sessionId,{status:'stopping-stt',transcriptDraft:liveState.transcript});
      active.recorder.stop();
    }
    await liveState.queue;
    const finalText=liveState.transcript.trim();
    if(active?.sessionId){
      const session=await waitForSessionFinalization(active.sessionId);
      if(session?.entryId){
        const entry=await get('entries',session.entryId);
        if(entry){await put('entries',{...entry,text:finalText,title:finalText.slice(0,70)||'Diktat',updatedAt:new Date().toISOString()})}
      }
      await updateSession(active.sessionId,{transcriptDraft:finalText,nativeSttSegments:liveState.segments,nativeSttAudioMs:liveState.audioMs,nativeSttElapsedMs:liveState.sttMs});
    }
    if(status){const factor=liveState.audioMs?liveState.sttMs/liveState.audioMs:0;status.textContent=`Diktat gespeichert · ${liveState.segments} Segmente · Echtzeitfaktor ${factor.toFixed(2)}`}
    await refresh();
  }catch(error){
    liveDiagnosticFailure('NAQYA-STT-4005',error,{where:'liveSTT.stopNativeLiveDictation',how:'Aufnahme stoppen, STT-Warteschlange leeren und Sitzung finalisieren',dialog:true});
    throw error;
  }finally{liveState.capture=null;liveState.stopping=false;liveState.modelPath='';liveState.modelId=null;liveState.transcript=''}
}

const previousToggleDictation=toggleDictation;
toggleDictation=async function(){
  if(state.activeRecorder?.kind==='dictation'&&liveState.capture){await stopNativeLiveDictation();return}
  if(state.activeRecorder){const status=$('#dictationStatus');if(status)status.textContent='Bitte zuerst die laufende Aufnahme beenden.';return}
  const providers=window.NAQYA?.stt?.providers?.()||{};
  if(providers.nativeWhisper){
    try{await startNativeLiveDictation();return}catch(err){
      liveDiagnosticFailure('NAQYA-STT-4004',err,{where:'liveSTT.toggleDictation',how:'Native Offline-Live-STT starten',result:providers.browserOnDevice?'Native STT nicht startbar; lokaler Browser-Fallback ist verfügbar':String(err.message||err),context:{browser_on_device_fallback:Boolean(providers.browserOnDevice)},dialog:!providers.browserOnDevice});
      const status=$('#dictationStatus');if(status)status.textContent=`Native Offline-STT nicht startbar: ${err.message}`;if(!providers.browserOnDevice)return
    }
  }
  if(!providers.nativeWhisper&&!providers.browserOnDevice)liveDiagnosticFailure('NAQYA-STT-4001',new Error('Keine lokale STT-Engine verfügbar.'),{where:'liveSTT.toggleDictation',how:'Lokale Providerwahl',dialog:true});
  await previousToggleDictation();
};

window.NAQYA.liveSTT={LIVE_STT_SEGMENT_MS,materializePreferredModel,startNativeLiveDictation,stopNativeLiveDictation,state:liveState};
