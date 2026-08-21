'use strict';

window.NAQYA=window.NAQYA||{};

window.NAQYA.capabilities={
  async detect(){
    const SpeechCtor=window.SpeechRecognition||window.webkitSpeechRecognition;
    let onDeviceSpeech=false;
    if(SpeechCtor){
      try{onDeviceSpeech='processLocally' in SpeechCtor.prototype||'processLocally' in new SpeechCtor()}catch{}
    }
    let storage={quota:null,usage:null,persisted:null};
    try{
      if(navigator.storage?.estimate){
        const estimate=await navigator.storage.estimate();
        storage.quota=estimate.quota??null;
        storage.usage=estimate.usage??null;
      }
      if(navigator.storage?.persisted)storage.persisted=await navigator.storage.persisted();
    }catch{}
    let native={available:false,platform:'browser',whisper:false,logicalCpus:null,modelStore:null};
    try{
      if(window.NAQYA?.nativeBridge?.available?.())native=await window.NAQYA.nativeBridge.capabilities();
    }catch(error){native={...native,error:String(error?.message||error)}}
    return {
      indexedDB:'indexedDB' in window,
      serviceWorker:'serviceWorker' in navigator,
      mediaDevices:Boolean(navigator.mediaDevices?.getUserMedia),
      mediaRecorder:'MediaRecorder' in window,
      webAudio:Boolean(window.AudioContext||window.webkitAudioContext),
      speechRecognition:Boolean(SpeechCtor),
      onDeviceSpeech,
      nativeBridge:Boolean(native.available),
      nativeWhisper:Boolean(native.whisper),
      nativePlatform:native.platform||'browser',
      nativeLogicalCpus:native.logicalCpus??null,
      nativeModelStore:native.modelStore??null,
      nativeError:native.error||null,
      cryptoSubtle:Boolean(window.crypto?.subtle),
      fileReader:'FileReader' in window,
      online:navigator.onLine,
      storage
    };
  },
  humanBytes(value){
    if(value===null||value===undefined)return 'unbekannt';
    const units=['B','KiB','MiB','GiB','TiB'];
    let n=Number(value),i=0;
    while(n>=1024&&i<units.length-1){n/=1024;i++}
    return `${n>=10||i===0?n.toFixed(0):n.toFixed(1)} ${units[i]}`;
  }
};
