(function(global){
'use strict';
const isAndroid=!!global.ProvowareAndroid;
const isIOS=!!(global.webkit&&global.webkit.messageHandlers&&global.webkit.messageHandlers.provoware);
const forced=/[?&]mobile-test=1(?:&|$)/.test(global.location?.search||'');
if(!isAndroid&&!isIOS&&!forced)return;

document.documentElement.classList.add('mobile-runtime');
global.__PROVOWARE_MOBILE__=true;

const pending=new Map();let seq=0;
global.ProvowareNativeCallbacks={
  resolve(id,payload){const p=pending.get(String(id));if(!p)return;pending.delete(String(id));p.resolve(payload)},
  reject(id,message){const p=pending.get(String(id));if(!p)return;pending.delete(String(id));p.reject(new Error(message||'NATIVE_BRIDGE_ERROR'))},
};
function callNative(action,payload={}){
  if(forced&&!isAndroid&&!isIOS){
    if(action==='platformInfo')return Promise.resolve({platform:'browser-mobile-test',native_bridge:false,device_tested:false});
    if(action==='shareText')return Promise.resolve({opened:false,test_mode:true});
    if(action==='scheduleReminder'||action==='cancelReminder')return Promise.resolve({scheduled:false,test_mode:true});
    if(action==='acceptanceResult'){console.log('ACCEPTANCE',payload);return Promise.resolve({logged:true,test_mode:true})}
    return Promise.reject(new Error('NATIVE_BRIDGE_UNAVAILABLE_IN_TEST_MODE'));
  }
  const id=String(++seq),msg={id,action,payload};
  return new Promise((resolve,reject)=>{
    const timer=setTimeout(()=>{if(pending.delete(id))reject(new Error('NATIVE_BRIDGE_TIMEOUT:'+action))},20000);
    pending.set(id,{resolve:(v)=>{clearTimeout(timer);resolve(v)},reject:(e)=>{clearTimeout(timer);reject(e)}});
    try{if(isAndroid)global.ProvowareAndroid.postMessage(JSON.stringify(msg));else global.webkit.messageHandlers.provoware.postMessage(msg)}
    catch(e){pending.delete(id);clearTimeout(timer);reject(e)}
  })
}
const native={
  async platformInfo(){if(global.__PROVOWARE_NATIVE_INFO__)return global.__PROVOWARE_NATIVE_INFO__;try{return await callNative('platformInfo')}catch(_){return {platform:isAndroid?'android':isIOS?'ios':'unknown',native_bridge:true}}},
  shareText:p=>callNative('shareText',p),scheduleReminder:p=>callNative('scheduleReminder',p),cancelReminder:p=>callNative('cancelReminder',p),
  audioStart:()=>callNative('audioStart',{}),audioStop:()=>callNative('audioStop',{}),
};
const storage=forced&&!('indexedDB' in global)?new global.ProvowareMobileCore.MemoryStore():new global.ProvowareMobileCore.IndexedDbStore();
const core=new global.ProvowareMobileCore.MobileCore(storage,native);
const baseReady=core.init();

function currentAcceptanceMode(){return new URLSearchParams(global.location?.search||'').get('acceptance')||global.__PROVOWARE_ACCEPTANCE_MODE__||null}
function authMarkup(profiles,lastId){
  const has=profiles.length>0;
  return `<div class="mobile-auth-overlay" role="dialog" aria-modal="true" aria-labelledby="mobileAuthTitle"><section class="mobile-auth-card">
    <div class="eyebrow">✦ OI - PROVOWARE - IO</div><h2 id="mobileAuthTitle">${has?'Profil öffnen':'Erstes Profil anlegen'}</h2>
    <p class="mobile-auth-help">Der 4-stellige PIN ist eine lokale Zugangssperre und <b>keine Verschlüsselung</b>.</p>
    <div id="authExisting" ${has?'':'hidden'}>
      <label>Profil<select id="authProfile">${profiles.map(p=>`<option value="${p.id}" ${p.id===lastId?'selected':''}>${String(p.name).replace(/[<&]/g,'')}</option>`).join('')}</select></label>
      <label>4-stelliger PIN<input id="authPin" type="password" inputmode="numeric" pattern="[0-9]{4}" maxlength="4" autocomplete="current-password"></label>
      <button class="primary" id="authUnlock">Profil öffnen</button><button id="authNew">Neues Profil</button>
    </div>
    <div id="authCreate" ${has?'hidden':''}>
      <label>Profilname<input id="authName" maxlength="80" autocomplete="nickname"></label>
      <label>PIN<input id="authCreatePin" type="password" inputmode="numeric" pattern="[0-9]{4}" maxlength="4" autocomplete="new-password"></label>
      <label>PIN wiederholen<input id="authCreatePin2" type="password" inputmode="numeric" pattern="[0-9]{4}" maxlength="4" autocomplete="new-password"></label>
      <button class="primary" id="authCreateBtn">Profil anlegen</button>${has?'<button id="authBack">Zurück</button>':''}
    </div><p id="authError" role="alert" class="auth-error"></p>
  </section></div>`;
}
async function interactiveAuth(){
  const profiles=await core.listProfiles(),lastId=await storage.get('meta','lastProfileId');
  return new Promise(resolve=>{
    const mount=()=>{
      document.body.insertAdjacentHTML('beforeend',authMarkup(profiles,lastId));
      const $=id=>document.getElementById(id),err=$('authError'),existing=$('authExisting'),create=$('authCreate');
      const done=()=>{document.querySelector('.mobile-auth-overlay')?.remove();resolve(core.profile)};
      const showError=e=>{err.textContent=String(e?.message||e)};
      if($('authUnlock'))$('authUnlock').onclick=async()=>{try{await core.verifyProfile($('authProfile').value,$('authPin').value);done()}catch(e){showError(e)}};
      if($('authNew'))$('authNew').onclick=()=>{existing.hidden=true;create.hidden=false;err.textContent='';$('authName')?.focus()};
      if($('authBack'))$('authBack').onclick=()=>{create.hidden=true;existing.hidden=false;err.textContent=''};
      if($('authCreateBtn'))$('authCreateBtn').onclick=async()=>{try{const a=$('authCreatePin').value,b=$('authCreatePin2').value;if(a!==b)throw new Error('PIN stimmt nicht überein.');await core.createProfile($('authName').value,a);done()}catch(e){showError(e)}};
      $('authPin')?.addEventListener('keydown',e=>{if(e.key==='Enter')$('authUnlock')?.click()});
    };
    if(document.body)mount();else document.addEventListener('DOMContentLoaded',mount,{once:true});
  })
}
async function ensureAuthenticated(){
  await baseReady;const mode=currentAcceptanceMode();
  if(mode==='run'||mode==='verify'){
    const profiles=await core.listProfiles();let p=profiles.find(x=>x.name==='Acceptance');
    if(!p)p=await core.createProfile('Acceptance','0000');else await core.verifyProfile(p.id,'0000');
    return p;
  }
  if(forced){const profiles=await core.listProfiles();let p=profiles.find(x=>x.name==='Browser-Test');if(!p)p=await core.createProfile('Browser-Test','0000');else await core.verifyProfile(p.id,'0000');return p}
  return interactiveAuth();
}
const authReady=ensureAuthenticated();

global.ProvowareMobileApi={
  active:true,core,ready:authReady,
  async request(path,method='GET',body){await authReady;return core.request(path,method,body)},
  async importFile(file,kind,title=''){await authReady;if(!file)throw new Error('DATEI_FEHLT');return core.importBlob(file,file.name,kind,title)},
  async assetUrl(assetId){await authReady;return core.assetUrl(assetId)},
  async shareText(title,text){await authReady;return native.shareText({title,text})},
  async nativeInfo(){return native.platformInfo()},
  async acceptanceResult(payload){return callNative('acceptanceResult',payload)},
  async lock(){await core.lockProfile();global.location.reload()},
};
})(typeof globalThis!=='undefined'?globalThis:this);
