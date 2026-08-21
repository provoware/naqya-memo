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

window.NAQYA.nativeBridge={
  available(){return Boolean(tauriInvoke())},
  async capabilities(){
    const invoke=tauriInvoke();
    if(!invoke)return {available:false,platform:'browser',whisper:false};
    return invoke('naqya_capabilities');
  },
  async materializeModel({name,blob,sha256=null,onProgress=null}){
    const invoke=tauriInvoke();
    if(!invoke)throw new Error('Native Desktop-Brücke ist nicht verfügbar.');
    if(!(blob instanceof Blob))throw new Error('Für die Modellmaterialisierung fehlen lokale Binärdaten.');
    const begin=await invoke('naqya_model_begin',{request:{name,sha256}}),token=begin.token;
    try{
      for(let offset=0;offset<blob.size;offset+=MODEL_CHUNK_BYTES){
        const part=blob.slice(offset,Math.min(blob.size,offset+MODEL_CHUNK_BYTES));
        const bytes=new Uint8Array(await part.arrayBuffer());
        await invoke('naqya_model_append',{request:{token,chunkBase64:bytesToBase64(bytes)}});
        if(onProgress)onProgress({written:Math.min(blob.size,offset+part.size),total:blob.size});
      }
      return await invoke('naqya_model_finish',{request:{token,name,sha256}});
    }catch(error){
      try{await invoke('naqya_model_abort',{request:{token}})}catch{}
      throw error;
    }
  },
  async transcribe({audioBase64,modelPath,language='de',threads=null}){
    const invoke=tauriInvoke();
    if(!invoke)throw new Error('Native Desktop-Brücke ist nicht verfügbar.');
    return invoke('naqya_transcribe',{request:{audioBase64,modelPath,language,threads}});
  }
};
