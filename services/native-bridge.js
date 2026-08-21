'use strict';

window.NAQYA=window.NAQYA||{};

const TARGET_RATE=16000;
const MODEL_CHUNK_BYTES=1024*1024;
let statusCache=null;
let statusAt=0;

function invokeFn(){return window.__TAURI__?.core?.invoke||null}
function tauriAvailable(){return typeof invokeFn()==='function'}

async function status(force=false){
  if(!tauriAvailable())return {available:false,runtime:'PWA',models:[],modelDir:'',sampleRate:TARGET_RATE};
  if(!force&&statusCache&&Date.now()-statusAt<3000)return statusCache;
  try{
    statusCache=await invokeFn()('naqya_native_status');
    statusAt=Date.now();
    return statusCache;
  }catch(error){
    return {available:false,runtime:'Tauri-Brücke nicht erreichbar',models:[],modelDir:'',sampleRate:TARGET_RATE,error:String(error)};
  }
}

function modelFragment(profile){return ({schnell:'tiny',ausgewogen:'base',genau:'small',maximum:'medium'})[profile]||'base'}
async function chooseModel(profile='ausgewogen'){
  const s=await status(true),fragment=modelFragment(profile);
  const models=s.models||[];
  return models.find(m=>String(m.name).toLowerCase().includes(fragment))||models[0]||null;
}

function resampleLinear(input,fromRate,toRate=TARGET_RATE){
  if(!input?.length)return new Float32Array();
  if(fromRate===toRate)return input instanceof Float32Array?input:new Float32Array(input);
  const outLength=Math.max(1,Math.round(input.length*toRate/fromRate));
  const output=new Float32Array(outLength),ratio=fromRate/toRate;
  for(let i=0;i<outLength;i++){
    const pos=i*ratio,left=Math.floor(pos),right=Math.min(input.length-1,left+1),mix=pos-left;
    output[i]=input[left]*(1-mix)+input[right]*mix;
  }
  return output;
}

function concatFloat32(parts,total){
  const out=new Float32Array(total);let offset=0;
  for(const part of parts){out.set(part,offset);offset+=part.length}
  return out;
}

function bytesToBase64(bytes){
  const step=0x8000;let binary='';
  for(let i=0;i<bytes.length;i+=step)binary+=String.fromCharCode(...bytes.subarray(i,Math.min(bytes.length,i+step)));
  return btoa(binary);
}

async function transcribePcm(samples,{language='de',profile='ausgewogen',modelFile=null,threads=null,noContext=true,singleSegment=true}={}){
  const s=await status();
  if(!s.available)throw new Error('Die native Offline-Whisper-Runtime ist nicht verfügbar.');
  let model=modelFile?{name:modelFile}:await chooseModel(profile);
  if(!model)throw new Error(`Kein lokales Sprachmodell für das Profil „${profile}“ gefunden.`);
  const clean=samples instanceof Float32Array?samples:new Float32Array(samples||[]);
  if(!clean.length)throw new Error('Kein PCM-Audio für die Transkription vorhanden.');
  return invokeFn()('naqya_transcribe_pcm',{request:{samples:Array.from(clean),sampleRate:TARGET_RATE,modelFile:model.name,profile,language,threads,noContext,singleSegment}});
}

async function importModelFile(file,{expectedSha256=null,onProgress=null}={}){
  if(!file)throw new Error('Keine Modelldatei gewählt.');
  const s=await status(true);
  if(!s.available)throw new Error('Der native Modellimport ist nur in der Desktop-App verfügbar.');
  const begin=await invokeFn()('naqya_model_import_begin',{name:file.name,totalSize:file.size,expectedSha256});
  let sent=0;
  try{
    for(let offset=0;offset<file.size;offset+=MODEL_CHUNK_BYTES){
      const buffer=await file.slice(offset,Math.min(file.size,offset+MODEL_CHUNK_BYTES)).arrayBuffer();
      const chunk=new Uint8Array(buffer);
      sent=await invokeFn()('naqya_model_import_chunk',{id:begin.id,chunkBase64:bytesToBase64(chunk)});
      onProgress?.({sent,total:file.size,percent:Math.min(100,Math.round(sent/file.size*100))});
    }
    const model=await invokeFn()('naqya_model_import_finish',{id:begin.id});
    await status(true);
    return model;
  }catch(error){
    try{await invokeFn()('naqya_model_import_abort',{id:begin.id})}catch{}
    throw error;
  }
}

async function startPcmCapture(stream,{chunkMs=3000,onChunk}={}){
  if(!stream)throw new Error('Kein Mikrofonstream vorhanden.');
  const AudioCtx=window.AudioContext||window.webkitAudioContext;
  if(!AudioCtx)throw new Error('Web Audio API ist nicht verfügbar.');
  const context=new AudioCtx({latencyHint:'interactive'});
  const source=context.createMediaStreamSource(stream),sampleRate=context.sampleRate;
  const targetSamples=Math.max(1,Math.round(sampleRate*chunkMs/1000));
  let blocks=[],samplesBuffered=0,stopped=false,node=null,silentGain=context.createGain();
  silentGain.gain.value=0;
  silentGain.connect(context.destination);

  const consume=async flush=>{
    while(samplesBuffered>=targetSamples||(flush&&samplesBuffered>0)){
      const wanted=flush?Math.min(targetSamples,samplesBuffered):targetSamples;
      const selected=[];let count=0;
      while(blocks.length&&count<wanted){
        const first=blocks[0],need=wanted-count;
        if(first.length<=need){selected.push(first);blocks.shift();count+=first.length;samplesBuffered-=first.length}
        else{selected.push(first.subarray(0,need));blocks[0]=first.subarray(need);count+=need;samplesBuffered-=need}
      }
      const nativeRate=resampleLinear(concatFloat32(selected,count),sampleRate,TARGET_RATE);
      if(nativeRate.length)await onChunk?.(nativeRate);
      if(!flush)break;
    }
  };

  const accept=block=>{
    if(stopped||!block?.length)return;
    blocks.push(block instanceof Float32Array?block:new Float32Array(block));
    samplesBuffered+=block.length;
    if(samplesBuffered>=targetSamples)consume(false).catch(error=>console.error('PCM-Livecapture:',error));
  };

  if(context.audioWorklet?.addModule){
    await context.audioWorklet.addModule('./services/pcm-worklet.js');
    node=new AudioWorkletNode(context,'naqya-pcm-capture',{numberOfInputs:1,numberOfOutputs:1,outputChannelCount:[1]});
    node.port.onmessage=e=>accept(e.data);
    source.connect(node);node.connect(silentGain);
  }else{
    node=context.createScriptProcessor(4096,1,1);
    node.onaudioprocess=e=>{const input=e.inputBuffer.getChannelData(0),copy=new Float32Array(input.length);copy.set(input);accept(copy)};
    source.connect(node);node.connect(silentGain);
  }

  return {
    sampleRate,
    targetRate:TARGET_RATE,
    async stop(){
      if(stopped)return;
      stopped=true;
      try{source.disconnect()}catch{}
      try{node.disconnect()}catch{}
      if(node?.port)node.port.onmessage=null;
      if('onaudioprocess' in node)node.onaudioprocess=null;
      await consume(true);
      await context.close();
    }
  };
}

window.NAQYANativeSTT={
  isTauri:tauriAvailable,
  async init(){return status(true)},
  status,
  isReady(){return Boolean(statusCache?.available)},
  chooseModel,
  transcribePcm,
  importModelFile,
  startPcmCapture,
  resampleLinear,
  targetRate:TARGET_RATE
};
