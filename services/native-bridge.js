'use strict';

window.NAQYA=window.NAQYA||{};

function tauriInvoke(){
  return window.__TAURI__?.core?.invoke||window.__TAURI__?.invoke||null;
}

window.NAQYA.nativeBridge={
  available(){return Boolean(tauriInvoke())},
  async capabilities(){
    const invoke=tauriInvoke();
    if(!invoke)return {available:false,platform:'browser',whisper:false};
    return invoke('naqya_capabilities');
  },
  async materializeModel({name,modelBase64,sha256=null}){
    const invoke=tauriInvoke();
    if(!invoke)throw new Error('Native Desktop-Brücke ist nicht verfügbar.');
    return invoke('naqya_materialize_model',{request:{name,modelBase64,sha256}});
  },
  async transcribe({audioBase64,modelPath,language='de',threads=null}){
    const invoke=tauriInvoke();
    if(!invoke)throw new Error('Native Desktop-Brücke ist nicht verfügbar.');
    return invoke('naqya_transcribe',{request:{audioBase64,modelPath,language,threads}});
  }
};
