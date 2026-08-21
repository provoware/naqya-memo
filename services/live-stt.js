'use strict';

window.NAQYA=window.NAQYA||{};

const LIVE_STT_SEGMENT_MS=4000;
const liveState={capture:null,queue:Promise.resolve(),stopping:false,segments:0,audioMs:0,sttMs:0,modelId:null,modelPath:''};

async function materializePreferredModel(){
  if(!window.NAQYA?.nativeBridge?.available?.())throw new Error('Native Desktop-Brücke ist nicht verfügbar.');
  if(!state.models?.length)throw new Error('Noch kein lokales Sprachmodell importiert. Unter Einstellungen zuerst ein .bin- oder .gguf-Modell hinzufügen.');
  const wanted=window.NAQYA?.stt?.profiles?.[state.modelProfile]?.engineModel||'';
  const model=state.models.find(m=>String(m.name||'').toLowerCase().includes(wanted))||state.models[0];
  if(model.nativePath&&model.materializedSha256===model.sha256){liveState.modelId=model.id;liveState.modelPath=model.nativePath;return model.nativePath}
  if(!model.blob)throw new Error('Die gespeicherte Modelldatei enthält keine lokalen Binärdaten.');
  const modelBase64=await blobToBase64(model.blob);
  const result=await window.NAQYA.nativeBridge.materializeModel({name:model.name,modelBase64,sha256:model.sha256||null});
  const updated={...model,nativePath:result.path,materializedSha256:result.sha256||model.sha256,status:'native-bereit',materializedAt:new Date().toISOString()};
  await put('models',updated);state.models=await all('models');liveState.modelId=model.id;liveState.modelPath=result.path;
  return result.path;
}

async function transcribeLiveSegment(segment,sessionId){
  const result=await window.NAQYA.stt.transcribeNative(segment.blob,{language:'de',modelPath:liveState.modelPath,threads:null});
  const text=String(result?.text||'').trim();
  liveState.segments+=1;liveState.audioMs+=segment.durationMs||0;liveState.sttMs+=Number(result?.elapsedMs||0);
  if(text){state.dictationFinal=(state.dictationFinal+' '+text).trim()+' ';state.dictationInterim='';const target=$('#dictationText');if(target)target.textContent=state.dictationFinal.trim()}
  await updateSession(sessionId,{transcriptDraft:state.dictationFinal.trim(),nativeSttSegments:liveState.segments,nativeSttAudioMs:liveState.audioMs,nativeSttElapsedMs:liveState.sttMs,nativeModelId:liveState.modelId,nativeModelPath:liveState.modelPath});
  const status=$('#dictationStatus');
  if(status){const factor=liveState.audioMs?liveState.sttMs/liveState.audioMs:0;status.textContent=`Offline-Live-Diktat · ${liveState.segments} Segmente · Echtzeitfaktor ${factor.toFixed(2)}`}
}

async function startNativeLiveDictation(){
  const status=$('#dictationStatus');
  const capabilities=await window.NAQYA.stt.nativeCapabilities();
  if(!capabilities?.whisper)throw new Error('whisper.cpp wurde lokal nicht gefunden.');
  liveState.modelPath=await materializePreferredModel();
  state.dictationFinal='';state.dictationInterim='';liveState.queue=Promise.resolve();liveState.stopping=false;liveState.segments=0;liveState.audioMs=0;liveState.sttMs=0;
  const active=await startSegmentedRecorder('dictation');
  const Capture=window.NAQYA?.audioNormalizer?.LivePcmCapture;
  if(!Capture){await stopActiveRecorder('');throw new Error('Audio-Normalisierung ist nicht geladen.');}
  liveState.capture=new Capture(active.stream,{segmentMs:LIVE_STT_SEGMENT_MS,onSegment:segment=>{
    liveState.queue=liveState.queue.then(()=>transcribeLiveSegment(segment,active.sessionId)).catch(async err=>{
      console.error('Live-STT Segment:',err);await updateSession(active.sessionId,{nativeSttError:String(err.message||err)});const s=$('#dictationStatus');if(s)s.textContent=`Lokale Transkription: ${err.message||err}`;
    });
    return liveState.queue;
  },onError:err=>{const s=$('#dictationStatus');if(s)s.textContent=`PCM-Erfassung: ${err.message||err}`;}});
  await liveState.capture.start();
  if(status)status.textContent='Offline-Live-Diktat läuft · 16 kHz Mono PCM · whisper.cpp';
  render();
}

async function stopNativeLiveDictation(){
  if(liveState.stopping)return;liveState.stopping=true;
  const status=$('#dictationStatus');if(status)status.textContent='Letztes Segment wird lokal transkribiert …';
  try{await liveState.capture?.stop();await liveState.queue;await stopActiveRecorder(state.dictationFinal.trim())}
  finally{liveState.capture=null;liveState.stopping=false;liveState.modelPath='';liveState.modelId=null}
}

const previousToggleDictation=toggleDictation;
toggleDictation=async function(){
  if(state.activeRecorder?.kind==='dictation'&&liveState.capture){await stopNativeLiveDictation();return}
  if(state.activeRecorder){const status=$('#dictationStatus');if(status)status.textContent='Bitte zuerst die laufende Aufnahme beenden.';return}
  const providers=window.NAQYA?.stt?.providers?.()||{};
  if(providers.nativeWhisper){
    try{await startNativeLiveDictation();return}catch(err){const status=$('#dictationStatus');if(status)status.textContent=`Native Offline-STT nicht startbar: ${err.message}`;if(!providers.browserOnDevice)return}
  }
  await previousToggleDictation();
};

window.NAQYA.liveSTT={LIVE_STT_SEGMENT_MS,materializePreferredModel,startNativeLiveDictation,stopNativeLiveDictation,state:liveState};
