(()=>{'use strict';
const nativeFetch=window.fetch.bind(window);
const recentErrors=[];
const MAX_ERROR_AGE_MS=1800;

function $(id){return document.getElementById(id)}
function localApiMeta(input,init){
 const raw=typeof input==='string'?input:(input&&input.url)||'';
 try{
  const url=new URL(raw,location.href);
  if(url.origin!==location.origin||!url.pathname.startsWith('/api/'))return null;
  const method=String(init?.method||(input&&input.method)||'GET').toUpperCase();
  return {path:url.pathname,method};
 }catch{return null}
}
function rememberError(payload,status,requestMeta=null){
 const safe={
  code:String(payload?.code||'REQUEST_FAILED'),
  message:String(payload?.message||'Die Aktion konnte nicht abgeschlossen werden.'),
  recovery_hint:String(payload?.recovery_hint||'Bitte Eingabe prüfen und den Schritt danach erneut ausführen.'),
  degraded_mode:Boolean(payload?.degraded_mode),status:Number(status)||0
 };
 recentErrors.push({payload:safe,at:Date.now()});
 while(recentErrors.length>8)recentErrors.shift();
 window.dispatchEvent(new CustomEvent('provoware:api-error',{detail:{payload:safe,status:safe.status,path:requestMeta?.path||'',method:requestMeta?.method||'GET'}}));
 if(safe.degraded_mode)renderError(safe);
}
function consumeRecentError(){
 const now=Date.now();
 while(recentErrors.length&&now-recentErrors[0].at>MAX_ERROR_AGE_MS)recentErrors.shift();
 return recentErrors.pop()?.payload||null;
}
function setMutationUi(degraded){
 document.documentElement.dataset.mutationMode=degraded?'degraded':'ready';
 const dataStatus=$('dataStatus'),chip=dataStatus?.closest('.status-chip');
 chip?.classList.toggle('degraded',degraded);
 if(degraded&&dataStatus)dataStatus.textContent='Nur Lesen';
 if(!degraded&&dataStatus?.textContent==='Nur Lesen')dataStatus.textContent='Prüfe …';
 window.dispatchEvent(new CustomEvent('provoware:mutation-mode',{detail:{degraded:Boolean(degraded),mode:degraded?'DEGRADED':'READY'}}));
}
function renderError(payload){
 const notice=$('statusNotice');if(!notice)return;
 const degraded=Boolean(payload?.degraded_mode||payload?.code==='MUTATION_DEGRADED_MODE');
 notice.dataset.level=degraded?'degraded':'error';
 $('statusNoticeIcon').textContent=degraded?'⛔':'⚠';
 $('statusNoticeKind').textContent=degraded?'SICHERER NUR-LESE-MODUS':'AKTION NICHT ABGESCHLOSSEN';
 $('statusNoticeMessage').textContent=payload?.message||'Die Aktion konnte nicht abgeschlossen werden.';
 $('statusNoticeRecovery').textContent=payload?.recovery_hint||'Bitte Eingabe prüfen und den Schritt danach erneut ausführen.';
 $('statusNoticeCode').textContent=`Fehlercode: ${payload?.code||'CLIENT_ERROR'}`;
 $('statusNoticeClose').hidden=degraded;
 notice.hidden=false;
 if(degraded)setMutationUi(true);
}
function fallbackFromToast(message){
 if(document.documentElement.dataset.mutationMode==='degraded'){
  return {code:'MUTATION_DEGRADED_MODE',message:'Schreibzugriffe sind nach einem internen Fehler vorsorglich gesperrt.',recovery_hint:'Lesen bleibt möglich. Bitte aktuellen Stand prüfen und das Tool anschließend über SCHNELLSTART.sh sauber neu starten.',degraded_mode:true};
 }
 return {code:'CLIENT_ERROR',message:message||'Die Aktion konnte nicht abgeschlossen werden.',recovery_hint:'Bitte Eingabe prüfen. Wenn der Fehler wiederkehrt, die Ansicht neu laden und das Tool über SCHNELLSTART.sh neu starten.',degraded_mode:false};
}

window.fetch=async function(...args){
 const requestMeta=localApiMeta(args[0],args[1]);
 if(!requestMeta)return nativeFetch(...args);
 try{
  const response=await nativeFetch(...args);
  const clone=response.clone();
  const ctype=(clone.headers.get('content-type')||'').toLowerCase();
  if(ctype.includes('application/json')){
   try{const payload=await clone.json();if(payload&&payload.ok===false)rememberError(payload,response.status,requestMeta)}catch{}
  }
  return response;
 }catch(error){
  rememberError({code:'NETWORK_ERROR',message:'Die Verbindung zum lokalen Tool wurde unterbrochen.',recovery_hint:'Bitte die Ansicht neu laden. Wenn der Fehler wiederkehrt, das Tool über SCHNELLSTART.sh neu starten.',degraded_mode:false},0,requestMeta);
  throw error;
 }
};

const toast=$('toast');
if(toast){
 const observer=new MutationObserver(()=>{
  if(toast.hidden||!toast.classList.contains('error'))return;
  const cached=consumeRecentError();
  const payload=cached?{...cached,message:toast.textContent.trim()||cached.message}:fallbackFromToast(toast.textContent.trim());
  renderError(payload);toast.hidden=true;
 });
 observer.observe(toast,{attributes:true,childList:true,subtree:true,characterData:true});
}

$('statusNoticeClose')?.addEventListener('click',()=>{
 const notice=$('statusNotice');
 if(notice?.dataset.level!=='degraded')notice.hidden=true;
});

import('./form_feedback_ui.js').catch(()=>{});
import('./mutation_status_ui.js').catch(()=>{});
import('./read_only_ui.js').catch(()=>{});

nativeFetch('/api/health',{headers:{Accept:'application/json'},cache:'no-store'})
 .then(r=>r.json())
 .then(payload=>{
  if(payload?.ok){
   const degraded=payload?.data?.mutation_mode==='DEGRADED';
   setMutationUi(degraded);
   if(degraded){
    renderError({code:'MUTATION_DEGRADED_MODE',message:'Schreibzugriffe sind nach einem internen Fehler vorsorglich gesperrt.',recovery_hint:'Lesen bleibt möglich. Bitte aktuellen Stand prüfen und das Tool anschließend über SCHNELLSTART.sh sauber neu starten.',degraded_mode:true});
   }
  }
 })
 .catch(()=>{});
})();