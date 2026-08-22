'use strict';

window.NAQYA=window.NAQYA||{};

const STT_PROVIDER_CONTRACT=Object.freeze({
  format:'NAQYA-STT-PROVIDER',
  schemaVersion:1,
  resultSchemaVersion:1,
  engineFamily:'whisper.cpp',
  operations:Object.freeze({
    streamingRecognition:'streaming-recognition',
    transcribeSegment:'transcribe-segment'
  })
});

const STT_ADAPTERS=Object.freeze({
  browserOnDevice:Object.freeze({
    id:'browser-on-device',
    kind:'browser',
    engine:'browser-local-stt',
    transport:'web-speech',
    mode:'streaming-recognition',
    platforms:Object.freeze(['browser']),
    implemented:true
  }),
  desktopWhisper:Object.freeze({
    id:'desktop-whisper-cpp',
    kind:'native',
    engine:'whisper.cpp',
    transport:'tauri-sidecar',
    mode:'transcribe-segment',
    platforms:Object.freeze(['linux','windows']),
    implemented:true
  }),
  androidWhisper:Object.freeze({
    id:'android-whisper-cpp',
    kind:'native',
    engine:'whisper.cpp',
    transport:'jni-ndk',
    mode:'transcribe-segment',
    platforms:Object.freeze(['android']),
    implemented:false
  }),
  iosWhisper:Object.freeze({
    id:'ios-whisper-cpp',
    kind:'native',
    engine:'whisper.cpp',
    transport:'swift-native',
    mode:'transcribe-segment',
    platforms:Object.freeze(['ios','ipados']),
    implemented:false
  })
});

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
function desktopWhisperAvailable(){return Boolean(window.NAQYA.nativeBridge?.available?.())}
function adapterState(adapter){
  let available=false;
  if(adapter.id==='browser-on-device')available=browserOnDeviceAvailable();
  if(adapter.id==='desktop-whisper-cpp')available=desktopWhisperAvailable();
  return {...adapter,available};
}
function normalizePlatform(platform=''){
  const value=String(platform||'').trim().toLowerCase();
  if(['darwin','iphone','ipad','iphoneos','ipados','ios'].includes(value))return value==='ipados'||value==='ipad'?'ipados':'ios';
  if(['win32','windows','win'].includes(value))return 'windows';
  if(['linux','android','browser'].includes(value))return value;
  return value||'browser';
}
function adapterForPlatform(platform){
  const normalized=normalizePlatform(platform);
  if(normalized==='linux'||normalized==='windows')return adapterState(STT_ADAPTERS.desktopWhisper);
  if(normalized==='android')return adapterState(STT_ADAPTERS.androidWhisper);
  if(normalized==='ios'||normalized==='ipados')return adapterState(STT_ADAPTERS.iosWhisper);
  return adapterState(STT_ADAPTERS.browserOnDevice);
}
async function blobToBase64(blob){
  const bytes=new Uint8Array(await blob.arrayBuffer());
  let binary='';
  const chunk=0x8000;
  for(let i=0;i<bytes.length;i+=chunk)binary+=String.fromCharCode(...bytes.subarray(i,i+chunk));
  return btoa(binary);
}

window.NAQYA.stt={
  contract:STT_PROVIDER_CONTRACT,
  adapters:STT_ADAPTERS,
  profiles:PROFILES,
  providers(){
    return {
      browserOnDevice:browserOnDeviceAvailable(),
      nativeWhisper:desktopWhisperAvailable(),
      adapters:{
        browserOnDevice:adapterState(STT_ADAPTERS.browserOnDevice),
        desktopWhisper:adapterState(STT_ADAPTERS.desktopWhisper),
        androidWhisper:adapterState(STT_ADAPTERS.androidWhisper),
        iosWhisper:adapterState(STT_ADAPTERS.iosWhisper)
      }
    };
  },
  adapterForPlatform,
  async nativeCapabilities(){
    if(!desktopWhisperAvailable())return {available:false,platform:'browser',whisper:false};
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
    if(!desktopWhisperAvailable())throw new Error('Native whisper.cpp-Brücke ist nicht verfügbar.');
    if(!modelPath)throw new Error('Für die native Transkription fehlt der lokale Modellpfad.');
    const audioBase64=await blobToBase64(blob);
    return window.NAQYA.nativeBridge.transcribe({audioBase64,modelPath,language,threads});
  },
  async transcribeWithAdapter(adapterId,blob,options={}){
    if(adapterId==='desktop-whisper-cpp')return this.transcribeNative(blob,options);
    const known=Object.values(STT_ADAPTERS).find(adapter=>adapter.id===adapterId);
    if(!known)throw new Error(`Unbekannter STT-Adapter: ${adapterId}`);
    if(!known.implemented)throw new Error(`STT-Adapter ${adapterId} ist für ${known.platforms.join('/')} vorbereitet, aber noch nicht implementiert.`);
    throw new Error(`STT-Adapter ${adapterId} unterstützt keine segmentbasierte Transkription.`);
  },
  validateModelFile(file){
    if(!file)return {ok:false,reason:'Keine Modelldatei gewählt.'};
    const name=file.name.toLowerCase();
    if(!name.endsWith('.bin')&&!name.endsWith('.gguf'))return {ok:false,reason:'Erwartet wird eine lokale .bin- oder .gguf-Modelldatei.'};
    if(file.size<10*1024*1024)return {ok:false,reason:'Die Datei ist ungewöhnlich klein und wahrscheinlich kein vollständiges Sprachmodell.'};
    return {ok:true,reason:''};
  }
};
