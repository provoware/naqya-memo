'use strict';

const VERSION='0.5.0';
const DB_NAME='naqya-memo-2026';
const DB_VERSION=2;
const AUDIO_SLICE_MS=3000;
const BACKUP_WARN_BYTES=100*1024*1024;
const ICONS={note:'📝',appointment:'📅',deadline:'⏰',task:'✓',text:'📄',document:'📎',audio:'🎙',dictation:'🎤'};
const LABELS={note:'Notiz',appointment:'Termin',deadline:'Frist',task:'Aufgabe',text:'Textdokument',document:'Dokument',audio:'Audio-Memo',dictation:'Diktat'};

const state={
  view:'dashboard',entries:[],projects:[],models:[],wizardStep:1,wizardType:'note',calendarDate:new Date(),
  activeRecorder:null,dictationRecognition:null,dictationFinal:'',dictationInterim:'',transcriptSaveTimer:null,
  capabilities:{},recoveredSessions:0,modelProfile:'ausgewogen'
};
let db;

const $=(s,r=document)=>r.querySelector(s);
const $$=(s,r=document)=>[...r.querySelectorAll(s)];
const uid=()=>crypto.randomUUID?.()||`${Date.now()}-${Math.random().toString(16).slice(2)}`;
const esc=s=>String(s??'').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
const fmt=d=>d?new Intl.DateTimeFormat('de-DE',{dateStyle:'medium',timeStyle:'short'}).format(new Date(d)):'—';
const fmtDate=d=>new Intl.DateTimeFormat('de-DE',{dateStyle:'medium'}).format(new Date(d));
const todayKey=()=>new Date().toISOString().slice(0,10);
const humanBytes=v=>window.NAQYA?.capabilities?.humanBytes(v)??`${v??0} B`;

function openDB(){
  return new Promise((resolve,reject)=>{
    const req=indexedDB.open(DB_NAME,DB_VERSION);
    req.onupgradeneeded=()=>{
      const d=req.result;
      if(!d.objectStoreNames.contains('entries')){
        const s=d.createObjectStore('entries',{keyPath:'id'});
        s.createIndex('createdAt','createdAt');s.createIndex('type','type');s.createIndex('date','date');s.createIndex('projectId','projectId');
      }
      if(!d.objectStoreNames.contains('projects'))d.createObjectStore('projects',{keyPath:'id'});
      if(!d.objectStoreNames.contains('files'))d.createObjectStore('files',{keyPath:'id'});
      if(!d.objectStoreNames.contains('settings'))d.createObjectStore('settings',{keyPath:'key'});
      if(!d.objectStoreNames.contains('audioSessions'))d.createObjectStore('audioSessions',{keyPath:'id'});
      if(!d.objectStoreNames.contains('audioSegments')){
        const seg=d.createObjectStore('audioSegments',{keyPath:'id'});
        seg.createIndex('sessionId','sessionId');seg.createIndex('createdAt','createdAt');
      }
      if(!d.objectStoreNames.contains('models'))d.createObjectStore('models',{keyPath:'id'});
    };
    req.onsuccess=()=>resolve(req.result);
    req.onerror=()=>reject(req.error);
  });
}
function store(name,mode='readonly'){return db.transaction(name,mode).objectStore(name)}
function all(name){return new Promise((res,rej)=>{const r=store(name).getAll();r.onsuccess=()=>res(r.result);r.onerror=()=>rej(r.error)})}
function put(name,value){return new Promise((res,rej)=>{const r=store(name,'readwrite').put(value);r.onsuccess=()=>res(value);r.onerror=()=>rej(r.error)})}
function get(name,key){return new Promise((res,rej)=>{const r=store(name).get(key);r.onsuccess=()=>res(r.result);r.onerror=()=>rej(r.error)})}
function del(name,key){return new Promise((res,rej)=>{const r=store(name,'readwrite').delete(key);r.onsuccess=()=>res();r.onerror=()=>rej(r.error)})}

async function logEvent(action,entry){
  const event={id:uid(),type:'chronology',title:action,text:entry?.title||'',createdAt:new Date().toISOString(),date:new Date().toISOString(),meta:{entryId:entry?.id||null,entryType:entry?.type||null},system:true};
  await put('entries',event);
}
async function refresh(){
  state.entries=(await all('entries')).sort((a,b)=>new Date(b.createdAt)-new Date(a.createdAt));
  state.projects=await all('projects');
  state.models=await all('models');
  render();
}

async function seed(){
  const settings=await get('settings','seeded');
  if(settings)return;
  const project={id:uid(),name:'Beispielprojekt',description:'Kann gelöscht oder umbenannt werden.',status:'aktiv',createdAt:new Date().toISOString()};
  await put('projects',project);
  await put('settings',{key:'seeded',value:true});
  await put('settings',{key:'theme',value:'hell'});
  await put('settings',{key:'scale',value:'standard'});
  await put('settings',{key:'modelProfile',value:'ausgewogen'});
  await put('entries',{id:uid(),type:'note',title:'Willkommen bei NAQYA',text:'Speichere schnell. Ordne später. Alles bleibt lokal.',createdAt:new Date().toISOString(),date:new Date().toISOString(),status:'aktiv',priority:'normal',projectId:'',category:'Start',tags:['hilfe'],deleted:false});
}

function visibleEntries(){return state.entries.filter(e=>!e.deleted&&!e.system)}
function chronologyEntries(){return state.entries.filter(e=>!e.deleted).sort((a,b)=>new Date(b.createdAt)-new Date(a.createdAt))}
function typeBadge(e){return `<span class="badge ${e.type}">${ICONS[e.type]||'•'} ${LABELS[e.type]||e.type}</span>`}
function entryRow(e){
  const tags=(e.tags||[]).slice(0,3).map(t=>`<span class="badge">#${esc(t)}</span>`).join('');
  const play=['audio','dictation'].includes(e.type)&&e.fileIds?.length?`<button class="secondary" data-play-entry="${esc(e.id)}" aria-label="${esc(e.title)} abspielen">▶</button>`:typeBadge(e);
  return `<article class="list-item"><div class="list-icon">${ICONS[e.type]||'•'}</div><div><strong>${esc(e.title||LABELS[e.type]||'Eintrag')}</strong><div><small>${fmt(e.date||e.createdAt)} · ${esc(e.category||'ohne Kategorie')}</small></div><div>${tags}</div></div><div>${play}</div></article>`;
}
function pageHead(title,sub,action=''){return `<div class="page-head"><div><h1>${title}</h1><p>${sub}</p></div>${action}</div>`}

function renderDashboard(){
  const entries=visibleEntries(),now=Date.now();
  const upcoming=entries.filter(e=>e.date&&new Date(e.date).getTime()>=now).sort((a,b)=>new Date(a.date)-new Date(b.date)).slice(0,5);
  const deadlines=entries.filter(e=>e.type==='deadline'&&e.status!=='erledigt');
  const today=entries.filter(e=>(e.date||'').slice(0,10)===todayKey());
  const recovery=state.recoveredSessions?`<section class="card span-12 recovery-banner"><span>🛟</span><div><strong>${state.recoveredSessions} Aufnahme${state.recoveredSessions===1?'':'n'} wiederhergestellt</strong><span>Vorhandene 3-Sekunden-Segmente wurden nach einer Unterbrechung zu sicheren Aufnahmen zusammengesetzt.</span></div></section>`:'';
  return `${pageHead('Guten Tag','Dein persönlicher Offline-Überblick','<button class="primary" data-quick="note">＋ Schnellnotiz</button>')}${recovery}<div class="grid dashboard-grid"><section class="card span-3 metric"><div><small class="muted">Heute</small><strong>${today.length}</strong><div>Einträge</div></div><span class="icon">☀️</span></section><section class="card span-3 metric"><div><small class="muted">Offene Fristen</small><strong>${deadlines.length}</strong><div>im Blick behalten</div></div><span class="icon">⏰</span></section><section class="card span-3 metric"><div><small class="muted">Dokumente</small><strong>${entries.filter(e=>['document','text'].includes(e.type)).length}</strong><div>lokal gespeichert</div></div><span class="icon">📄</span></section><section class="card span-3 metric"><div><small class="muted">Projekte</small><strong>${state.projects.length}</strong><div>Arbeitsbereiche</div></div><span class="icon">📁</span></section><section class="card span-8"><h2>Schnell erfassen</h2><div class="quick-grid"><button data-quick="note">📝<span>Notiz</span></button><button data-quick="appointment">📅<span>Termin</span></button><button data-quick="deadline">⏰<span>Frist</span></button><button data-quick="task">✓<span>Aufgabe</span></button><button data-view-go="audio">🎤<span>Diktieren</span></button><button data-view-go="audio">🎙<span>Audio</span></button><button data-quick="document">📷<span>Dokument</span></button><button data-view-go="projects">📁<span>Projekt</span></button></div></section><section class="card span-4"><h2>Nächste Termine & Fristen</h2><div class="list">${upcoming.length?upcoming.map(entryRow).join(''):'<div class="empty">Nichts geplant.</div>'}</div></section><section class="card span-12"><h2>Zuletzt gespeichert</h2><div class="list">${entries.slice(0,6).map(entryRow).join('')||'<div class="empty">Noch keine Einträge.</div>'}</div></section></div>`;
}
function renderToday(){const entries=visibleEntries().filter(e=>(e.date||'').slice(0,10)===todayKey());return `${pageHead('Heute',fmtDate(new Date()))}<section class="card"><div class="list">${entries.map(entryRow).join('')||'<div class="empty">Heute ist noch nichts eingetragen.</div>'}</div></section>`}
function renderCalendar(){
  const d=state.calendarDate,y=d.getFullYear(),m=d.getMonth(),first=new Date(y,m,1),start=new Date(y,m,1-((first.getDay()+6)%7)),days=[];
  for(let i=0;i<42;i++){
    const day=new Date(start);day.setDate(start.getDate()+i);const key=day.toISOString().slice(0,10);
    const ev=visibleEntries().filter(e=>(e.date||'').slice(0,10)===key).slice(0,3);
    days.push(`<div class="day ${day.getMonth()!==m?'other':''} ${key===todayKey()?'today':''}"><span class="day-num">${day.getDate()}</span>${ev.map(x=>`<span class="day-event" title="${esc(x.title)}">${ICONS[x.type]||'•'} ${esc(x.title)}</span>`).join('')}</div>`);
  }
  return `${pageHead('Kalender','Monatsübersicht',`<div class="calendar-controls"><button class="secondary" id="calPrev">←</button><strong>${new Intl.DateTimeFormat('de-DE',{month:'long',year:'numeric'}).format(d)}</strong><button class="secondary" id="calNext">→</button></div>`)}<section class="card"><div class="calendar"><div class="dow">Mo</div><div class="dow">Di</div><div class="dow">Mi</div><div class="dow">Do</div><div class="dow">Fr</div><div class="dow">Sa</div><div class="dow">So</div>${days.join('')}</div></section>`;
}
function renderDocuments(){const entries=visibleEntries().filter(e=>['document','text'].includes(e.type));return `${pageHead('Dokumente','Fotos, Dateien und Textdokumente','<button class="primary" data-quick="document">＋ Dokument</button>')}<section class="card"><div class="list">${entries.map(entryRow).join('')||'<div class="empty">Noch keine Dokumente gespeichert.</div>'}</div></section>`}
function renderProjects(){return `${pageHead('Projekte','Zusammengehörige Inhalte als digitale Akten','<button class="primary" id="newProject">＋ Projekt</button>')}<div class="grid project-grid">${state.projects.map(p=>{const count=visibleEntries().filter(e=>e.projectId===p.id).length;return `<section class="card project-card"><h2>${esc(p.name)}</h2><p class="muted">${esc(p.description||'')}</p><strong>${count}</strong> Einträge<br><small>${esc(p.status||'aktiv')}</small></section>`}).join('')||'<div class="card empty">Noch keine Projekte.</div>'}</div>`}
function renderChronology(){return `${pageHead('Chronologie','Was wann passiert ist')}<section class="card"><div class="list">${chronologyEntries().slice(0,100).map(entryRow).join('')||'<div class="empty">Noch keine Chronologie.</div>'}</div></section>`}
function renderSearch(){return `${pageHead('Suche','Titel, Texte, Kategorien, Projekte und Tags lokal durchsuchen')}<section class="card"><label>Suchbegriff<input id="searchInput" type="search" placeholder="z. B. Versicherung"></label><div id="searchResults" class="list" style="margin-top:16px"></div></section>`}

function sttProviderLabel(){
  const p=window.NAQYA?.stt?.providers?.()||{};
  if(p.nativeWhisper)return 'Native whisper.cpp-Brücke erkannt';
  if(p.browserOnDevice)return 'Lokale Browser-Spracherkennung bereit';
  return 'Noch keine lokale STT-Engine verfügbar';
}
function renderAudio(){
  const active=state.activeRecorder;
  const recording=Boolean(active?.recorder?.state==='recording');
  const dictating=recording&&active.kind==='dictation';
  const audioRecording=recording&&active.kind==='audio';
  const provider=sttProviderLabel();
  const recovery=state.recoveredSessions?`<section class="card span-12 recovery-banner"><span>🛟</span><div><strong>Recovery aktiv</strong><span>${state.recoveredSessions} unterbrochene Aufnahme${state.recoveredSessions===1?' wurde':'n wurden'} beim Start gerettet.</span></div></section>`:'';
  return `${pageHead('Audio & Offline-Live-Diktat','3-Sekunden-Segmente, Crash-Recovery und lokale STT-Provider')}${recovery}<div class="grid dashboard-grid"><section class="card span-6"><h2>Audio-Memo</h2><div class="audio-box"><div class="audio-session"><button id="recordAudio" class="record-button ${audioRecording?'active':''}" aria-label="${audioRecording?'Audioaufnahme stoppen':'Audioaufnahme starten'}">${audioRecording?'■':'●'}</button><strong id="recordStatus">${audioRecording?'Aufnahme läuft und wird segmentweise gesichert':'Bereit'}</strong><div class="status-row"><span class="status-chip ok">✓ lokal</span><span class="status-chip ok">✓ Recovery ${AUDIO_SLICE_MS/1000}s</span></div><p class="muted">Jedes Segment wird sofort in IndexedDB gesichert. Beim Stoppen entsteht daraus eine zusammenhängende Audiodatei.</p></div></div></section><section class="card span-6"><h2>Offline-Live-Diktat</h2><div class="audio-box"><button id="recordDictation" class="record-button ${dictating?'active':''}" aria-label="${dictating?'Diktat stoppen':'Offline-Diktat starten'}">${dictating?'■':'🎤'}</button><strong id="dictationStatus">${dictating?'Diktat läuft vollständig lokal':esc(provider)}</strong><div class="status-row"><span class="status-chip ${window.NAQYA?.stt?.providers?.().browserOnDevice?'ok':'warn'}">Browser On-Device</span><span class="status-chip ${window.NAQYA?.stt?.providers?.().nativeWhisper?'ok':'warn'}">whisper.cpp Bridge</span></div><div id="dictationText" class="dictation-text dictation-live" role="status" aria-live="polite">${esc((state.dictationFinal+state.dictationInterim).trim()||'Hier erscheint dein Live-Text. NAQYA startet niemals einen Cloud-Fallback.')}</div></div></section><section class="card span-12"><h2>Gespeicherte Aufnahmen</h2><div class="list">${visibleEntries().filter(e=>['audio','dictation'].includes(e.type)).map(entryRow).join('')||'<div class="empty">Noch keine Aufnahme.</div>'}</div></section></div>`;
}

function capabilityItem(label,value,okText='verfügbar',offText='nicht verfügbar'){
  return `<div class="capability"><strong>${esc(label)}</strong><span class="state ${value?'ok':'off'}">${value?'✓ '+esc(okText):'✕ '+esc(offText)}</span></div>`;
}
function renderModelManager(){
  const profiles=window.NAQYA?.stt?.profiles||{};
  const cards=Object.values(profiles).map(p=>`<button class="model-card ${state.modelProfile===p.id?'active':''}" data-model-profile="${p.id}"><strong>${esc(p.label)}</strong><span>~${p.approxMiB} MiB · ${esc(p.engineModel)}</span><small>${esc(p.description)}</small></button>`).join('');
  const installed=state.models.length?state.models.map(m=>`<div class="model-file"><div><strong>${esc(m.name)}</strong><div><small>${humanBytes(m.size)} · SHA-256 ${esc((m.sha256||'nicht berechnet').slice(0,16))}${m.sha256?'…':''}</small></div></div><button class="secondary" data-delete-model="${m.id}">Entfernen</button></div>`).join(''):'<div class="empty">Noch keine lokale Modelldatei importiert.</div>';
  return `<h2>Offline-Sprachmodell</h2><p class="muted">Das Profil steuert die geplante whisper.cpp-Qualitätsstufe. Browser-On-Device-STT verwaltet sein Modell selbst.</p><div class="model-grid">${cards}</div><div style="margin-top:14px"><label class="secondary" style="display:grid;place-items:center">Lokales Modell importieren (.bin/.gguf)<input id="modelFile" type="file" accept=".bin,.gguf" hidden></label></div><div class="list" style="margin-top:12px">${installed}</div><p class="backup-warning">Importierte Modelle bleiben lokal. Die native whisper.cpp-Laufzeit wird über den vorbereiteten Providervertrag angebunden; ein importiertes Modell allein aktiviert noch keine Engine.</p>`;
}
function renderSettings(){
  const theme=document.documentElement.dataset.theme,scale=document.documentElement.dataset.scale,c=state.capabilities||{},storage=c.storage||{};
  const quota=storage.quota||0,usage=storage.usage||0,pct=quota?Math.min(100,(usage/quota)*100):0;
  return `${pageHead('Einstellungen & Diagnose','Lesbarkeit, Offline-Fähigkeiten, Sprachmodelle und vollständige Datensicherung')}<div class="grid dashboard-grid"><section class="card span-6"><h2>Farbtheme</h2><div class="theme-grid">${[['hell','Klar & Hell'],['dunkel','Dunkel Kontrast'],['kontrast','Barrierefrei Kontrast'],['violett','Elegant Violett']].map(([v,l])=>`<button class="theme-button ${theme===v?'active':''}" data-theme-set="${v}">${l}</button>`).join('')}</div><h2 style="margin-top:22px">Schrift & Sichtbarkeit</h2><label>Profil<select id="scaleSelect"><option value="kompakt">Kompakt</option><option value="standard">Standard</option><option value="gross">Groß</option><option value="sehr-gross">Sehr groß</option><option value="maximal">Maximale Lesbarkeit</option></select></label><h2 style="margin-top:22px">Lokaler Speicher</h2><div class="storage-meter" aria-label="Speicherbelegung"><span style="width:${pct}%"></span></div><p><strong>${humanBytes(usage)}</strong> verwendet · ${humanBytes(quota)} verfügbar laut Browser</p></section><section class="card span-6"><h2>Vollbackup</h2><p>Sichert Einträge, Projekte, Einstellungen und alle Dokument-/Audiodateien in einem lokalen NAQYA-Paket. Dateien erhalten SHA-256-Prüfsummen, wenn die Plattform WebCrypto unterstützt.</p><div class="two-col"><button class="secondary" id="exportBackup">⬇ Vollbackup exportieren</button><label class="secondary" style="display:grid;place-items:center">⬆ Backup importieren<input id="importBackup" type="file" accept="application/json,.naqya-backup.json" hidden></label></div><p class="backup-warning">Sehr große Backups benötigen während des Exports zusätzlichen Arbeitsspeicher. Ab ${humanBytes(BACKUP_WARN_BYTES)} fragt NAQYA vorher nach.</p><h2 style="margin-top:22px">Fähigkeiten</h2><div class="capability-grid">${capabilityItem('IndexedDB',c.indexedDB)}${capabilityItem('Mikrofon',c.mediaDevices)}${capabilityItem('MediaRecorder',c.mediaRecorder)}${capabilityItem('Service Worker',c.serviceWorker)}${capabilityItem('Browser On-Device STT',c.onDeviceSpeech)}${capabilityItem('Native whisper.cpp',c.nativeWhisper)}${capabilityItem('SHA-256/WebCrypto',c.cryptoSubtle)}${capabilityItem('Persistenter Speicher',storage.persisted===true,'zugesagt',storage.persisted===false?'nicht zugesagt':'unbekannt')}</div></section><section class="card span-12">${renderModelManager()}</section><section class="card span-12"><h2>Version</h2><p><strong>PROVOWARE – NAQYA Memo Tool 2026 ${VERSION}</strong><br><span class="muted">AUDIO & OFFLINE-STT CORE</span></p></section></div>`;
}

function render(){
  const v=$('#view');if(!v)return;
  const map={dashboard:renderDashboard,today:renderToday,calendar:renderCalendar,documents:renderDocuments,projects:renderProjects,audio:renderAudio,chronology:renderChronology,search:renderSearch,settings:renderSettings};
  v.innerHTML=(map[state.view]||renderDashboard)();
  $$('.nav-item').forEach(b=>b.classList.toggle('active',b.dataset.view===state.view));
  wireDynamic();
}
function setView(v){state.view=v;render();$('#hauptinhalt').focus();if(innerWidth<760)$('#sidebar').classList.remove('open')}

function wireDynamic(){
  $$('[data-quick]').forEach(b=>b.onclick=()=>openWizard(b.dataset.quick));
  $$('[data-view-go]').forEach(b=>b.onclick=()=>setView(b.dataset.viewGo));
  $$('[data-play-entry]').forEach(b=>b.onclick=()=>playEntry(b.dataset.playEntry));
  $('#calPrev')?.addEventListener('click',()=>{state.calendarDate=new Date(state.calendarDate.getFullYear(),state.calendarDate.getMonth()-1,1);render()});
  $('#calNext')?.addEventListener('click',()=>{state.calendarDate=new Date(state.calendarDate.getFullYear(),state.calendarDate.getMonth()+1,1);render()});
  $('#newProject')?.addEventListener('click',newProject);
  $('#recordAudio')?.addEventListener('click',toggleAudio);
  $('#recordDictation')?.addEventListener('click',toggleDictation);
  $('#searchInput')?.addEventListener('input',e=>runSearch(e.target.value));
  $$('[data-theme-set]').forEach(b=>b.onclick=()=>setTheme(b.dataset.themeSet));
  $$('[data-model-profile]').forEach(b=>b.onclick=()=>setModelProfile(b.dataset.modelProfile));
  $$('[data-delete-model]').forEach(b=>b.onclick=()=>deleteModel(b.dataset.deleteModel));
  const scale=$('#scaleSelect');if(scale){scale.value=document.documentElement.dataset.scale;scale.onchange=()=>setScale(scale.value)}
  $('#modelFile')?.addEventListener('change',installModelFile);
  $('#exportBackup')?.addEventListener('click',exportBackup);
  $('#importBackup')?.addEventListener('change',importBackup);
}

function openWizard(type='note'){state.wizardStep=1;state.wizardType=type;$('#wizardForm').reset();$$('#typeGrid button').forEach(b=>b.classList.toggle('selected',b.dataset.type===type));syncWizard();loadProjectOptions();$('#wizard').showModal()}
function syncWizard(){$$('.wizard-step').forEach(x=>x.hidden=Number(x.dataset.step)!==state.wizardStep);$('#wizardStepLabel').textContent=`Schritt ${state.wizardStep} von 3`;$('#wizardProgress').style.width=`${state.wizardStep/3*100}%`;$('#wizardBack').disabled=state.wizardStep===1;$('#wizardNext').hidden=state.wizardStep===3;$('#wizardSave').hidden=state.wizardStep!==3;$('#fileLabel').hidden=state.wizardType!=='document';$('#wizardMessage').textContent=''}
function loadProjectOptions(){const s=$('#entryProject');s.innerHTML='<option value="">Noch keinem Projekt zuordnen</option>'+state.projects.map(p=>`<option value="${p.id}">${esc(p.name)}</option>`).join('')}
async function saveWizard(){
  const file=$('#entryFile').files?.[0];let fileId=null;
  if(file){fileId=uid();await put('files',{id:fileId,name:file.name,type:file.type,size:file.size,blob:file,createdAt:new Date().toISOString()})}
  const entry={id:uid(),type:state.wizardType,title:$('#entryTitle').value.trim()||LABELS[state.wizardType],text:$('#entryText').value.trim(),date:$('#entryDate').value?new Date($('#entryDate').value).toISOString():new Date().toISOString(),createdAt:new Date().toISOString(),updatedAt:new Date().toISOString(),priority:$('#entryPriority').value,status:'aktiv',projectId:$('#entryProject').value,category:$('#entryCategory').value.trim(),tags:$('#entryTags').value.split(',').map(x=>x.trim()).filter(Boolean),fileIds:fileId?[fileId]:[],deleted:false};
  await put('entries',entry);await logEvent('Eintrag erstellt',entry);$('#wizard').close();await refresh();
}
async function newProject(){const name=prompt('Projektname:');if(!name?.trim())return;const description=prompt('Kurze Beschreibung (optional):')||'';const p={id:uid(),name:name.trim(),description,status:'aktiv',createdAt:new Date().toISOString()};await put('projects',p);await logEvent('Projekt erstellt',{...p,type:'project',title:p.name});await refresh()}

function preferredAudioMime(){
  if(!window.MediaRecorder?.isTypeSupported)return '';
  return ['audio/webm;codecs=opus','audio/ogg;codecs=opus','audio/webm'].find(x=>MediaRecorder.isTypeSupported(x))||'';
}
async function getAudioStream(){
  if(!navigator.mediaDevices?.getUserMedia)throw new Error('Dieses Gerät stellt keinen Mikrofonzugriff bereit.');
  return navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true,noiseSuppression:true,channelCount:1}});
}
async function segmentsForSession(sessionId){return (await all('audioSegments')).filter(s=>s.sessionId===sessionId).sort((a,b)=>a.seq-b.seq)}
async function deleteSegments(sessionId){const segments=await segmentsForSession(sessionId);for(const s of segments)await del('audioSegments',s.id)}
async function updateSession(sessionId,patch){const current=await get('audioSessions',sessionId);if(current)await put('audioSessions',{...current,...patch,updatedAt:new Date().toISOString()})}

async function startSegmentedRecorder(kind){
  if(state.activeRecorder)throw new Error('Es läuft bereits eine Aufnahme.');
  const stream=await getAudioStream(),mimeType=preferredAudioMime();
  const recorder=mimeType?new MediaRecorder(stream,{mimeType}):new MediaRecorder(stream);
  const sessionId=uid(),createdAt=new Date().toISOString();
  await put('audioSessions',{id:sessionId,kind,status:'recording',createdAt,updatedAt:createdAt,mimeType:recorder.mimeType||mimeType||'audio/webm',segmentMs:AUDIO_SLICE_MS,segments:0,transcriptDraft:''});
  const active={sessionId,kind,stream,recorder,seq:0,pendingWrites:[],startedAt:Date.now(),pendingTranscript:''};
  state.activeRecorder=active;
  recorder.ondataavailable=e=>{
    if(!e.data?.size)return;
    active.seq+=1;
    const segment={id:`${sessionId}:${String(active.seq).padStart(8,'0')}`,sessionId,seq:active.seq,createdAt:new Date().toISOString(),size:e.data.size,type:e.data.type||recorder.mimeType,blob:e.data};
    const write=put('audioSegments',segment).then(()=>updateSession(sessionId,{segments:active.seq,lastSegmentAt:segment.createdAt}));
    active.pendingWrites.push(write);
    write.finally(()=>{const i=active.pendingWrites.indexOf(write);if(i>=0)active.pendingWrites.splice(i,1)});
  };
  recorder.onerror=e=>console.error('MediaRecorder',e.error||e);
  recorder.onstop=async()=>{
    await Promise.allSettled([...active.pendingWrites]);
    try{await finalizeSession(sessionId,active.pendingTranscript||'')}catch(err){console.error('Audio finalisieren:',err);await updateSession(sessionId,{status:'recoverable',error:String(err.message||err)})}
    stream.getTracks().forEach(t=>t.stop());
    if(state.activeRecorder?.sessionId===sessionId)state.activeRecorder=null;
    state.dictationRecognition=null;
    state.dictationFinal='';state.dictationInterim='';
    await refresh();
  };
  recorder.start(AUDIO_SLICE_MS);
  return active;
}
async function stopActiveRecorder(transcript=''){
  const active=state.activeRecorder;if(!active)return;
  active.pendingTranscript=transcript;
  await updateSession(active.sessionId,{status:'stopping',transcriptDraft:transcript});
  if(active.recorder.state==='recording')active.recorder.stop();
}
async function finalizeSession(sessionId,transcript=''){
  const session=await get('audioSessions',sessionId);if(!session)return;
  const segments=await segmentsForSession(sessionId);if(!segments.length){await updateSession(sessionId,{status:'empty'});return}
  const mimeType=session.mimeType||segments[0].type||'audio/webm';
  const blob=new Blob(segments.map(s=>s.blob),{type:mimeType});
  const fileId=uid();
  await put('files',{id:fileId,name:`${session.kind==='dictation'?'diktat':'audio'}-${Date.now()}.${mimeType.includes('ogg')?'ogg':'webm'}`,type:mimeType,size:blob.size,blob,createdAt:new Date().toISOString(),sourceSessionId:sessionId});
  const cleanText=(transcript||session.transcriptDraft||'').trim();
  const entry={id:uid(),type:session.kind,title:session.kind==='dictation'?(cleanText.slice(0,70)||'Diktat'):`Audio-Memo ${new Intl.DateTimeFormat('de-DE',{dateStyle:'short',timeStyle:'short'}).format(new Date())}`,text:cleanText,date:new Date().toISOString(),createdAt:new Date().toISOString(),status:'aktiv',priority:'normal',tags:session.kind==='dictation'?['diktat']:[],fileIds:[fileId],audioSessionId:sessionId,deleted:false};
  await put('entries',entry);await logEvent(session.kind==='dictation'?'Diktat gespeichert':'Audio-Memo gespeichert',entry);
  await deleteSegments(sessionId);
  await updateSession(sessionId,{status:'finalized',entryId:entry.id,fileId,bytes:blob.size,finalizedAt:new Date().toISOString(),transcriptDraft:cleanText});
}

async function recoverInterruptedAudioSessions(){
  const sessions=await all('audioSessions');let recovered=0;
  for(const session of sessions.filter(s=>['recording','stopping','recoverable'].includes(s.status))){
    const segments=await segmentsForSession(session.id);
    if(!segments.length){await updateSession(session.id,{status:'empty-recovered'});continue}
    try{
      const mimeType=session.mimeType||segments[0].type||'audio/webm',blob=new Blob(segments.map(s=>s.blob),{type:mimeType}),fileId=uid();
      await put('files',{id:fileId,name:`wiederhergestellt-${Date.now()}.${mimeType.includes('ogg')?'ogg':'webm'}`,type:mimeType,size:blob.size,blob,createdAt:new Date().toISOString(),sourceSessionId:session.id,recovered:true});
      const entry={id:uid(),type:session.kind||'audio',title:`Wiederhergestellte ${session.kind==='dictation'?'Diktat-':'Audio-'}Aufnahme`,text:(session.transcriptDraft||'').trim(),date:session.createdAt||new Date().toISOString(),createdAt:new Date().toISOString(),status:'wiederhergestellt',priority:'normal',tags:['wiederhergestellt'],fileIds:[fileId],audioSessionId:session.id,deleted:false};
      await put('entries',entry);await logEvent('Unterbrochene Aufnahme wiederhergestellt',entry);await deleteSegments(session.id);await updateSession(session.id,{status:'recovered',entryId:entry.id,fileId,recoveredAt:new Date().toISOString(),bytes:blob.size});recovered++;
    }catch(err){console.error('Recovery:',err);await updateSession(session.id,{status:'recoverable',error:String(err.message||err)})}
  }
  state.recoveredSessions=recovered;
}

async function toggleAudio(){
  const status=$('#recordStatus');
  if(state.activeRecorder?.kind==='audio'){status&&(status.textContent='Finalisiere Aufnahme …');await stopActiveRecorder('');return}
  if(state.activeRecorder){status&&(status.textContent='Bitte zuerst die laufende Aufnahme beenden.');return}
  try{await startSegmentedRecorder('audio');render()}catch(e){status&&(status.textContent=`Mikrofon nicht verfügbar: ${e.message}`)}
}
function scheduleTranscriptDraft(){
  clearTimeout(state.transcriptSaveTimer);
  state.transcriptSaveTimer=setTimeout(async()=>{
    const active=state.activeRecorder;if(!active||active.kind!=='dictation')return;
    await updateSession(active.sessionId,{transcriptDraft:(state.dictationFinal+state.dictationInterim).trim()});
  },500);
}
async function toggleDictation(){
  const status=$('#dictationStatus');
  if(state.activeRecorder?.kind==='dictation'){
    const text=(state.dictationFinal+state.dictationInterim).trim();
    try{state.dictationRecognition?.stop()}catch{}
    state.dictationRecognition=null;
    await stopActiveRecorder(text);return;
  }
  if(state.activeRecorder){status&&(status.textContent='Bitte zuerst die laufende Audioaufnahme beenden.');return}
  const providers=window.NAQYA?.stt?.providers?.()||{};
  if(!providers.browserOnDevice){status&&(status.textContent=providers.nativeWhisper?'Native whisper.cpp-Brücke erkannt; Live-Streaming wird mit der Desktop-Hülle aktiviert.':'Keine lokale STT-Engine verfügbar. Kein Cloud-Fallback gestartet.');return}
  try{
    const active=await startSegmentedRecorder('dictation');
    const r=window.NAQYA.stt.createBrowserRecognition('de-DE');
    state.dictationFinal='';state.dictationInterim='';state.dictationRecognition=r;
    r.onresult=e=>{
      let interim='';
      for(let i=e.resultIndex;i<e.results.length;i++){
        const t=e.results[i][0].transcript;
        if(e.results[i].isFinal)state.dictationFinal+=t+' ';else interim+=t;
      }
      state.dictationInterim=interim;
      const target=$('#dictationText');if(target)target.textContent=(state.dictationFinal+interim).trim();
      scheduleTranscriptDraft();
    };
    r.onerror=e=>{const s=$('#dictationStatus');if(s)s.textContent=`Lokale Erkennung: ${e.error}. Kein Cloud-Fallback.`};
    r.onend=async()=>{
      if(state.dictationRecognition===r)state.dictationRecognition=null;
      if(state.activeRecorder?.sessionId===active.sessionId&&state.activeRecorder.recorder.state==='recording')await stopActiveRecorder((state.dictationFinal+state.dictationInterim).trim());
    };
    r.start();render();
  }catch(e){status&&(status.textContent=`Lokales Diktat konnte nicht starten: ${e.message}`)}
}
async function playEntry(entryId){
  const entry=state.entries.find(e=>e.id===entryId);if(!entry?.fileIds?.length)return;
  const file=await get('files',entry.fileIds[0]);if(!file?.blob)return;
  const url=URL.createObjectURL(file.blob),audio=new Audio(url);
  audio.onended=()=>URL.revokeObjectURL(url);audio.onerror=()=>URL.revokeObjectURL(url);await audio.play();
}

function runSearch(q){const out=$('#searchResults');if(!out)return;const s=q.trim().toLowerCase();if(!s){out.innerHTML='<div class="empty">Suchbegriff eingeben.</div>';return}const projectMap=new Map(state.projects.map(p=>[p.id,p.name]));const found=visibleEntries().filter(e=>[e.title,e.text,e.category,(e.tags||[]).join(' '),projectMap.get(e.projectId)||''].join(' ').toLowerCase().includes(s));out.innerHTML=found.map(entryRow).join('')||'<div class="empty">Keine Treffer.</div>';$$('[data-play-entry]',out).forEach(b=>b.onclick=()=>playEntry(b.dataset.playEntry))}

async function setTheme(theme){document.documentElement.dataset.theme=theme;await put('settings',{key:'theme',value:theme});render()}
async function setScale(scale){document.documentElement.dataset.scale=scale;await put('settings',{key:'scale',value:scale})}
async function setModelProfile(profile){if(!window.NAQYA?.stt?.profiles?.[profile])return;state.modelProfile=profile;await put('settings',{key:'modelProfile',value:profile});render()}
async function loadSettings(){const theme=await get('settings','theme'),scale=await get('settings','scale'),modelProfile=await get('settings','modelProfile');document.documentElement.dataset.theme=theme?.value||'hell';document.documentElement.dataset.scale=scale?.value||'standard';state.modelProfile=modelProfile?.value||'ausgewogen'}

async function sha256Blob(blob){
  if(!crypto.subtle)return null;
  const digest=await crypto.subtle.digest('SHA-256',await blob.arrayBuffer());
  return [...new Uint8Array(digest)].map(b=>b.toString(16).padStart(2,'0')).join('');
}
function arrayBufferToBase64(buffer){const bytes=new Uint8Array(buffer),chunk=0x8000;let binary='';for(let i=0;i<bytes.length;i+=chunk)binary+=String.fromCharCode(...bytes.subarray(i,Math.min(i+chunk,bytes.length)));return btoa(binary)}
async function blobToBase64(blob){return arrayBufferToBase64(await blob.arrayBuffer())}
function base64ToBlob(base64,type='application/octet-stream'){const binary=atob(base64),chunk=0x8000,parts=[];for(let i=0;i<binary.length;i+=chunk){const slice=binary.slice(i,i+chunk),bytes=new Uint8Array(slice.length);for(let j=0;j<slice.length;j++)bytes[j]=slice.charCodeAt(j);parts.push(bytes)}return new Blob(parts,{type})}
function downloadJson(data,name){const blob=new Blob([JSON.stringify(data)],{type:'application/json'}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1500)}
async function exportBackup(){
  const files=await all('files'),total=files.reduce((n,f)=>n+(f.size||f.blob?.size||0),0);
  if(total>BACKUP_WARN_BYTES&&!confirm(`Dieses Vollbackup enthält ${humanBytes(total)} Binärdaten und benötigt vorübergehend zusätzlichen Arbeitsspeicher. Trotzdem fortfahren?`))return;
  const packed=[];
  for(const f of files){
    const blob=f.blob instanceof Blob?f.blob:new Blob([],{type:f.type||'application/octet-stream'});
    packed.push({id:f.id,name:f.name,type:f.type||blob.type,size:blob.size,createdAt:f.createdAt||null,sha256:await sha256Blob(blob),base64:await blobToBase64(blob)});
  }
  const models=(await all('models')).map(({blob,...meta})=>meta);
  const payload={format:'NAQYA-OFFLINE-BACKUP',schema:2,product:'PROVOWARE – NAQYA Memo Tool 2026',version:VERSION,exportedAt:new Date().toISOString(),entries:await all('entries'),projects:await all('projects'),settings:await all('settings'),files:packed,models};
  downloadJson(payload,`NAQYA_VOLLbackup_${todayKey()}.naqya-backup.json`);
}
async function importBackup(e){
  const file=e.target.files?.[0];if(!file)return;
  try{
    const data=JSON.parse(await file.text());
    if(data.schema===1&&Array.isArray(data.entries)){
      for(const x of data.entries)await put('entries',x);for(const x of data.projects||[])await put('projects',x);for(const x of data.settings||[])await put('settings',x);await refresh();alert('Legacy-Backup 0.1 wurde eingelesen.');return;
    }
    if(data.format!=='NAQYA-OFFLINE-BACKUP'||data.schema!==2||!Array.isArray(data.entries))throw new Error('Unbekanntes oder beschädigtes Backupformat.');
    for(const f of data.files||[]){
      const blob=base64ToBlob(f.base64||'',f.type);
      if(f.sha256){const actual=await sha256Blob(blob);if(actual!==f.sha256)throw new Error(`Prüfsumme stimmt nicht: ${f.name}`)}
      await put('files',{id:f.id,name:f.name,type:f.type,size:blob.size,blob,createdAt:f.createdAt||new Date().toISOString()});
    }
    for(const x of data.entries)await put('entries',x);for(const x of data.projects||[])await put('projects',x);for(const x of data.settings||[])await put('settings',x);
    await refresh();alert(`Vollbackup erfolgreich geprüft und eingelesen. ${(data.files||[]).length} Dateien wiederhergestellt.`);
  }catch(err){alert(`Import fehlgeschlagen: ${err.message}`)}finally{e.target.value=''}
}

async function installModelFile(e){
  const file=e.target.files?.[0];if(!file)return;
  const result=window.NAQYA?.stt?.validateModelFile?.(file)||{ok:false,reason:'STT-Modul nicht geladen.'};
  if(!result.ok){alert(result.reason);e.target.value='';return}
  try{
    const hash=await sha256Blob(file),model={id:uid(),name:file.name,type:file.type||'application/octet-stream',size:file.size,sha256:hash,createdAt:new Date().toISOString(),blob:file,status:'lokal-importiert'};
    await put('models',model);await refresh();alert(`Sprachmodell lokal gespeichert: ${file.name}`);
  }catch(err){alert(`Modell konnte nicht gespeichert werden: ${err.message}`)}finally{e.target.value=''}
}
async function deleteModel(id){if(!confirm('Dieses lokale Sprachmodell entfernen?'))return;await del('models',id);await refresh()}

function updateConnectivity(){const b=$('#offlineBadge');if(!b)return;b.textContent=navigator.onLine?'● lokal · Netz verfügbar':'● vollständig offline';b.classList.toggle('online',navigator.onLine)}
function assistant(text){$('#assistantContent').innerHTML=text}

async function init(){
  if(!('indexedDB' in window)){document.body.innerHTML='<main><h1>NAQYA kann nicht starten</h1><p>Dieses Gerät unterstützt IndexedDB nicht.</p></main>';return}
  db=await openDB();await seed();await loadSettings();
  state.capabilities=await (window.NAQYA?.capabilities?.detect?.()||Promise.resolve({indexedDB:true}));
  await recoverInterruptedAudioSessions();await refresh();
  $$('.nav-item').forEach(b=>b.onclick=()=>setView(b.dataset.view));
  $('#quickAdd').onclick=()=>openWizard('note');
  $('#navToggle').onclick=()=>$('#sidebar').classList.toggle('open');
  $('#openHelp').onclick=()=>$('#helpDialog').showModal();
  $('#globalSearch').addEventListener('keydown',e=>{if(e.key==='Enter'){setView('search');setTimeout(()=>{const i=$('#searchInput');i.value=e.target.value;runSearch(i.value);i.focus()},0)}});
  $$('#typeGrid button').forEach(b=>b.onclick=()=>{state.wizardType=b.dataset.type;$$('#typeGrid button').forEach(x=>x.classList.toggle('selected',x===b));assistant(`<strong>${ICONS[state.wizardType]} ${LABELS[state.wizardType]}</strong><p>Im nächsten Schritt erfasst du nur die wichtigsten Angaben. Alles Weitere bleibt optional.</p>`)});
  $('#wizardBack').onclick=()=>{state.wizardStep=Math.max(1,state.wizardStep-1);syncWizard()};
  $('#wizardNext').onclick=()=>{state.wizardStep=Math.min(3,state.wizardStep+1);syncWizard()};
  $('#wizardSave').onclick=saveWizard;
  window.addEventListener('online',async()=>{updateConnectivity();state.capabilities=await window.NAQYA.capabilities.detect()});
  window.addEventListener('offline',async()=>{updateConnectivity();state.capabilities=await window.NAQYA.capabilities.detect()});
  updateConnectivity();
  if(navigator.storage?.persist){try{await navigator.storage.persist();state.capabilities=await window.NAQYA.capabilities.detect()}catch{}}
  if('serviceWorker' in navigator){try{await navigator.serviceWorker.register('./sw.js')}catch(e){console.warn('Service Worker:',e)}}
}

document.addEventListener('DOMContentLoaded',()=>init().catch(e=>{console.error(e);document.body.insertAdjacentHTML('afterbegin',`<div class="message">Startfehler: ${esc(e.message)}</div>`)}));
