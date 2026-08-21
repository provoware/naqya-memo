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
    let nativeStatus={available:false,models:[],modelDir:'',runtime:'PWA'};
    try{nativeStatus=await (window.NAQYANativeSTT?.status?.()||Promise.resolve(nativeStatus))}catch{}
    return {
      indexedDB:'indexedDB' in window,
      serviceWorker:'serviceWorker' in navigator,
      mediaDevices:Boolean(navigator.mediaDevices?.getUserMedia),
      mediaRecorder:'MediaRecorder' in window,
      audioWorklet:Boolean((window.AudioContext||window.webkitAudioContext)?.prototype?.audioWorklet)||'AudioWorkletNode' in window,
      speechRecognition:Boolean(SpeechCtor),
      onDeviceSpeech,
      nativeDesktop:Boolean(window.NAQYANativeSTT?.isTauri?.()),
      nativeWhisper:Boolean(nativeStatus?.available),
      nativeWhisperModels:nativeStatus?.models?.length||0,
      nativeWhisperRuntime:nativeStatus?.runtime||null,
      nativeWhisperVersion:nativeStatus?.whisperCppVersion||null,
      nativeModelDir:nativeStatus?.modelDir||null,
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
