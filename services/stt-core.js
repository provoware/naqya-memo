'use strict';

window.NAQYA=window.NAQYA||{};

const PROFILES={
  schnell:{id:'schnell',label:'Schnell',engineModel:'tiny',approxMiB:75,description:'Für schwächere Geräte und kurze Diktate.'},
  ausgewogen:{id:'ausgewogen',label:'Ausgewogen',engineModel:'base',approxMiB:142,description:'Empfohlenes Standardprofil für Deutsch.'},
  genau:{id:'genau',label:'Genau',engineModel:'small',approxMiB:466,description:'Mehr Qualität bei höherem Speicher- und Rechenbedarf.'},
  maximum:{id:'maximum',label:'Maximum',engineModel:'medium',approxMiB:1536,description:'Für leistungsfähige Desktop-Geräte.'}
};

function speechCtor(){return window.SpeechRecognition||window.webkitSpeechRecognition}
function browserOnDeviceAvailable(){
  const C=speechCtor();
  if(!C)return false;
  try{return 'processLocally' in C.prototype||'processLocally' in new C()}catch{return false}
}
async function blobToBase64(blob){
  const bytes=new Uint8Array(await blob.arrayBuffer());
  let binary='';
  const chunk=0x8000;
  for(let i=0;i<bytes.length;i+=chunk)binary+=String.fromCharCode(...bytes.subarray(i,i+chunk));
  return btoa(binary);
}

window.NAQYA.stt={
  profiles:PROFILES,
  providers(){
    return {
      browserOnDevice:browserOnDeviceAvailable(),
      nativeWhisper:Boolean(window.NAQYA.nativeBridge?.available?.())
    };
  },
  async nativeCapabilities(){
    if(!window.NAQYA.nativeBridge?.available?.())return {available:false,platform:'browser',whisper:false};
    return window.NAQYA.nativeBridge.capabilities();
  },
  createBrowserRecognition(language='de-DE'){
    if(!browserOnDeviceAvailable())throw new Error('Lokale Browser-Spracherkennung ist auf diesem Gerät nicht verfügbar.');
    const C=speechCtor();
    const recognition=new C();
    recognition.lang=language;
    recognition.continuous=true;
    recognition.interimResults=true;
    recognition.processLocally=true;
    return recognition;
  },
  async transcribeNative(blob,{language='de',modelPath='',threads=null}={}){
    if(!window.NAQYA.nativeBridge?.available?.())throw new Error('Native whisper.cpp-Brücke ist nicht verfügbar.');
    if(!modelPath)throw new Error('Für die native Transkription fehlt der lokale Modellpfad.');
    const audioBase64=await blobToBase64(blob);
    return window.NAQYA.nativeBridge.transcribe({audioBase64,modelPath,language,threads});
  },
  validateModelFile(file){
    if(!file)return {ok:false,reason:'Keine Modelldatei gewählt.'};
    const name=file.name.toLowerCase();
    if(!name.endsWith('.bin')&&!name.endsWith('.gguf'))return {ok:false,reason:'Erwartet wird eine lokale .bin- oder .gguf-Modelldatei.'};
    if(file.size<10*1024*1024)return {ok:false,reason:'Die Datei ist ungewöhnlich klein und wahrscheinlich kein vollständiges Sprachmodell.'};
    return {ok:true,reason:''};
  }
};
