(()=>{'use strict';

const STYLE_ID='provoware-read-only-css';
const REASON='Nur-Lese-Modus: Schreibaktionen sind nach einem internen Fehler bis zum sauberen Neustart gesperrt.';
const MUTATION_SELECTOR=[
 'form button[type="submit"]',
 'form input[type="submit"]',
 '#quickSave','#quickOpen','#quickShare',
 '#undoBtn','#redoBtn',
 '#themeBtn','#fontDown','#fontUp',
 '#recordStart','#recordStop','#diagCreate','#docSave',
 '[data-trash-memo]','[data-trash-todo]','[data-trash-event]',
 '[data-restore]','[data-complete-todo]','[data-day]'
].join(',');
const originalState=new WeakMap();
let degraded=document.documentElement.dataset.mutationMode==='degraded';

function ensureStyles(){
 if(document.getElementById(STYLE_ID))return;
 const link=document.createElement('link');
 link.id=STYLE_ID;link.rel='stylesheet';link.href='read_only_ui.css';
 document.head.appendChild(link);
}
function mutationControls(scope=document){
 const controls=[];
 if(scope?.matches?.(MUTATION_SELECTOR))controls.push(scope);
 scope?.querySelectorAll?.(MUTATION_SELECTOR)?.forEach?.(el=>controls.push(el));
 return [...new Set(controls)];
}
function lockControl(control){
 if(!control||control.dataset?.readonlyLocked==='1')return;
 originalState.set(control,{
  disabled:Boolean(control.disabled),
  ariaDisabled:control.getAttribute?.('aria-disabled'),
  title:control.getAttribute?.('title')
 });
 control.dataset.readonlyLocked='1';
 control.disabled=true;
 control.setAttribute?.('aria-disabled','true');
 control.setAttribute?.('title',REASON);
}
function unlockControl(control){
 if(!control||control.dataset?.readonlyLocked!=='1')return;
 const original=originalState.get(control)||{disabled:false,ariaDisabled:null,title:null};
 control.disabled=Boolean(original.disabled);
 if(original.ariaDisabled==null)control.removeAttribute?.('aria-disabled');
 else control.setAttribute?.('aria-disabled',original.ariaDisabled);
 if(original.title==null)control.removeAttribute?.('title');
 else control.setAttribute?.('title',original.title);
 delete control.dataset.readonlyLocked;
 originalState.delete(control);
}
function ensureHint(){
 let hint=document.getElementById('readOnlyToolbarHint');
 if(!hint){
  hint=document.createElement('span');
  hint.id='readOnlyToolbarHint';
  hint.className='read-only-toolbar-hint';
  hint.setAttribute('role','status');
  hint.setAttribute('aria-live','polite');
  hint.innerHTML='<span aria-hidden="true">🔒</span><span><b>Nur Lesen:</b> Schreibaktionen sind bis zum sauberen Neustart gesperrt.</span>';
  document.querySelector('.workspace-toolbar')?.appendChild(hint);
 }
 hint.hidden=!degraded;
 return hint;
}
function applyMode(scope=document){
 document.documentElement.classList?.toggle('read-only-active',degraded);
 mutationControls(scope).forEach(control=>degraded?lockControl(control):unlockControl(control));
 ensureHint();
}
function setMode(value){
 degraded=Boolean(value);
 applyMode(document);
}
function focusSafetyNotice(){
 const notice=document.getElementById('statusNotice');
 if(!notice)return;
 if(!notice.hasAttribute?.('tabindex'))notice.setAttribute?.('tabindex','-1');
 notice.focus?.({preventScroll:true});
 notice.scrollIntoView?.({block:'nearest',behavior:'auto'});
}
function blockedControlFromEvent(event){
 return event?.target?.closest?.(MUTATION_SELECTOR)||event?.submitter||null;
}

ensureStyles();
applyMode(document);

window.addEventListener('provoware:mutation-mode',event=>{
 setMode(Boolean(event.detail?.degraded||event.detail?.mode==='DEGRADED'));
});

document.addEventListener('submit',event=>{
 if(!degraded)return;
 event.preventDefault();
 event.stopImmediatePropagation?.();
 focusSafetyNotice();
},true);

document.addEventListener('click',event=>{
 if(!degraded)return;
 const control=blockedControlFromEvent(event);
 if(!control||!control.matches?.(MUTATION_SELECTOR))return;
 event.preventDefault();
 event.stopImmediatePropagation?.();
 focusSafetyNotice();
},true);

document.addEventListener('keydown',event=>{
 if(!degraded||event.key!=='Enter'||event.target?.id!=='quickInput')return;
 event.preventDefault();
 event.stopImmediatePropagation?.();
 focusSafetyNotice();
},true);

const observer=new MutationObserver(records=>{
 if(!degraded)return;
 for(const record of records){
  for(const node of record.addedNodes||[]){
   if(node?.nodeType===1)applyMode(node);
  }
 }
});
observer.observe(document.documentElement,{childList:true,subtree:true});
})();