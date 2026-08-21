'use strict';

window.NAQYA=window.NAQYA||{};

// ENTWICKLERHINWEIS: 4-MiB-Blöcke begrenzen Base64-/IPC-Spitzen bei großen Modellen; nicht zu einem Gesamtpayload zusammenfassen.
const MODEL_CHUNK_BYTES=4*1024*1024;

function tauriInvoke(){
  return window.__TAURI__?.core?.invoke||window.__TAURI__?.invoke||null;
}
function bytesToBase64(bytes){
  let binary='';const chunk=0x8000;
  for(let i=0;i<bytes.length;i+=chunk)binary+=String.fromCharCode(...bytes.subarray(i,Math.min(i+chunk,bytes.length)));
  return btoa(binary);
}
function diagnosticFailure(code,error,detail={}){
  try{return window.NAQYA?.diagnostics?.failure?.(code,error,detail)||null}catch{return null}
}

window.NAQYA.nativeBridge={
  available(){return Boolean(tauriInvoke())},
  async capabilities(){
    const invoke=tauriInvoke();
    if(!invoke)return {available:false,platform:'browser',whisper:false};
    try{return await invoke('naqya_capabilities')}
    catch(error){diagnosticFailure('NAQYA-RUNTIME-6002',error,{where:'nativeBridge.capabilities',how:'Tauri invoke naqya_capabilities',result:'Native Laufzeitdiagnose nicht verfügbar'});throw error}
  },
  async materializeModel({name,blob,sha256=null,onProgress=null}){
    const invoke=tauriInvoke();
    if(!invoke){const error=new Error('Native Desktop-Brücke ist nicht verfügbar.');diagnosticFailure('NAQYA-RUNTIME-6001',error,{where:'nativeBridge.materializeModel',how:'Lokaler Modelltransfer',result:error.message});throw error}
    if(!(blob instanceof Blob))throw new Error('Für die Modellmaterialisierung fehlen lokale Binärdaten.');
    let token=null;
    try{
      const begin=await invoke('naqya_model_begin',{request:{name,sha256}});token=begin.token;
      for(let offset=0;offset<blob.size;offset+=MODEL_CHUNK_BYTES){
        const part=blob.slice(offset,Math.min(blob.size,offset+MODEL_CHUNK_BYTES));
        const bytes=new Uint8Array(await part.arrayBuffer());
        await invoke('naqya_model_append',{request:{token,chunkBase64:bytesToBase64(bytes)}});
        if(onProgress)onProgress({written:Math.min(blob.size,offset+part.size),total:blob.size});
      }
      return await invoke('naqya_model_finish',{request:{token,name,sha256}});
    }catch(error){
      if(token){try{await invoke('naqya_model_abort',{request:{token}})}catch{}}
      diagnosticFailure('NAQYA-MODEL-5001',error,{where:'nativeBridge.materializeModel',how:'4-MiB-IPC-Transfer, SHA-256-Prüfung und atomare Aktivierung',context:{model_bytes:blob.size,expected_sha256_present:Boolean(sha256)}});
      throw error;
    }
  },
  async transcribe({audioBase64,modelPath,language='de',threads=null}){
    const invoke=tauriInvoke();
    if(!invoke){const error=new Error('Native Desktop-Brücke ist nicht verfügbar.');diagnosticFailure('NAQYA-RUNTIME-6001',error,{where:'nativeBridge.transcribe',how:'Lokale STT-Anforderung',result:error.message});throw error}
    try{return await invoke('naqya_transcribe',{request:{audioBase64,modelPath,language,threads}})}
    catch(error){diagnosticFailure('NAQYA-RUNTIME-6003',error,{where:'nativeBridge.transcribe',how:'Tauri invoke naqya_transcribe',context:{audio_payload_chars:String(audioBase64||'').length,language,threads,model_configured:Boolean(modelPath)}});throw error}
  }
};
