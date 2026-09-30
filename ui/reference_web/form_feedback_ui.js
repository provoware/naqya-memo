(()=>{'use strict';

const STYLE_ID='provoware-form-feedback-css';
const FEEDBACK_CLASS='form-field-error';
const SUMMARY_CLASS='form-error-summary';

function ensureStyles(){
 if(document.getElementById(STYLE_ID))return;
 const link=document.createElement('link');
 link.id=STYLE_ID;link.rel='stylesheet';link.href='form_feedback_ui.css';
 document.head.appendChild(link);
}
function safeId(value){return String(value||'field').replace(/[^a-zA-Z0-9_-]+/g,'-')}
function fieldMessage(field){
 if(field.validity?.valueMissing)return 'Bitte dieses Pflichtfeld ausfüllen.';
 if(field.validity?.typeMismatch)return 'Bitte das Format prüfen.';
 if(field.validity?.tooLong)return `Bitte höchstens ${field.maxLength} Zeichen eingeben.`;
 if(field.validity?.rangeOverflow||field.validity?.rangeUnderflow)return 'Bitte einen Wert im erlaubten Bereich eingeben.';
 if(field.validity?.patternMismatch)return 'Bitte das erwartete Format verwenden.';
 return 'Bitte die Eingabe prüfen.';
}
function describedByTokens(field){return String(field.getAttribute('aria-describedby')||'').split(/\s+/).filter(Boolean)}
function clearField(field){
 if(!field)return;
 const id=field.dataset.feedbackId;
 if(id)document.getElementById(id)?.remove();
 const original=field.dataset.feedbackDescribedby;
 if(original!==undefined){
  if(original)field.setAttribute('aria-describedby',original);else field.removeAttribute('aria-describedby');
  delete field.dataset.feedbackDescribedby;
 }
 delete field.dataset.feedbackId;
 field.removeAttribute('aria-invalid');
 field.closest('label')?.classList.remove('field-has-error');
}
function clearForm(form){
 if(!form)return;
 form.querySelectorAll('[aria-invalid="true"]').forEach(clearField);
 form.querySelector(`.${SUMMARY_CLASS}`)?.remove();
}
function markField(field,message,code='CLIENT_VALIDATION'){
 if(!field)return false;
 clearField(field);
 const base=(field.id||field.name||'field');
 const id=`feedback-${safeId(formIdentity(field.form))}-${safeId(base)}`;
 const error=document.createElement('small');
 error.className=FEEDBACK_CLASS;error.id=id;error.setAttribute('role','alert');
 error.innerHTML=`<span aria-hidden="true">⚠</span><span>${escapeText(message)}</span><code>${escapeText(code)}</code>`;
 field.insertAdjacentElement('afterend',error);
 field.dataset.feedbackId=id;
 field.dataset.feedbackDescribedby=field.getAttribute('aria-describedby')||'';
 const tokens=describedByTokens(field).filter(x=>x!==id);tokens.push(id);
 field.setAttribute('aria-describedby',tokens.join(' '));
 field.setAttribute('aria-invalid','true');
 field.closest('label')?.classList.add('field-has-error');
 return true;
}
function formIdentity(form){return form?.id||'form'}
function escapeText(value){
 const span=document.createElement('span');span.textContent=String(value??'');return span.innerHTML;
}
function showFormSummary(form,payload){
 if(!form)return false;
 form.querySelector(`.${SUMMARY_CLASS}`)?.remove();
 const summary=document.createElement('div');
 summary.className=SUMMARY_CLASS;summary.tabIndex=-1;summary.setAttribute('role','alert');
 summary.innerHTML=`<strong><span aria-hidden="true">↻</span> Inhalt inzwischen geändert</strong><span>${escapeText(payload.message||'Der Inhalt wurde inzwischen geändert.')}</span><span><b>Lösung:</b> ${escapeText(payload.recovery_hint||'Bitte neu laden und die Änderung danach erneut prüfen.')}</span><code>${escapeText(payload.code||'REVISION_CONFLICT')}</code>`;
 form.insertAdjacentElement('afterbegin',summary);
 summary.focus({preventScroll:true});summary.scrollIntoView({block:'nearest'});
 return true;
}
function formForPath(path){
 if(path.startsWith('/api/memos'))return document.getElementById('memoForm');
 if(path.startsWith('/api/todos'))return document.getElementById('todoForm');
 if(path.startsWith('/api/events'))return document.getElementById('eventForm');
 if(path==='/api/calendar/colors')return document.getElementById('colorForm');
 if(path.startsWith('/api/assets'))return document.getElementById('assetForm');
 if(path.startsWith('/api/playlists'))return document.getElementById('playlistForm');
 if(path==='/api/settings')return document.getElementById('settingsForm');
 return document.activeElement?.form||null;
}
function firstNamed(form,names){
 for(const name of names){const field=form?.elements?.namedItem(name);if(field&&field instanceof HTMLElement)return field}
 return null;
}
function firstBlankColorTitle(form){
 if(!form)return null;
 return [...form.querySelectorAll('input[name^="title"]')].find(x=>!String(x.value||'').trim())||form.querySelector('input[name^="title"]');
}
function targetField(form,code,path){
 if(!form)return null;
 if(['MEMO_TITLE_REQUIRED','TODO_TITLE_REQUIRED','EVENT_TITLE_REQUIRED','TITLE_TOO_LONG'].includes(code))return firstNamed(form,['title']);
 if(code==='REMINDER_REQUIRES_DUE_DATE')return firstNamed(form,['due_at']);
 if(code==='EVENT_END_BEFORE_START')return firstNamed(form,['end_at']);
 if(code==='DATETIME_REQUIRED')return path.startsWith('/api/events')?firstNamed(form,['start_at']):firstNamed(form,['due_at','reminder_at']);
 if(code==='INVALID_DATETIME')return path.startsWith('/api/events')?firstNamed(form,['start_at','end_at','reminder_at']):firstNamed(form,['due_at','reminder_at']);
 if(code==='COLOR_TITLE_REQUIRED')return firstBlankColorTitle(form);
 if(['UPLOAD_EMPTY','UPLOAD_FILENAME_REQUIRED'].includes(code))return firstNamed(form,['file','source_path']);
 return null;
}
function focusField(field){
 field.focus({preventScroll:true});field.scrollIntoView({block:'center',behavior:'auto'});
}
function handleApiError(event){
 const detail=event.detail||{},payload=detail.payload||{};
 if(payload.degraded_mode)return;
 const form=formForPath(String(detail.path||''));
 if(!form)return;
 const code=String(payload.code||'');
 clearForm(form);
 if(code==='REVISION_CONFLICT'||code==='ASSET_REVISION_CONFLICT'){showFormSummary(form,payload);return}
 const field=targetField(form,code,String(detail.path||''));
 if(field&&markField(field,payload.message||'Bitte Eingabe prüfen.',code)){focusField(field)}
}

ensureStyles();

document.addEventListener('invalid',event=>{
 const field=event.target;
 if(!(field instanceof HTMLInputElement||field instanceof HTMLTextAreaElement||field instanceof HTMLSelectElement)||!field.form)return;
 event.preventDefault();
 markField(field,fieldMessage(field),'CLIENT_VALIDATION');
 if(!field.form.dataset.feedbackFocusPending){
  field.form.dataset.feedbackFocusPending='1';
  queueMicrotask(()=>{
   delete field.form.dataset.feedbackFocusPending;
   const first=field.form.querySelector('[aria-invalid="true"]');if(first)focusField(first);
  });
 }
},true);

document.addEventListener('input',event=>{
 const field=event.target;
 if(field?.getAttribute?.('aria-invalid')==='true'&&field.validity?.valid)clearField(field);
},true);
document.addEventListener('change',event=>{
 const field=event.target;
 if(field?.getAttribute?.('aria-invalid')==='true'&&field.validity?.valid)clearField(field);
},true);
document.addEventListener('submit',event=>clearForm(event.target),true);
window.addEventListener('provoware:api-error',handleApiError);
})();