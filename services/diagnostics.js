'use strict';

(function(root){
  const NAQYA=root.NAQYA=root.NAQYA||{};
  const STORAGE_KEY='naqya-diagnostics-v1';
  const CONTRACT_URL='./diagnostics/DIAGNOSTICS_CONTRACT.json';
  const FALLBACK_MAX_EVENTS=200;
  const FALLBACK_DEDUPE_MS=5000;
  const retryCallbacks=new Map();
  let contract=null;
  let contractBinding={status:'loading',schema_version:null,event_schema_version:1,sha256:null};
  let sequence=0;
  let events=loadEvents();

  function safeStorage(){try{return root.localStorage||null}catch{return null}}
  function loadEvents(){
    try{
      const raw=safeStorage()?.getItem(STORAGE_KEY);if(!raw)return [];
      const parsed=JSON.parse(raw);return Array.isArray(parsed)?parsed.slice(-FALLBACK_MAX_EVENTS):[];
    }catch{return []}
  }
  function persist(){try{safeStorage()?.setItem(STORAGE_KEY,JSON.stringify(events))}catch{}}
  function maxEvents(){return Number(contract?.max_events)||FALLBACK_MAX_EVENTS}
  function dedupeMs(){return Number(contract?.dedupe_window_ms)||FALLBACK_DEDUPE_MS}
  function maxString(){return Number(contract?.privacy?.max_string_length)||240}
  function forbiddenKeys(){return new Set((contract?.privacy?.forbidden_keys||['audio','audioBase64','base64','blob','content','document','entryText','password','secret','text','token','transcript']).map(x=>String(x).toLowerCase()))}
  function codeMeta(code){return contract?.codes?.[code]||{severity:'error',category:'app',what:'Diagnoseereignis',options:['export-json','close']}}
  function now(){return new Date().toISOString()}
  function newId(){
    sequence+=1;
    const random=root.crypto?.randomUUID?.()||`${Date.now().toString(36)}-${sequence.toString(36)}`;
    return `NQ-${random}`;
  }
  function basename(path){const parts=String(path).replace(/\\/g,'/').split('/').filter(Boolean);return parts.at(-1)||'[pfad]'}
  function sanitizeString(value){
    let text=String(value);
    text=text.replace(/(?:[A-Za-z]:\\|\/home\/|\/Users\/)[^\s"']+/g,m=>`[pfad]/${basename(m)}`);
    if(text.length>maxString())text=`${text.slice(0,maxString())}…`;
    return text;
  }
  function sanitize(value,key='',depth=0){
    if(depth>4)return '[gekürzt]';
    const lower=String(key).toLowerCase();
    if(forbiddenKeys().has(lower)||/(?:base64|password|secret|token|transcript|content|entrytext)/i.test(lower))return '[REDACTED]';
    if(value===null||value===undefined||typeof value==='number'||typeof value==='boolean')return value??null;
    if(typeof value==='string')return sanitizeString(value);
    if(Array.isArray(value))return value.slice(0,20).map(v=>sanitize(v,'',depth+1));
    if(typeof value==='object'){
      if(typeof Blob!=='undefined'&&value instanceof Blob)return `[Blob ${value.size} Bytes]`;
      const out={};for(const [k,v] of Object.entries(value).slice(0,40))out[k]=sanitize(v,k,depth+1);return out;
    }
    return sanitizeString(value);
  }
  function productInfo(){
    let version='unbekannt';
    try{if(typeof VERSION!=='undefined')version=VERSION}catch{}
    return {name:'PROVOWARE – NAQYA Memo Tool 2026',version:NAQYA.release?.version||version,phase:NAQYA.release?.phase||null};
  }
  function bindingInfo(){return {...contractBinding}}
  function dedupeKey(code,where,result){return `${code}|${where||''}|${result||''}`}
  function record(code,input={}){
    try{
      const meta=codeMeta(code),stamp=now(),where=sanitizeString(input.where||'unbekannt'),result=sanitizeString(input.result||'siehe Diagnose');
      const key=dedupeKey(code,where,result),last=events.at(-1),lastMs=last?Date.parse(last.last_seen_at||last.when):0;
      if(last&&last.dedupe_key===key&&Date.now()-lastMs<=dedupeMs()){
        last.repeat_count=(last.repeat_count||1)+1;last.last_seen_at=stamp;persist();return {...last,deduplicated:true};
      }
      const eventId=newId(),event={
        schema_version:Number(contract?.event_schema_version)||1,
        event_id:eventId,
        correlation_id:input.correlation_id||eventId,
        parent_event_id:input.parent_event_id||null,
        code,
        severity:meta.severity||input.severity||'error',
        category:meta.category||input.category||'app',
        what:sanitizeString(input.what||meta.what||'Diagnoseereignis'),
        when:stamp,
        where,
        how:sanitizeString(input.how||'lokaler Programmablauf'),
        result,
        options:[...(input.options||meta.options||[])].filter(x=>contract?.safe_actions?.[x]||['close','settings','export-json','export-text','retry-once'].includes(x)),
        context:sanitize(input.context||{}),
        product:productInfo(),
        release_binding:bindingInfo(),
        repeat_count:1,
        last_seen_at:stamp,
        dedupe_key:key
      };
      events.push(event);events=events.slice(-maxEvents());persist();
      if(typeof input.retry==='function'&&event.options.includes('retry-once'))retryCallbacks.set(eventId,input.retry);
      if(input.dialog)showEvent(eventId);
      return {...event};
    }catch{return null}
  }
  function failure(code,error,input={}){
    const err=error instanceof Error?error:new Error(String(error||'Unbekannter Fehler'));
    return record(code,{...input,result:input.result||err.message,context:{...(input.context||{}),error_class:err.name,error_message:err.message}});
  }
  function snapshot(){return events.map(({dedupe_key,...event})=>JSON.parse(JSON.stringify(event)))}
  function exportPayload(){return {format:'NAQYA-DIAGNOSTICS',schema_version:1,exported_at:now(),contract:bindingInfo(),product:productInfo(),events:snapshot()}}
  function exportTextValue(){
    const lines=['NAQYA DIAGNOSEBERICHT',`Export: ${now()}`,`Produkt: ${productInfo().version}`,`Diagnosevertrag: ${contractBinding.sha256||'nicht gebunden'}`,''];
    for(const e of snapshot())lines.push(`Code: ${e.code}\nEreignis-ID: ${e.event_id}\nWas: ${e.what}\nWann: ${e.when}\nWo: ${e.where}\nWie: ${e.how}\nErgebnis: ${e.result}\nOptionen: ${e.options.join(', ')||'keine'}\nWiederholungen: ${e.repeat_count}\n`);
    return lines.join('\n');
  }
  function download(content,name,type){
    if(!root.document)return;
    const blob=new Blob([content],{type}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1500);
  }
  function exportJSON(){download(JSON.stringify(exportPayload(),null,2),`NAQYA_Diagnose_${new Date().toISOString().slice(0,10)}.json`,'application/json')}
  function exportText(){download(exportTextValue(),`NAQYA_Diagnose_${new Date().toISOString().slice(0,10)}.txt`,'text/plain')}
  function ensureDialog(){
    if(!root.document)return null;
    let dialog=document.querySelector('#naqyaDiagnosticDialog');if(dialog)return dialog;
    dialog=document.createElement('dialog');dialog.id='naqyaDiagnosticDialog';dialog.setAttribute('aria-labelledby','naqyaDiagnosticTitle');
    dialog.innerHTML='<div class="dialog-head"><div><small id="naqyaDiagnosticCode">NAQYA</small><h2 id="naqyaDiagnosticTitle">Diagnose</h2></div><button class="icon-button" data-diagnostic-action="close" aria-label="Schließen">✕</button></div><div class="help-content"><p id="naqyaDiagnosticResult"></p><p><strong>Was du jetzt tun kannst</strong></p><div id="naqyaDiagnosticActions" class="dialog-actions"></div><details><summary>Technische Kennung</summary><pre id="naqyaDiagnosticTechnical"></pre></details></div>';
    document.body.appendChild(dialog);
    dialog.addEventListener('click',async e=>{
      const button=e.target.closest?.('[data-diagnostic-action]');if(!button)return;
      const action=button.dataset.diagnosticAction,eventId=dialog.dataset.eventId||null;
      await executeAction(action,eventId);if(action==='close'&&dialog.open)dialog.close();
    });
    return dialog;
  }
  function actionLabel(action){return contract?.safe_actions?.[action]?.label||({'close':'Schließen','settings':'Einstellungen öffnen','export-json':'Diagnose als JSON speichern','export-text':'Diagnose lesbar speichern','retry-once':'Einmal erneut versuchen'}[action]||action)}
  function showEvent(eventId){
    const event=events.find(e=>e.event_id===eventId);if(!event)return;
    const dialog=ensureDialog();if(!dialog)return;
    dialog.dataset.eventId=event.event_id;
    dialog.querySelector('#naqyaDiagnosticCode').textContent=event.code;
    dialog.querySelector('#naqyaDiagnosticTitle').textContent=event.what;
    dialog.querySelector('#naqyaDiagnosticResult').textContent=`Ergebnis: ${event.result}`;
    dialog.querySelector('#naqyaDiagnosticTechnical').textContent=`Ereignis-ID: ${event.event_id}\nZeit: ${event.when}\nBereich: ${event.where}\nVertrag: ${event.release_binding?.sha256||'noch nicht gebunden'}`;
    const actions=dialog.querySelector('#naqyaDiagnosticActions');actions.innerHTML='';
    for(const action of [...new Set([...event.options,'close'])]){const b=document.createElement('button');b.type='button';b.className=action==='close'?'secondary':'primary';b.dataset.diagnosticAction=action;b.textContent=actionLabel(action);actions.appendChild(b)}
    if(!dialog.open)dialog.showModal();
  }
  function showOverview(){
    const latest=events.at(-1);if(latest){showEvent(latest.event_id);return}
    const event=record('NAQYA-APP-1101',{what:'Diagnose geöffnet',where:'diagnostics.showOverview',how:'Benutzeraktion',result:'Noch keine Fehlerereignisse gespeichert',options:['export-json','export-text','close']});if(event)showEvent(event.event_id);
  }
  async function executeAction(action,eventId){
    const parent=events.find(e=>e.event_id===eventId),correlation=parent?.correlation_id||eventId||null;
    record('NAQYA-APP-1101',{where:'diagnostics.executeAction',how:'Auswahldialog',result:`Aktion ${action} gewählt`,parent_event_id:eventId,correlation_id:correlation,context:{action}});
    if(action==='export-json'){exportJSON();return}
    if(action==='export-text'){exportText();return}
    if(action==='settings'){try{if(typeof setView==='function')setView('settings')}catch{}return}
    if(action==='retry-once'){
      const callback=retryCallbacks.get(eventId);retryCallbacks.delete(eventId);if(!callback)return;
      try{await callback()}catch(error){failure('NAQYA-APP-1102',error,{where:'diagnostics.executeAction',how:'Einmaliger manueller Wiederholungsversuch',parent_event_id:eventId,correlation_id:correlation,dialog:true})}
    }
  }
  function clear(){events=[];retryCallbacks.clear();persist()}
  async function initializeContract(){
    try{
      const response=await root.fetch(CONTRACT_URL,{cache:'no-store'});if(!response.ok)throw new Error(`HTTP ${response.status}`);
      const text=await response.text(),parsed=JSON.parse(text);if(parsed.schema_version!==1||parsed.event_schema_version!==1)throw new Error('Nicht unterstützter Diagnosevertrag');
      let sha256=null;if(root.crypto?.subtle){const digest=await root.crypto.subtle.digest('SHA-256',new TextEncoder().encode(text));sha256=[...new Uint8Array(digest)].map(b=>b.toString(16).padStart(2,'0')).join('')}
      contract=parsed;contractBinding={status:'bound',schema_version:parsed.schema_version,event_schema_version:parsed.event_schema_version,sha256};
      for(const event of events)if(event.release_binding?.status!=='bound')event.release_binding=bindingInfo();
      persist();
      return bindingInfo();
    }catch(error){contractBinding={status:'unavailable',schema_version:null,event_schema_version:1,sha256:null};return bindingInfo()}
  }
  function installUI(){
    if(!root.document)return;
    const host=document.querySelector('.sidebar-help');if(host&&!document.querySelector('#openDiagnostics')){const b=document.createElement('button');b.id='openDiagnostics';b.className='secondary full';b.type='button';b.textContent='🛠 Diagnose & Fehlercodes';b.addEventListener('click',showOverview);host.appendChild(b)}
  }
  if(root.addEventListener){
    root.addEventListener('error',event=>failure('NAQYA-APP-1002',event.error||event.message,{where:'window.error',how:'Globaler Fehlerfang',result:event.message||'Unerwarteter Programmfehler'}));
    root.addEventListener('unhandledrejection',event=>failure('NAQYA-APP-1003',event.reason,{where:'window.unhandledrejection',how:'Globaler Promise-Fehlerfang'}));
    root.addEventListener('DOMContentLoaded',installUI,{once:true});
  }

  NAQYA.diagnostics={record,failure,snapshot,exportPayload,exportTextValue,exportJSON,exportText,showEvent,showOverview,executeAction,clear,initializeContract,contractBinding:()=>bindingInfo(),sanitize};
  void initializeContract();
})(typeof window!=='undefined'?window:globalThis);
