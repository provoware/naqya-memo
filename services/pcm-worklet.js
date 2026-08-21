'use strict';

class NaqyaPcmCaptureProcessor extends AudioWorkletProcessor {
  process(inputs) {
    const input=inputs?.[0]?.[0];
    if(input?.length){
      const copy=new Float32Array(input.length);
      copy.set(input);
      this.port.postMessage(copy,[copy.buffer]);
    }
    return true;
  }
}

registerProcessor('naqya-pcm-capture',NaqyaPcmCaptureProcessor);
