'use strict';

const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');

function loadSttCore({nativeAvailable=false,browserAvailable=false}={}){
  class LocalRecognition{}
  LocalRecognition.prototype.processLocally=false;
  const sandbox={
    window:{
      NAQYA:{
        nativeBridge:{
          available:()=>nativeAvailable,
          capabilities:async()=>({available:true,platform:'linux',whisper:true}),
          transcribe:async request=>({text:'ok',request})
        }
      },
      SpeechRecognition:browserAvailable?LocalRecognition:undefined,
      webkitSpeechRecognition:undefined
    },
    Blob,
    Uint8Array,
    btoa:value=>Buffer.from(value,'binary').toString('base64'),
    console
  };
  vm.createContext(sandbox);
  vm.runInContext(fs.readFileSync('services/stt-core.js','utf8'),sandbox,{filename:'services/stt-core.js'});
  return sandbox.window.NAQYA.stt;
}

(async()=>{
  const stt=loadSttCore({nativeAvailable:true,browserAvailable:true});

  assert.equal(stt.contract.format,'NAQYA-STT-PROVIDER');
  assert.equal(stt.contract.schemaVersion,1);
  assert.equal(stt.contract.resultSchemaVersion,1);
  assert.equal(stt.contract.engineFamily,'whisper.cpp');

  const providers=stt.providers();
  assert.equal(providers.browserOnDevice,true,'Legacy-Browserfähigkeit muss erhalten bleiben');
  assert.equal(providers.nativeWhisper,true,'Legacy-Desktopfähigkeit muss erhalten bleiben');

  assert.equal(providers.adapters.desktopWhisper.engine,'whisper.cpp');
  assert.equal(providers.adapters.desktopWhisper.transport,'tauri-sidecar');
  assert.equal(providers.adapters.desktopWhisper.available,true);
  assert.deepEqual(Array.from(providers.adapters.desktopWhisper.platforms),['linux','windows']);

  assert.equal(providers.adapters.androidWhisper.engine,'whisper.cpp');
  assert.equal(providers.adapters.androidWhisper.transport,'jni-ndk');
  assert.equal(providers.adapters.androidWhisper.implemented,false);
  assert.equal(providers.adapters.androidWhisper.available,false);

  assert.equal(providers.adapters.iosWhisper.engine,'whisper.cpp');
  assert.equal(providers.adapters.iosWhisper.transport,'swift-native');
  assert.equal(providers.adapters.iosWhisper.implemented,false);
  assert.equal(providers.adapters.iosWhisper.available,false);

  assert.equal(stt.adapterForPlatform('linux').id,'desktop-whisper-cpp');
  assert.equal(stt.adapterForPlatform('win32').id,'desktop-whisper-cpp');
  assert.equal(stt.adapterForPlatform('android').id,'android-whisper-cpp');
  assert.equal(stt.adapterForPlatform('iphone').id,'ios-whisper-cpp');
  assert.equal(stt.adapterForPlatform('ipad').id,'ios-whisper-cpp');
  assert.equal(stt.adapterForPlatform('browser').id,'browser-on-device');

  await assert.rejects(
    ()=>stt.transcribeWithAdapter('android-whisper-cpp',new Blob(['x']),{}),
    /noch nicht implementiert/
  );
  await assert.rejects(
    ()=>stt.transcribeWithAdapter('ios-whisper-cpp',new Blob(['x']),{}),
    /noch nicht implementiert/
  );
  await assert.rejects(
    ()=>stt.transcribeWithAdapter('does-not-exist',new Blob(['x']),{}),
    /Unbekannter STT-Adapter/
  );

  const result=await stt.transcribeWithAdapter('desktop-whisper-cpp',new Blob(['wav']),{modelPath:'/model.bin',language:'de'});
  assert.equal(result.text,'ok');
  assert.equal(result.request.modelPath,'/model.bin');
  assert.equal(result.request.language,'de');

  console.log('STT provider contract regression: OK');
})().catch(error=>{
  console.error(error);
  process.exitCode=1;
});
