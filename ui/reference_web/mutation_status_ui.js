(()=>{'use strict';

const previousFetch=window.fetch.bind(window);
const STYLE_ID='provoware-mutation-status-css';
const inFlight=new Map();
const TRIGGER_MAX_AGE_MS=1600;
let lastTrigger=null;
let lastTriggerAt=0;

function ensureStyles(){
 if(document.getElementById(STYLE_ID))return;
 const link=document.createElement('link');
 link.id=STYLE_ID;link.rel='stylesheet';link.href='mutation_status_ui.css';
 document.head.appendChild(link);
}

function localApiMeta(input,init){
 const raw=typeof input==='string'?input:(input&&input.url)||'';
 try{
  const url=new URL(raw,location.href);
  if(url.origin!==location.origin||!url.pathname.startsWith('/api/'))return null;
  const method=String(init?.method||(input&&input.method)||'GET').toUpperCase();
  return {method,path:url.pathname,href:`${url.pathname}${url.search}`};
 }catch{return null}
}
function bodyDescriptor(body){
 if(body==null)return '';
 if(typeof body==='string')return `text:${body}`;
 if(body instanceof URLSearchParams)return `params:${body.toString()}`;
 if(typeof FormData!=='undefined'&&body instanceof FormData){
  const parts=[];
  for(const [key,value] of body.entries()){
   if(typeof value==='string')parts.push(`${key}=${value}`);
   else parts.push(`${key}=file:${value.name||''}:${value.size||0}:${value.lastModified||0}:${value.type||''}`);
  }
  return `form:${parts.join('&')}`;
 }
 if(typeof Blob!=='undefined'&&body instanceof Blob){
  return `blob:${body.name||''}:${body.size||0}:${body.lastModified||0}:${body.type||''}`;
 }
 if(body instanceof ArrayBuffer)return `buffer:${body.byteLength}`;
 if(ArrayBuffer.isView(body))return `view:${body.byteLength}`;
 return `other:${Object.prototype.toString.call(body)}`;
}
function requestKey(meta,init){
 return `${meta.method}|${meta.href}|${bodyDescriptor(init?.body)}`;
}
function mutationLocked(){
 return document.documentElement.dataset.mutationMode==='degraded';
}
function blockedMutation(meta){
 const payload={
  ok:false,
  code:'MUTATION_DEGRADED_MODE',
  message:'Schreibzugriffe sind nach einem internen Fehler vorsorglich gesperrt.',
  recovery_hint:'Lesen bleibt möglich. Bitte aktuellen Stand prüfen und das Tool anschließend über SCHNELLSTART.sh sauber neu starten.',
  degraded_mode:true
 };
 window.dispatchEvent(new CustomEvent('provoware:api-error',{detail:{payload,status:503,path:meta.path,method:meta.method}}));
 return Promise.resolve(new Response(JSON.stringify(payload),{
  status:503,
  headers:{'content-type':'application/json','x-provoware-client-block':'read-only'}
 }));
}
function rememberTrigger(trigger){
 if(!trigger)return;
 lastTrigger=trigger;
 lastTriggerAt=Date.now();
}
function triggerFromEvent(event){
 const target=event?.target;
 return target?.closest?.('button,input[type="submit"],input[type="button"]')||null;
}
document.addEventListener('click',event=>rememberTrigger(triggerFromEvent(event)),true);
document.addEventListener('submit',event=>rememberTrigger(event.submitter||triggerFromEvent(event)),true);
document.addEventListener('keydown',event=>{
 if(event.key==='Enter'&&event.target?.id==='quickInput')rememberTrigger(document.getElementById('quickSave'));
},true);

function currentTrigger(){
 const recent=lastTrigger&&lastTrigger.isConnected!==false&&Date.now()-lastTriggerAt<=TRIGGER_MAX_AGE_MS?lastTrigger:null;
 if(recent)return recent;
 return document.activeElement?.closest?.('button,input[type="submit"],input[type="button"]')||null;
}
function busyText(path){
 if(path.startsWith('/api/assets/'))return 'Wird importiert …';
 if(path==='/api/diagnostics/create')return 'Wird erstellt …';
 if(path.includes('/trash'))return 'Wird verschoben …';
 if(path.includes('/restore'))return 'Wird wiederhergestellt …';
 if(path.includes('/complete'))return 'Wird erledigt …';
 if(path==='/api/undo'||path==='/api/redo')return 'Wird ausgeführt …';
 if(path==='/api/audio/start')return 'Wird gestartet …';
 if(path==='/api/quick-note/open')return 'Wird geöffnet …';
 if(path==='/api/quick-note/share')return 'Wird vorbereitet …';
 return 'Wird gespeichert …';
}
function setBusy(trigger,path){
 if(!trigger||trigger.dataset?.mutationBusy==='1')return ()=>{};
 const owner=trigger.form||trigger;
 const original={
  text:trigger.textContent,
  disabled:Boolean(trigger.disabled),
  ariaDisabled:trigger.getAttribute?.('aria-disabled'),
  ariaBusy:owner.getAttribute?.('aria-busy')
 };
 trigger.dataset.mutationBusy='1';
 trigger.classList?.add('mutation-busy');
 trigger.setAttribute?.('aria-disabled','true');
 trigger.disabled=true;
 if('textContent'in trigger)trigger.textContent=busyText(path);
 owner.setAttribute?.('aria-busy','true');

 return ()=>{
  if(trigger.isConnected===false)return;
  if(original.text!=null&&'textContent'in trigger)trigger.textContent=original.text;
  trigger.disabled=original.disabled;
  if(original.ariaDisabled==null)trigger.removeAttribute?.('aria-disabled');
  else trigger.setAttribute?.('aria-disabled',original.ariaDisabled);
  if(original.ariaBusy==null)owner.removeAttribute?.('aria-busy');
  else owner.setAttribute?.('aria-busy',original.ariaBusy);
  trigger.classList?.remove('mutation-busy');
  delete trigger.dataset.mutationBusy;
 };
}
function responseSnapshot(response){
 const clone=response.clone();
 return clone.arrayBuffer().then(body=>({
  body,
  status:response.status,
  statusText:response.statusText,
  headers:[...response.headers.entries()]
 }));
}
function responseFromSnapshot(snapshot){
 const body=snapshot.body.slice(0);
 return new Response(body,{status:snapshot.status,statusText:snapshot.statusText,headers:snapshot.headers});
}

ensureStyles();

window.fetch=function(input,init){
 const meta=localApiMeta(input,init);
 if(!meta||meta.method!=='POST')return previousFetch(input,init);
 if(mutationLocked())return blockedMutation(meta);
 const key=requestKey(meta,init);
 const existing=inFlight.get(key);

 if(existing){
  const duplicateRelease=setBusy(currentTrigger(),meta.path);
  return existing.snapshot.then(responseFromSnapshot).finally(duplicateRelease);
 }

 const releaseBusy=setBusy(currentTrigger(),meta.path);
 const source=Promise.resolve().then(()=>previousFetch(input,init));
 const snapshot=source.then(responseSnapshot);
 snapshot.catch(()=>{});
 inFlight.set(key,{source,snapshot});

 return source.finally(()=>{
  if(inFlight.get(key)?.source===source)inFlight.delete(key);
  releaseBusy();
 });
};
})();