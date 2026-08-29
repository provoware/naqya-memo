(function(global){
'use strict';
const params=new URLSearchParams(global.location?.search||'');
const mode=params.get('acceptance')||global.__PROVOWARE_ACCEPTANCE_MODE__;
if(!mode||!global.ProvowareMobileApi?.active)return;
async function report(payload){
  try{await global.ProvowareMobileApi.acceptanceResult(payload)}catch(e){console.error('Acceptance result bridge failed',e)}
}
async function run(){
  await global.ProvowareMobileApi.ready;
  try{
    if(mode==='verify'){
      const memos=await global.ProvowareMobileApi.request('/api/memos');
      const assets=await global.ProvowareMobileApi.request('/api/assets/list');
      const marker=memos.find(x=>x.title==='__MOBILE_ACCEPTANCE__');
      const audio=assets.find(x=>x.kind==='audio'&&x.title==='Acceptance Audio');
      const state=await global.ProvowareMobileApi.request('/api/state');
      const ok=!!marker&&!!audio&&state.integrity==='ok';
      await report({status:ok?'PASS':'FAIL',mode:'verify',persistence:{memo:!!marker,audio:!!audio},counts:state.counts,integrity:state.integrity});
      return;
    }
    // run mode: exercise persistent core, native reminder and real microphone bridge.
    const old=await global.ProvowareMobileApi.request('/api/memos');
    for(const m of old.filter(x=>x.title==='__MOBILE_ACCEPTANCE__')){
      try{await global.ProvowareMobileApi.request(`/api/memos/${m.id}/trash`,'POST',{revision:m.revision})}catch(_){}
    }
    await global.ProvowareMobileApi.request('/api/memos','POST',{title:'__MOBILE_ACCEPTANCE__',body:'device acceptance marker',tags:['acceptance']});
    const now=Date.now();
    const reminder=new Date(now+3500).toISOString();
    const due=new Date(now+60_000).toISOString();
    await global.ProvowareMobileApi.request('/api/todos','POST',{title:'Acceptance Reminder',description:'native reminder acceptance',due_at:due,reminder_at:reminder,priority:'HOCH'});
    await global.ProvowareMobileApi.request('/api/events','POST',{title:'Acceptance Event',start_at:new Date(now+120_000).toISOString(),end_at:new Date(now+180_000).toISOString()});
    const cap=await global.ProvowareMobileApi.request('/api/audio/capability');
    if(!cap.available)throw new Error('NATIVE_AUDIO_CAPABILITY_FALSE');
    await global.ProvowareMobileApi.request('/api/audio/start','POST',{});
    await new Promise(r=>setTimeout(r,1300));
    const audio=await global.ProvowareMobileApi.request('/api/audio/stop','POST',{title:'Acceptance Audio'});
    const state=await global.ProvowareMobileApi.request('/api/state');
    const platform=await global.ProvowareMobileApi.nativeInfo();
    const ok=audio.size_bytes>0&&state.integrity==='ok'&&state.counts.memos>=1&&state.counts.todos>=1&&state.counts.events>=1;
    await report({status:ok?'PASS':'FAIL',mode:'run',audio_bytes:audio.size_bytes,audio_sha256:audio.sha256,counts:state.counts,integrity:state.integrity,reminder_at:reminder,platform});
  }catch(e){await report({status:'FAIL',mode,error:String(e?.message||e),stack:String(e?.stack||'').slice(0,1200)})}
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>setTimeout(run,350));else setTimeout(run,350);
})(typeof globalThis!=='undefined'?globalThis:this);
