'use strict';

const NAQYA_03_VERSION='0.3.0';
state.nativePcmCapture=null;
state.nativeTranscriptionQueue=Promise.resolve();
state.nativeQueueDepth=0;
state.nativeStatus=null;
state.nativeLastRtf=null;

function mergeNativeTranscript(existing,incoming){
  const left=String(existing||'').trim(),right=String(incoming||'').trim();
  if(!left)return right;
  if(!right)return left;
  const a=left.split(/\s+/),b=right.split(/\s+/),max=Math.min(8,a.length,b.length);let overlap=0;
  for(let n=max;n>=1;n--){
    const tail=a.slice(-n).join(' ').toLocaleLowerCase('de-DE');
    const head=b.slice(0,n).join(' ').toLocaleLowerCase('de-DE');
    if(tail===head){overlap=n;break}
  }
  return `${left} ${b.slice(overlap).join(' ')}`.replace(/\s+/g,' ').trim();
}

async function refreshNativeStatus(){
  try{state.nativeStatus=await window.NAQYANativeSTT?.status?.(true)||{available:false,models:[]}}catch{state.nativeStatus={available:false,models:[]}}
  try{state.capabilities=await window.NAQYA.capabilities.detect()}catch{}
  return state.nativeStatus;
}

const init02=init;
init=async function(){
  try{await window.NAQYANativeSTT?.init?.()}catch{}
  await refreshNativeStatus();
  await init02();
  await refreshNativeStatus();
  render();
};

const renderModelManager02=renderModelManager;
renderModelManager=function(){
  const profiles=window.NAQYA?.stt?.profiles||{};
  const cards=Object.values(profiles).map(p=>`<button class="model-card ${state.modelProfile===p.id?'active':''}" data-model-profile="${p.id}"><strong>${esc(p.label)}</strong><span>~${p.approxMiB} MiB · ${esc(p.engineModel)}</span><small>${esc(p.description)}</small></button>`).join('');
  const native=state.nativeStatus||{available:false,models:[],modelDir:''};
  const nativeModels=(native.models||[]).length?(native.models||[]).map(m=>`<div class="model-file"><div><strong>${esc(m.name)}</strong><div><small>${humanBytes(m.bytes)} · ${esc(m.source||'native')}</small></div></div><span class="status-chip ok">aktivierbar</span></div>`).join(''):'<div class="empty">Noch kein natives Whisper-Modell installiert.</div>';
  const pwaModels=state.models.filter(m=>m.status!=='native-installiert');
  const pwa=pwaModels.length?pwaModels.map(m=>`<div class="model-file"><div><strong>${esc(m.name)}</strong><div><small>${humanBytes(m.size)} · Browser-Speicher</small></div></div><button class="secondary" data-delete-model="${m.id}">Entfernen</button></div>`).join(''):'<div class="empty">Keine zusätzlichen PWA-Modelldateien.</div>';
  return `<h2>Offline-Sprachmodell</h2><p class="muted">Wähle zuerst das Leistungsprofil. In der Desktop-App wird das Modell blockweise und vollständig lokal in den nativen App-Speicher übernommen.</p><div class="model-grid">${cards}</div><div class="native-model-panel"><h3>Desktop-Runtime</h3><p>${native.available?`<span class="status-chip ok">✓ whisper.cpp ${esc(native.whisperCppVersion||'')}</span>`:'<span class="status-chip warn">Desktop-Runtime nicht aktiv</span>'}</p>${native.modelDir?`<p class="muted path-text">Modellordner: ${esc(native.modelDir)}</p>`:''}<label class="secondary native-import">Lokales Modell installieren (.bin/.gguf)<input id="modelFile" type="file" accept=".bin,.gguf" hidden></label><div class="list" style="margin-top:12px">${nativeModels}</div></div><details class="pwa-models"><summary>PWA-Modellspeicher anzeigen</summary><div class="list" style="margin-top:12px">${pwa}</div></details>`;
};

const renderSettings02=renderSettings;
renderSettings=function(){
  return renderSettings02()
    .replace(`2026 ${VERSION}`,`2026 ${NAQYA_03_VERSION}`)
    .replace('AUDIO & OFFLINE-STT CORE','NATIVE WHISPER RUNTIME & DESKTOP BRIDGE');
};

const installModelFile02=installModelFile;
installModelFile=async function(e){
  const file=e.target.files?.[0];if(!file)return;
  const valid=window.NAQYA?.stt?.validateModelFile?.(file)||{ok:false,reason:'STT-Modul nicht geladen.'};
  if(!valid.ok){alert(valid.reason);e.target.value='';return}
  const native=await window.NAQYANativeSTT?.status?.();
  if(!native?.available)return installModelFile02(e);
  try{
    assistant('<strong>Sprachmodell wird installiert …</strong><p id="nativeModelProgress">0 %</p><p>Die Datei bleibt vollständig auf diesem Gerät.</p>');
    const result=await window.NAQYA.stt.importNativeModel(file,{onProgress:p=>{const el=$('#nativeModelProgress');if(el)el.textContent=`${p.percent} % · ${humanBytes(p.sent)} / ${humanBytes(p.total)}`}});
    const old=state.models.find(m=>m.name===file.name&&m.status==='native-installiert');if(old)await del('models',old.id);
    await put('models',{id:uid(),name:file.name,size:file.size,createdAt:new Date().toISOString(),status:'native-installiert',nativePath:result.path,source:result.source||'App-Daten'});
    await refreshNativeStatus();
    await refresh();
    assistant(`<strong>✓ Sprachmodell installiert</strong><p>${esc(file.name)} ist jetzt für die lokale Desktop-Transkription verfügbar.</p>`);
  }catch(err){alert(`Modell konnte nicht installiert werden: ${err}`)}finally{e.target.value=''}
};

const toggleDictation02=toggleDictation;
toggleDictation=async function(){
  const statusEl=$('#dictationStatus');
  if(state.activeRecorder?.kind==='dictation'&&state.nativePcmCapture){
    statusEl&&(statusEl.textContent='Finalisiere lokale Transkription …');
    try{await state.nativePcmCapture.stop()}catch(e){console.warn('PCM stop:',e)}
    state.nativePcmCapture=null;
    try{await state.nativeTranscriptionQueue}catch{}
    const text=(state.dictationFinal+state.dictationInterim).trim();
    await stopActiveRecorder(text);
    return;
  }
  if(state.activeRecorder)return toggleDictation02();

  const native=await window.NAQYANativeSTT?.status?.(true);
  const nativeModel=(native?.models||[]).length>0;
  if(!native?.available||!nativeModel)return toggleDictation02();

  try{
    const active=await startSegmentedRecorder('dictation');
    state.dictationFinal='';state.dictationInterim='';state.nativeQueueDepth=0;state.nativeLastRtf=null;
    state.nativeTranscriptionQueue=Promise.resolve();
    state.nativePcmCapture=await window.NAQYANativeSTT.startPcmCapture(active.stream,{chunkMs:AUDIO_SLICE_MS,onChunk:async samples=>{
      state.nativeQueueDepth+=1;
      state.nativeTranscriptionQueue=state.nativeTranscriptionQueue.then(async()=>{
        try{
          const result=await window.NAQYA.stt.transcribeNativePcm(samples,{language:'de',profile:state.modelProfile,noContext:true,singleSegment:true});
          state.nativeLastRtf=result.realtimeFactor;
          if(result.text)state.dictationFinal=mergeNativeTranscript(state.dictationFinal,result.text)+' ';
          const target=$('#dictationText');if(target)target.textContent=state.dictationFinal.trim()||'Sprache erkannt, warte auf Text …';
          const s=$('#dictationStatus');if(s)s.textContent=`Lokal · ${result.modelFile} · ${result.processingMs} ms · RTF ${Number(result.realtimeFactor).toFixed(2)}`;
          await updateSession(active.sessionId,{transcriptDraft:state.dictationFinal.trim(),nativeWhisper:true,lastRtf:result.realtimeFactor,lastProcessingMs:result.processingMs});
        }catch(error){
          const s=$('#dictationStatus');if(s)s.textContent=`Lokale Whisper-Transkription: ${String(error)}`;
          console.error('Native Whisper:',error);
        }finally{state.nativeQueueDepth=Math.max(0,state.nativeQueueDepth-1)}
      });
    }});
    render();
    const s=$('#dictationStatus');if(s)s.textContent='Native Offline-Transkription läuft · Audio wird zusätzlich gesichert';
  }catch(error){
    console.error('Native Diktatstart:',error);
    if(state.activeRecorder?.kind==='dictation')await stopActiveRecorder('');
    statusEl&&(statusEl.textContent=`Native Diktierfunktion konnte nicht starten: ${String(error)}`);
  }
};

const exportBackup02=exportBackup;
exportBackup=async function(){
  const files=await all('files'),total=files.reduce((n,f)=>n+(f.size||f.blob?.size||0),0);
  if(total>BACKUP_WARN_BYTES&&!confirm(`Dieses Vollbackup enthält ${humanBytes(total)} Binärdaten und benötigt vorübergehend zusätzlichen Arbeitsspeicher. Trotzdem fortfahren?`))return;
  const packed=[];
  for(const f of files){
    const blob=f.blob instanceof Blob?f.blob:new Blob([],{type:f.type||'application/octet-stream'});
    packed.push({id:f.id,name:f.name,type:f.type||blob.type,size:blob.size,createdAt:f.createdAt||null,sha256:await sha256Blob(blob),base64:await blobToBase64(blob)});
  }
  const models=(await all('models')).map(({blob,...meta})=>meta);
  const payload={format:'NAQYA-OFFLINE-BACKUP',schema:2,product:'PROVOWARE – NAQYA Memo Tool 2026',version:NAQYA_03_VERSION,exportedAt:new Date().toISOString(),entries:await all('entries'),projects:await all('projects'),settings:await all('settings'),files:packed,models,nativeRuntime:state.nativeStatus?{runtime:state.nativeStatus.runtime,whisperCppVersion:state.nativeStatus.whisperCppVersion,models:(state.nativeStatus.models||[]).map(m=>({name:m.name,bytes:m.bytes,source:m.source}))}:null};
  downloadJson(payload,`NAQYA_VOLLbackup_${todayKey()}.naqya-backup.json`);
};
