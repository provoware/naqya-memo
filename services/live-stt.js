'use strict';

window.NAQYA=window.NAQYA||{};

const LIVE_STT_SEGMENT_MS=4000;
// ENTWICKLERHINWEIS: Die Promise-Kette serialisiert STT-Segmente absichtlich, damit Textreihenfolge und Messwerte stabil bleiben.
const liveState={capture:null,queue:Promise.resolve(),stopping:false,segments:0,segmentsAttempted:0,segmentsFailed:0,audioMs:0,capturedAudioMs:0,sttMs:0,rtfMax:0,modelId:null,modelPath:'',transcript:''};

function runtimeMetricsSnapshot(){
  const avg=liveState.audioMs?liveState.sttMs/liveState.audioMs:0;
  return {
    schemaVersion:1,
    targetSegmentMs:LIVE_STT_SEGMENT_MS,
    segmentsTotal:liveState.segmentsAttempted,
    segmentsSucceeded:liveState.segments,
    segmentsLost:liveState.segmentsFailed,
    capturedAudioMs:liveState.capturedAudioMs,
    transcribedAudioMs:liveState.audioMs,
    sttElapsedMs:liveState.sttMs,
    realtimeFactorAvg:Number(avg.toFixed(6)),
    realtimeFactorMax:Number(liveState.rtfMax.toFixed(6))
  };
}

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
  const durationMs=Math.max(0,Number(segment.durationMs||0));
  const segmentNumber=liveState.segmentsAttempted+1;
  liveState.segmentsAttempted=segmentNumber;
  liveState.capturedAudioMs+=durationMs;
  try{
    const result=await window.NAQYA.stt.transcribeNative(segment.blob,{language:'de',modelPath:liveState.modelPath,threads:null});
    const text=String(result?.text||'').trim();
    const elapsedMs=Math.max(0,Number(result?.elapsedMs||0));
    const factor=durationMs?elapsedMs/durationMs:0;
    liveState.segments+=1;liveState.audioMs+=durationMs;liveState.sttMs+=elapsedMs;liveState.rtfMax=Math.max(liveState.rtfMax,factor);
    if(text){liveState.transcript=(liveState.transcript+' '+text).trim();state.dictationFinal=liveState.transcript+' ';state.dictationInterim='';const target=$('#dictationText');if(target)target.textContent=liveState.transcript}
    await updateSession(sessionId,{transcriptDraft:liveState.transcript,nativeSttSegments:liveState.segments,nativeSttSegmentsAttempted:liveState.segmentsAttempted,nativeSttSegmentsLost:liveState.segmentsFailed,nativeSttAudioMs:liveState.audioMs,nativeSttCapturedAudioMs:liveState.capturedAudioMs,nativeSttElapsedMs:liveState.sttMs,nativeSttRealtimeFactorMax:liveState.rtfMax,nativeSttRuntimeMetrics:runtimeMetricsSnapshot(),nativeModelId:liveState.modelId,nativeModelPath:liveState.modelPath});
    const status=$('#dictationStatus');
    if(status){const avg=liveState.audioMs?liveState.sttMs/liveState.audioMs:0;status.textContent=`Offline-Live-Diktat · ${liveState.segmentsAttempted} Segmente · Echtzeitfaktor Ø ${avg.toFixed(2)} / max ${liveState.rtfMax.toFixed(2)}`}
  }catch(err){
    liveState.segmentsFailed+=1;
    await updateSession(sessionId,{nativeSttSegmentsAttempted:liveState.segmentsAttempted,nativeSttSegmentsLost:liveState.segmentsFailed,nativeSttCapturedAudioMs:liveState.capturedAudioMs,nativeSttRuntimeMetrics:runtimeMetricsSnapshot(),nativeSttError:String(err?.message||err)});
    if(String(err?.message||err).includes('Sprachmodell'))await invalidateCachedModelPath();
    liveDiagnosticFailure('NAQYA-STT-4002',err,{where:'liveSTT.transcribeLiveSegment',how:'4-Sekunden-Live-Segment über lokalen STT-Provider',context:{segment_duration_ms:durationMs,segment_number:segmentNumber},dialog:true});
    throw err;
  }
}

async function startNativeLiveDictation(){
  const status=$('#dictationStatus');
  const capabilities=await window.NAQYA.stt.nativeCapabilities();
  if(!capabilities?.whisper)throw new Error('whisper.cpp wurde lokal nicht gefunden.');
  liveState.modelPath=await materializePreferredModel();
  state.dictationFinal='';state.dictationInterim='';liveState.transcript='';liveState.queue=Promise.resolve();liveState.stopping=false;liveState.segments=0;liveState.segmentsAttempted=0;liveState.segmentsFailed=0;liveState.audioMs=0;liveState.capturedAudioMs=0;liveState.sttMs=0;liveState.rtfMax=0;
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
      await updateSession(active.sessionId,{transcriptDraft:finalText,nativeSttSegments:liveState.segments,nativeSttSegmentsAttempted:liveState.segmentsAttempted,nativeSttSegmentsLost:liveState.segmentsFailed,nativeSttAudioMs:liveState.audioMs,nativeSttCapturedAudioMs:liveState.capturedAudioMs,nativeSttElapsedMs:liveState.sttMs,nativeSttRealtimeFactorMax:liveState.rtfMax,nativeSttRuntimeMetrics:runtimeMetricsSnapshot()});
    }
    if(status){const avg=liveState.audioMs?liveState.sttMs/liveState.audioMs:0;status.textContent=`Diktat gespeichert · ${liveState.segmentsAttempted} Segmente · verloren ${liveState.segmentsFailed} · Echtzeitfaktor Ø ${avg.toFixed(2)} / max ${liveState.rtfMax.toFixed(2)}`}
    await refresh();
  }catch(error){
    liveDiagnosticFailure('NAQYA-STT-4005',error,{where:'liveSTT.stopNativeLiveDictation',how:'Aufnahme stoppen, STT-Warteschlange leeren und Sitzung finalisieren',dialog:true});
    throw error;
  }finally{liveState.capture=null;liveState.stopping=false;liveState.modelPath='';liveState.modelId=null;liveState.transcript=''}
}

function runtimeMetricsEnvelope(){
  const metrics=runtimeMetricsSnapshot();
  if(metrics.segmentsTotal<1)throw new Error('Noch keine native Live-STT-Messung vorhanden.');
  return {format:'NAQYA-LIVE-STT-RUNTIME',schemaVersion:1,exportedAt:new Date().toISOString(),metrics};
}

function exportRuntimeMetricsFile(){
  if(typeof downloadJson!=='function')throw new Error('Lokaler JSON-Export ist nicht verfügbar.');
  const payload=runtimeMetricsEnvelope();
  const stamp=new Date().toISOString().replace(/[:.]/g,'-');
  downloadJson(payload,`NAQYA_RUNTIME_METRICS_${stamp}.json`);
  return payload;
}

function wireRuntimeMetricsExport(){
  const status=$('#dictationStatus');
  if(!status||$('#exportRuntimeMetrics'))return;
  const host=status.closest('.audio-box');if(!host)return;
  const button=document.createElement('button');
  button.id='exportRuntimeMetrics';button.className='secondary';button.type='button';
  button.textContent='⬇ Laufzeit-Messwerte exportieren';
  button.disabled=runtimeMetricsSnapshot().segmentsTotal<1;
  button.title=button.disabled?'Nach einem nativen Offline-Diktat verfügbar':'E3-Messwerte als JSON für Hardware-Abnahme speichern';
  button.addEventListener('click',()=>{try{exportRuntimeMetricsFile()}catch(err){alert(`Messwert-Export fehlgeschlagen: ${err.message||err}`)}});
  host.appendChild(button);
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

const previousWireDynamic=wireDynamic;
wireDynamic=function(){previousWireDynamic();wireRuntimeMetricsExport()};

window.NAQYA.liveSTT={LIVE_STT_SEGMENT_MS,materializePreferredModel,startNativeLiveDictation,stopNativeLiveDictation,runtimeMetricsSnapshot,runtimeMetricsEnvelope,exportRuntimeMetricsFile,state:liveState};
