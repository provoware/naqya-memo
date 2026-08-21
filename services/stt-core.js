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

window.NAQYA.stt={
  profiles:PROFILES,
  providers(){
    return {
      browserOnDevice:browserOnDeviceAvailable(),
      nativeWhisper:Boolean(window.NAQYANativeSTT?.transcribe||window.NAQYANativeSTT?.startLive)
    };
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
  async transcribeNative(blob,{language='de',profile='ausgewogen'}={}){
    if(!window.NAQYANativeSTT?.transcribe)throw new Error('Native whisper.cpp-Brücke ist nicht verfügbar.');
    return window.NAQYANativeSTT.transcribe(blob,{language,profile});
  },
  validateModelFile(file){
    if(!file)return {ok:false,reason:'Keine Modelldatei gewählt.'};
    const name=file.name.toLowerCase();
    if(!name.endsWith('.bin')&&!name.endsWith('.gguf'))return {ok:false,reason:'Erwartet wird eine lokale .bin- oder .gguf-Modelldatei.'};
    if(file.size<10*1024*1024)return {ok:false,reason:'Die Datei ist ungewöhnlich klein und wahrscheinlich kein vollständiges Sprachmodell.'};
    return {ok:true,reason:''};
  }
};
