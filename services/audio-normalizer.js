'use strict';

window.NAQYA=window.NAQYA||{};

const TARGET_RATE=16000;
const LIVE_SEGMENT_MS=4000;

function clampSample(v){return Math.max(-1,Math.min(1,v))}
function resampleLinear(input,inputRate,targetRate=TARGET_RATE){
  if(inputRate===targetRate)return input.slice();
  const ratio=inputRate/targetRate;
  const length=Math.max(1,Math.round(input.length/ratio));
  const out=new Float32Array(length);
  for(let i=0;i<length;i++){
    const pos=i*ratio,left=Math.floor(pos),right=Math.min(input.length-1,left+1),frac=pos-left;
    out[i]=(input[left]||0)*(1-frac)+(input[right]||0)*frac;
  }
  return out;
}
function wavBlob(samples,sampleRate=TARGET_RATE){
  const buffer=new ArrayBuffer(44+samples.length*2),view=new DataView(buffer);
  const text=(offset,value)=>{for(let i=0;i<value.length;i++)view.setUint8(offset+i,value.charCodeAt(i))};
  text(0,'RIFF');view.setUint32(4,36+samples.length*2,true);text(8,'WAVE');text(12,'fmt ');
  view.setUint32(16,16,true);view.setUint16(20,1,true);view.setUint16(22,1,true);view.setUint32(24,sampleRate,true);
  view.setUint32(28,sampleRate*2,true);view.setUint16(32,2,true);view.setUint16(34,16,true);text(36,'data');view.setUint32(40,samples.length*2,true);
  let offset=44;
  for(const sample of samples){const s=clampSample(sample);view.setInt16(offset,s<0?s*0x8000:s*0x7fff,true);offset+=2}
  return new Blob([buffer],{type:'audio/wav'});
}
function mergeChannels(audioBuffer){
  const length=audioBuffer.length,out=new Float32Array(length),channels=audioBuffer.numberOfChannels;
  for(let c=0;c<channels;c++){
    const data=audioBuffer.getChannelData(c);
    for(let i=0;i<length;i++)out[i]+=data[i]/channels;
  }
  return out;
}
async function normalizeBlobToWav(blob){
  const C=window.AudioContext||window.webkitAudioContext;
  if(!C)throw new Error('Web-Audio ist auf diesem Gerät nicht verfügbar.');
  const ctx=new C();
  try{
    const decoded=await ctx.decodeAudioData(await blob.arrayBuffer());
    const mono=mergeChannels(decoded),resampled=resampleLinear(mono,decoded.sampleRate,TARGET_RATE);
    return {blob:wavBlob(resampled,TARGET_RATE),sampleRate:TARGET_RATE,durationMs:Math.round(resampled.length/TARGET_RATE*1000)};
  }finally{await ctx.close().catch(()=>{})}
}

class LivePcmCapture{
  constructor(stream,{segmentMs=LIVE_SEGMENT_MS,onSegment=()=>{},onError=()=>{}}={}){
    this.stream=stream;this.segmentMs=segmentMs;this.onSegment=onSegment;this.onError=onError;this.ctx=null;this.source=null;this.processor=null;this.sink=null;this.parts=[];this.samples=0;this.seq=0;this.running=false;
  }
  async start(){
    if(this.running)return;
    const C=window.AudioContext||window.webkitAudioContext;
    if(!C)throw new Error('Web-Audio ist auf diesem Gerät nicht verfügbar.');
    this.ctx=new C();
    if(this.ctx.state==='suspended')await this.ctx.resume();
    this.source=this.ctx.createMediaStreamSource(this.stream);
    this.processor=this.ctx.createScriptProcessor(4096,1,1);
    this.sink=this.ctx.createGain();this.sink.gain.value=0;
    const segmentSamples=Math.round(this.ctx.sampleRate*this.segmentMs/1000);
    this.processor.onaudioprocess=e=>{
      if(!this.running)return;
      try{
        const input=e.inputBuffer.getChannelData(0),copy=new Float32Array(input.length);copy.set(input);
        this.parts.push(copy);this.samples+=copy.length;
        if(this.samples>=segmentSamples)this.flush();
      }catch(err){this.onError(err)}
    };
    this.source.connect(this.processor);this.processor.connect(this.sink);this.sink.connect(this.ctx.destination);this.running=true;
  }
  flush(){
    if(!this.samples||!this.ctx)return;
    const merged=new Float32Array(this.samples);let offset=0;
    for(const part of this.parts){merged.set(part,offset);offset+=part.length}
    this.parts=[];this.samples=0;this.seq+=1;
    const pcm=resampleLinear(merged,this.ctx.sampleRate,TARGET_RATE),blob=wavBlob(pcm,TARGET_RATE);
    Promise.resolve(this.onSegment({seq:this.seq,blob,sampleRate:TARGET_RATE,durationMs:Math.round(pcm.length/TARGET_RATE*1000)})).catch(this.onError);
  }
  async stop(){
    if(!this.running)return;
    this.flush();this.running=false;
    try{this.source?.disconnect();this.processor?.disconnect();this.sink?.disconnect()}catch{}
    if(this.processor)this.processor.onaudioprocess=null;
    await this.ctx?.close().catch(()=>{});this.ctx=null;
  }
}

window.NAQYA.audioNormalizer={TARGET_RATE,LIVE_SEGMENT_MS,resampleLinear,wavBlob,normalizeBlobToWav,LivePcmCapture};
