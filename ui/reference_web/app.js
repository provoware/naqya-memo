(()=>{'use strict';
const $=id=>document.getElementById(id),root=document.documentElement;
let state=null,current='dashboard',font=1,zoom=1,calendarCursor=new Date(),selectedDayColor=null,calendarMode='month';
const themeOptions=[
 {service:'NEON_TUERKIS',css:'neon-core',label:'Neon'},
 {service:'LILA_NACHT',css:'violet-night',label:'Lila'},
 {service:'KNALLGELB_DUNKEL',css:'yellow-dark',label:'Gelb'},
 {service:'HOCHKONTRAST',css:'high-contrast',label:'Kontrast'}
];let themeIndex=0;
const esc=s=>String(s??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
async function api(path,method='GET',body){if(window.ProvowareMobileApi?.active)return window.ProvowareMobileApi.request(path,method,body);const r=await fetch(path,{method,headers:{'Content-Type':'application/json'},body:body?JSON.stringify(body):undefined});const j=await r.json();if(!j.ok)throw new Error(j.message||j.code||'Fehler');return j.data}
async function assetUrl(id){return window.ProvowareMobileApi?.active?window.ProvowareMobileApi.assetUrl(id):`/asset-file/${id}`}
async function uploadAsset(file,kind,title){
 if(window.ProvowareMobileApi?.active)return window.ProvowareMobileApi.importFile(file,kind,title);
 const q=new URLSearchParams({filename:file.name,kind:String(kind||''),title:String(title||'')});
 const r=await fetch(`/api/assets/upload?${q.toString()}`,{
   method:'POST',headers:{'Content-Type':'application/octet-stream'},body:file
 });
 const data=await r.json();
 if(!data.ok)throw new Error(data.message||data.code||'Dateiimport fehlgeschlagen');
 return data.data;
}
function displayVersion(v){const m=String(v||'').match(/^\d+(?:\.\d+)+/);return m?m[0]:String(v||'unbekannt')}
function setVersionUi(v){
 const short=displayVersion(v);
 const el=$('toolVersion');
 if(el){el.textContent=short;el.title=String(v||short)}
 document.title='OI - PROVOWARE - IO';
}

function toast(msg,error=false){const t=$('toast');t.textContent=msg;t.classList.toggle('error',error);t.hidden=false;clearTimeout(toast.timer);toast.timer=setTimeout(()=>t.hidden=true,3300)}
function isoLocal(v){if(!v)return'';try{return new Date(v).toLocaleString('de-DE',{dateStyle:'short',timeStyle:'short'})}catch{return v}}
function localToIso(v){return v?new Date(v).toISOString():null}
function isoToLocalInput(v){if(!v)return'';const d=new Date(v);d.setMinutes(d.getMinutes()-d.getTimezoneOffset());return d.toISOString().slice(0,16)}
function colorCss(token){return {'neon-tuerkis':'#19f4f2','lila':'#bd42ff','knallgelb':'#ffe53b','orange':'#ff7a31','gruen':'#49ef9b'}[token]||token||'#19f4f2'}

const FIELD_GUIDES={
 title:{placeholder:'z. B. Einkauf, Idee oder Projekt',hint:'Optionales Beispiel – der Titel bleibt frei wählbar.'},
 body:{placeholder:'z. B. Stichpunkte, Gedanken oder längerer Text …',hint:'Optional: frei schreiben oder Stichpunkte verwenden.'},
 tags:{placeholder:'z. B. privat, wichtig, projekt',hint:'Optional: mehrere Begriffe mit Komma trennen.'},
 description:{placeholder:'z. B. Was genau ist zu erledigen?',hint:'Optional: kurze Zusatzinfo zur Aufgabe.'},
 due_at:{hint:'Optional: Termin auswählen; ohne Termin bleibt die Aufgabe offen.'},
 reminder_at:{hint:'Optional: Erinnerung vor oder zum Termin einstellen.'},
 start_at:{hint:'Vorgabe: Startzeit des Termins auswählen.'},
 end_at:{hint:'Optional: Ende nur angeben, wenn benötigt.'},
 priority:{hint:'Vorgabe: NORMAL – nur bei Bedarf ändern.'},
 color_id:{hint:'Optional: passende Kalenderfarbe wählen.'},
 all_day:{hint:'Optional: aktivieren, wenn keine Uhrzeit benötigt wird.'},
 file:{hint:'Optional: Datei direkt auswählen; Dateiname kann als Titel dienen.'},
 source_path:{placeholder:'/home/name/Dokumente/datei.pdf',hint:'Nur Profi: lokalen Pfad alternativ manuell eintragen.'},
 help_mode:{hint:'Vorgabe: 1 · knapp – bei Bedarf ausführlicher stellen.'}
};
const VIEW_META={
 dashboard:{title:'Dashboard',hint:'Überblick und nächster sinnvoller Einstieg.'},
 memo:{title:'Textmemos',hint:'Notiz schreiben, speichern und vorhandene Memos bearbeiten.'},
 todo:{title:'Todos',hint:'Aufgaben erfassen, terminieren und sicher abhaken.'},
 calendar:{title:'Kalender',hint:'Termine und Tagesfarben in Tag, Woche, Monat oder Jahr.'},
 trash:{title:'Papierkorb',hint:'Gelöschte Inhalte prüfen und bei Bedarf wiederherstellen.'},
 diagnostics:{title:'Diagnose',hint:'Systemzustand verstehen; technische Details nur bei Bedarf öffnen.'},
 voice:{title:'Sprachmemos',hint:'Aufnahme bewusst starten und anschließend sicher speichern.'},
 docs:{title:'Dokument / PDF',hint:'Datei auswählen, importieren und revisionsgesichert bearbeiten.'},
 audio:{title:'Audio',hint:'Audio-Assets und Playlists übersichtlich verwalten.'},
 search:{title:'Suche',hint:'Inhalte schnell wiederfinden.'},
 settings:{title:'Einstellungen',hint:'Nur die nötige Hilfetiefe einstellen; Ansicht bleibt oben erreichbar.'},
 help:{title:'Hilfe',hint:'Kurze Orientierung zur aktuellen Bedienung.'}
};
function applyHelpModeUi(mode){
 const value=String(Math.max(1,Math.min(3,Number(mode)||1)));
 root.dataset.helpMode=value;
}
function updateWorkspaceMeta(view){
 const meta=VIEW_META[view]||{title:'Arbeitsbereich',hint:'Sicherer Arbeitsbereich.'};
 $('viewTitle').textContent=meta.title;
 $('viewHint').textContent=meta.hint;
}

function fieldGuideFor(el){
 const n=el.name||el.id||'';
 if(FIELD_GUIDES[n])return FIELD_GUIDES[n];
 if(/^title\d+$/.test(n))return {placeholder:'z. B. Privat, Arbeit oder Wichtig',hint:'Optional: eigene Bezeichnung für diese Kalenderfarbe.'};
 if(/^token\d+$/.test(n))return {placeholder:'z. B. neon-tuerkis',hint:'Optional: gültigen Farbtoken verwenden.'};
 if(n==='quickTitle')return {placeholder:'Notizen',hint:'Vorgabe: Notizen – frei änderbar.'};
 if(n==='quickInput')return {placeholder:'z. B. Rückruf, Idee oder Einkauf …',hint:'Optional: kurze Notiz; Enter speichert direkt.'};
 if(n==='docEditor')return {placeholder:'Text hier bearbeiten …',hint:'Bearbeitung wird als neue Revision gespeichert.'};
 return null;
}
function applyFieldGuidance(scope=document){
 scope.querySelectorAll('input:not([type="hidden"]),textarea,select').forEach(el=>{
   const g=fieldGuideFor(el);
   if(!g)return;
   if(g.placeholder && !el.placeholder && !['datetime-local','checkbox','file'].includes(el.type))el.placeholder=g.placeholder;
   if(g.hint)el.dataset.guide=g.hint;
   const label=el.closest('label');
   if(label && g.hint && !label.querySelector(':scope > .field-hint')){
     const hint=document.createElement('small');hint.className='field-hint';hint.textContent=g.hint;label.appendChild(hint);
   }
   if(!label && g.hint && !el.closest('.quick-note'))el.title=g.hint;
 });
}

function applyFontUi(value,persistLocal=true){
 font=clamp(Number(value)||1,.8,2);
 root.style.setProperty('--font-scale',font.toFixed(2));
 root.dataset.fontTier=font>=1.6?'xl':font>=1.3?'large':'normal';
 if($('fontValue'))$('fontValue').value=`${Math.round(font*100)} %`;
 if(persistLocal)localStorage.setItem('v08-font',font);
}
function applyThemeUi(service,persistLocal=true){
 let idx=themeOptions.findIndex(x=>x.service===service||x.css===service);
 if(idx<0)idx=0;
 themeIndex=idx;const opt=themeOptions[idx];
 root.dataset.theme=opt.css;
 if($('themeValue'))$('themeValue').value=opt.label;
 if(persistLocal)localStorage.setItem('v08-theme-service',opt.service);
}
function displaySettingsFromState(){
 const settings=state?.settings||{};
 if(settings.font_scale!=null)applyFontUi(settings.font_scale,false);
 if(settings.theme)applyThemeUi(settings.theme,false);
 applyHelpModeUi(settings.help_mode||1);
}
async function refresh(){state=await api('/api/state');setVersionUi(state.version);displaySettingsFromState();$('profileName').textContent=state.profile.name;$('integrity').textContent=state.integrity;$('startStatus').textContent='Bereit';$('dataStatus').textContent=state.integrity==='ok'?'OK':'Prüfen';const bs=state.backup||{generations:0,label:'Noch keine'};$('backupStatus').textContent=bs.label;$('backupChip')?.classList.toggle('warn',!bs.generations);$('countMemo').textContent=state.counts.memos;$('countTodo').textContent=state.counts.todos;$('countEvent').textContent=state.counts.events;$('countTrash').textContent=state.counts.trash;renderNext();if(current)await render(current)}
function renderNext(){const n=$('nextGrid');n.innerHTML='';if(!state.next.length){n.innerHTML='<div class="next-row"><em>—</em><span>Noch keine Aufgaben oder Termine</span><span></span></div>';return}state.next.forEach(x=>{const when=x.payload.due_at||x.payload.start_at||'';n.insertAdjacentHTML('beforeend',`<div class="next-row"><em>${x.entity_type==='todo'?'✓':'▦'}</em><span>${esc(x.title)}</span><span>${esc(isoLocal(when))}</span></div>`)})}
function dash(){const bs=state.backup||{label:'Noch keine'};return `<div class="dashboard-grid simplified-dashboard">
<article class="dash-card"><h3>Textmemos</h3><strong>${state.counts.memos}</strong><p>Notizen anlegen, bearbeiten und wiederfinden.</p></article>
<article class="dash-card"><h3>Todos</h3><strong>${state.counts.todos}</strong><p>Aufgaben mit Termin und Erinnerung.</p></article>
<article class="dash-card"><h3>Kalender</h3><strong>${state.counts.events}</strong><p>Termine und farbige Tagesmarkierungen.</p></article>
<article class="dash-card safety-card"><h3>Sicherheit</h3><strong>${state.integrity==='ok'?'OK':'Prüfen'}</strong><p>DB ${esc(state.integrity)} · Papierkorb ${state.counts.trash} · Backup ${esc(bs.label)}</p></article>
</div>`}
async function memoView(){const items=await api('/api/memos');return `<div class="module-grid"><section class="form-card"><h3>Textmemo</h3><form id="memoForm" class="form-grid"><input type="hidden" name="id"><input type="hidden" name="revision"><label class="full">Titel<input name="title" maxlength="240" required placeholder="z. B. Idee, Einkauf oder Projekt"></label><label class="full">Text<textarea name="body" rows="8" placeholder="z. B. Stichpunkte, Gedanken oder längerer Text …"></textarea></label><label class="full">Tags<input name="tags" placeholder="z. B. privat, wichtig, projekt"></label><div class="form-actions"><button class="primary">Speichern</button><button type="button" id="memoCancel">Neu/leeren</button></div></form></section><section class="list-card"><h3>Textmemos (${items.length})</h3><div class="item-list">${items.map(x=>`<article class="item"><div><h4>${esc(x.title)}</h4><p>${esc(x.payload.body)}</p><div class="item-meta">Revision ${x.revision} · ${esc((x.payload.tags||[]).join(', '))}</div></div><div class="item-actions"><button data-edit-memo="${x.id}">Bearbeiten</button><button class="danger" data-trash-memo="${x.id}" data-rev="${x.revision}">Papierkorb</button></div></article>`).join('')||'<p>Noch keine Memos.</p>'}</div></section></div>`}
async function todoView(){const items=await api('/api/todos');return `<div class="module-grid"><section class="form-card"><h3>Aufgabe</h3><form id="todoForm" class="form-grid"><input type="hidden" name="id"><input type="hidden" name="revision"><label class="full">Titel<input name="title" required placeholder="z. B. Einkauf erledigen"></label><label class="full">Beschreibung<textarea name="description" rows="4" placeholder="z. B. Was genau ist zu erledigen?"></textarea></label><label>Termin<input name="due_at" type="datetime-local"></label><label>Erinnerung<input name="reminder_at" type="datetime-local"></label><label>Priorität<select name="priority"><option>NORMAL</option><option>HOCH</option><option>NIEDRIG</option></select></label><div class="form-actions"><button class="primary">Speichern</button><button type="button" id="todoCancel">Neu/leeren</button></div></form></section><section class="list-card"><h3>Todos (${items.length})</h3><div class="item-list">${items.map(x=>`<article class="item"><div><h4>${esc(x.title)}</h4><p>${esc(x.payload.description||'')}</p><div class="item-meta">${esc(isoLocal(x.payload.due_at))} · ${esc(x.payload.priority)} · Rev ${x.revision}</div></div><div class="item-actions"><button data-edit-todo="${x.id}">Bearbeiten</button>${x.payload.completed?'<span>✓ erledigt</span>':`<button data-complete-todo="${x.id}" data-rev="${x.revision}">Abhaken</button>`}<button class="danger" data-trash-todo="${x.id}" data-rev="${x.revision}">Papierkorb</button></div></article>`).join('')||'<p>Noch keine Todos.</p>'}</div></section></div>`}
function monthMeta(d){const y=d.getFullYear(),m=d.getMonth();return {y,m,first:new Date(y,m,1),last:new Date(y,m+1,0)}}
function dateKey(d){return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`}

function dayCalendar(events){
 const key=dateKey(calendarCursor); const todays=events.filter(e=>String(e.payload.start_at||'').slice(0,10)===key);
 return `<section class="calendar-shell"><h3>${esc(calendarCursor.toLocaleDateString('de-DE',{weekday:'long',day:'2-digit',month:'long',year:'numeric'}))}</h3><div class="item-list">${todays.map(e=>`<article class="item"><div><h4>${esc(e.title)}</h4><div class="item-meta">${esc(isoLocal(e.payload.start_at))}</div></div></article>`).join('')||'<p>Keine Termine an diesem Tag.</p>'}</div></section>`;
}
function weekCalendar(events){
 const d=new Date(calendarCursor); const monday=new Date(d); monday.setDate(d.getDate()-((d.getDay()+6)%7));
 let html='<div class="calendar-week">';
 for(let i=0;i<7;i++){const x=new Date(monday);x.setDate(monday.getDate()+i);const key=dateKey(x);const ev=events.filter(e=>String(e.payload.start_at||'').slice(0,10)===key);html+=`<section class="week-day"><h4>${esc(x.toLocaleDateString('de-DE',{weekday:'short',day:'2-digit',month:'2-digit'}))}</h4>${ev.map(e=>`<div class="mini-event">${esc(e.title)}</div>`).join('')||'<small>frei</small>'}</section>`}
 return html+'</div>';
}
function yearCalendar(events){
 const year=calendarCursor.getFullYear();
 return `<div class="year-grid">${Array.from({length:12},(_,m)=>{const count=events.filter(e=>String(e.payload.start_at||'').startsWith(`${year}-${String(m+1).padStart(2,'0')}`)).length;return `<button class="year-month" data-year-month="${m}"><strong>${esc(new Date(year,m,1).toLocaleDateString('de-DE',{month:'long'}))}</strong><span>${count} Termine</span></button>`}).join('')}</div>`;
}
function monthCalendar(events){const {y,m,first}=monthMeta(calendarCursor);const start=new Date(y,m,1);const monday=(start.getDay()+6)%7;start.setDate(start.getDate()-monday);let html='<div class="month-grid">'+['Mo','Di','Mi','Do','Fr','Sa','So'].map(x=>`<div class="weekday">${x}</div>`).join('');
for(let i=0;i<42;i++){const d=new Date(start);d.setDate(start.getDate()+i);const key=dateKey(d);const same=d.getMonth()===m;const dayEvents=events.filter(e=>String(e.payload.start_at||'').slice(0,10)===key);const dc=state.day_colors?.[key];const col=state.colors.find(c=>c.id===dc?.color_id);html+=`<button class="day-cell ${same?'':'other'} ${dateKey(new Date())===key?'today':''}" data-day="${key}" aria-label="${key}${col?' · '+esc(col.title):''}" ${col?`style="box-shadow:inset 0 0 0 2px ${colorCss(col.token)}"`:''}><span class="day-number">${d.getDate()}</span>${col?`<span class="day-color-dot" style="background:${colorCss(col.token)}"></span>`:''}<span class="day-events">${dayEvents.slice(0,3).map(e=>`<span class="mini-event">${esc(e.title)}</span>`).join('')}</span></button>`}
return html+'</div>'}
async function calendarView(){const items=await api('/api/events');const opts=state.colors.map(c=>`<option value="${c.id}">${esc(c.title)}</option>`).join('');const ym=calendarCursor.toLocaleDateString('de-DE',{month:'long',year:'numeric'});
return `<div class="calendar-legend">${state.colors.map(c=>`<div class="legend-chip" style="border-color:${colorCss(c.token)}">${esc(c.title)}</div>`).join('')}</div>
<div class="calendar-modes"><button data-cal-mode="day">Tag</button><button data-cal-mode="week">Woche</button><button data-cal-mode="month">Monat</button><button data-cal-mode="year">Jahr</button></div>
<section class="calendar-shell"><div class="calendar-head"><h3>${esc(ym)}</h3><div class="calendar-nav"><button id="monthPrev">←</button><button id="monthToday">Heute</button><button id="monthNext">→</button></div></div>${calendarMode==='day'?dayCalendar(items):calendarMode==='week'?weekCalendar(items):calendarMode==='year'?yearCalendar(items):monthCalendar(items)}</section>
<div class="module-grid" style="margin-top:10px"><section class="form-card"><h3>Termin</h3><form id="eventForm" class="form-grid"><input type="hidden" name="id"><input type="hidden" name="revision"><label class="full">Titel<input name="title" required placeholder="z. B. Einkauf erledigen"></label><label>Start<input name="start_at" type="datetime-local" required></label><label>Ende<input name="end_at" type="datetime-local"></label><label>Erinnerung<input name="reminder_at" type="datetime-local"></label><label>Farbe<select name="color_id">${opts}</select></label><label><span>Ganztägig</span><input name="all_day" type="checkbox"></label><div class="form-actions"><button class="primary">Speichern</button><button type="button" id="eventCancel">Neu/leeren</button></div></form>
<h3>5er-Legende bearbeiten</h3><form id="colorForm"><div class="color-editor">${state.colors.map((c,i)=>`<label class="color-row">${i+1}. Farbe<input name="title${i}" value="${esc(c.title)}"><input name="token${i}" value="${esc(c.token)}" aria-label="Farbtoken ${i+1}"></label>`).join('')}</div><button class="primary">Legende speichern</button></form></section>
<section class="list-card"><h3>Termine (${items.length})</h3><div class="item-list">${items.map(x=>`<article class="item"><div><h4>${esc(x.title)}</h4><p>${esc(isoLocal(x.payload.start_at))}${x.payload.end_at?' – '+esc(isoLocal(x.payload.end_at)):''}</p><div class="item-meta">Rev ${x.revision}</div></div><div class="item-actions"><button data-edit-event="${x.id}">Bearbeiten</button><button class="danger" data-trash-event="${x.id}" data-rev="${x.revision}">Papierkorb</button></div></article>`).join('')||'<p>Noch keine Termine.</p>'}</div></section></div>`}
async function trashView(){const items=await api('/api/trash');return `<section class="list-card"><h3>Papierkorb (${items.length})</h3><p>Kein Hard Delete. Wiederherstellung ist eine kontrollierte Mutation.</p><div class="item-list">${items.map(x=>`<article class="item"><div><h4>${esc(x.title)}</h4><div class="item-meta">${esc(x.entity_type)} · Revision ${x.revision}</div></div><div class="item-actions"><button class="primary" data-restore="${x.id}" data-rev="${x.revision}">Wiederherstellen</button></div></article>`).join('')||'<p>Papierkorb leer.</p>'}</div></section>`}
async function diagnosticView(){const p=await api('/api/diagnostics/preview');const caps=await api('/api/platform/capabilities');const rem=await api('/api/reminders/pending');return `<div class="diagnostic-grid"><section class="diagnostic-card"><h3>Privacy-Vorschau</h3><p>Vor Erzeugung des Berichts sehen Sie, welche Daten enthalten werden.</p><pre>${esc(JSON.stringify(p,null,2))}</pre></section><section class="diagnostic-card"><h3>Datenschutzfilter</h3><p class="privacy-ok">✓ Memo-Inhalte ausgeschlossen<br>✓ PIN ausgeschlossen<br>✓ Tokens ausgeschlossen<br>✓ Home-Pfad verkürzt</p><p>Erst nach Ihrer Bestätigung wird lokal eine TXT-Datei erzeugt.</p><button class="primary" id="diagCreate">Diagnose-TXT erstellen</button></section>
<section class="diagnostic-card"><h3>Plattform-Evidence</h3><pre>${esc(JSON.stringify(caps,null,2))}</pre></section>
<section class="diagnostic-card"><h3>Reminder Acceptance</h3><p>${rem.length} Reminder aktuell fällig und noch nicht als zugestellt markiert.</p></section></div>`}


async function voiceView(){const cap=await api('/api/audio/capability');const assets=(await api('/api/assets/list')).filter(x=>x.kind==='audio');const ff=cap.ffmpeg?'Bereit':'Fehlt';const mic=cap.native_microphone_tested?'Bestätigt':'Noch offen';return `<div class="module-grid"><section class="form-card"><h3>Sprachaufnahme</h3><p>${window.ProvowareMobileApi?.active?'Mobile: native Mikrofonbrücke → sicherer Asset-Commit.':'Linux: FFmpeg-Aufnahme → Staging → sicherer Asset-Commit.'}</p><div class="runtime-summary"><span><b>FFmpeg</b>${ff}</span><span><b>Mikrofontest</b>${mic}</span></div><div class="form-actions"><button class="primary" id="recordStart">● Aufnahme starten</button><button id="recordStop">■ Stop & sicher speichern</button></div><details class="tech-details"><summary>Technische Details anzeigen</summary><pre>${esc(JSON.stringify(cap,null,2))}</pre></details><p class="item-meta">Mikrofonzugriff wird erst nach ausdrücklicher Systemfreigabe verwendet.</p></section><section class="list-card"><h3>Audio (${assets.length})</h3><div class="item-list">${assets.map(a=>`<article class="item"><div><h4>${esc(a.title)}</h4><audio controls preload="metadata" data-audio-asset="${a.asset_id}" ${window.ProvowareMobileApi?.active?'':`src="/asset-file/${a.asset_id}"`}></audio><div class="item-meta">${a.size_bytes} Bytes · SHA ${esc(a.sha256.slice(0,12))}…</div></div></article>`).join('')||'<p>Noch keine Audio-Assets.</p>'}</div></section></div>`}
async function documentView(){const assets=(await api('/api/assets/list')).filter(x=>x.kind==='document');return `<div class="module-grid"><section class="form-card"><h3>Dokumente / PDF</h3><form id="assetForm" class="form-grid"><input type="hidden" name="kind" value="document"><label class="full file-picker-field">📂 Datei auswählen<input type="file" name="file" accept=".pdf,.txt,.md,.rtf,.docx"></label><label class="full">Titel<input name="title" placeholder="Optional: eigener Titel"></label><details class="full advanced-import"><summary>Profi: lokalen Pfad manuell verwenden</summary><label>Lokaler Dateipfad<input name="source_path" placeholder="/home/.../dokument.pdf"></label></details><div class="form-actions"><button class="primary">Sicher importieren</button></div></form><p>PDF wird intern angezeigt. TXT/MD kann revisionsgesichert bearbeitet werden. DOCX/RTF bleibt kontrolliert read-only.</p></section><section class="list-card"><h3>Dokumente (${assets.length})</h3><div class="item-list">${assets.map(a=>`<article class="item"><div><h4>${esc(a.title)}</h4><div class="item-meta">${esc(a.original_name)} · Rev ${a.revision||1} · ${a.size_bytes} Bytes</div></div><div class="item-actions"><button data-view-doc="${a.asset_id}" data-name="${esc(a.original_name)}">Anzeigen</button>${/\.(txt|md)$/i.test(a.original_name)?`<button data-edit-doc="${a.asset_id}">Bearbeiten</button>`:''}</div></article>`).join('')||'<p>Noch keine Dokumente.</p>'}</div></section></div><section id="documentStage" class="document-stage" hidden></section>`}
function showModal(title,body,actions=''){const old=document.querySelector('.modal');if(old)old.remove();document.body.insertAdjacentHTML('beforeend',`<div class="modal"><section class="modal-card"><div class="modal-head"><h3>${esc(title)}</h3><button id="modalClose">×</button></div>${body}<div class="modal-actions">${actions}</div></section></div>`);$('modalClose').onclick=()=>document.querySelector('.modal')?.remove()}
function assetView(kind,title){return `<div class="module-grid"><section class="form-card"><h3>${esc(title)}</h3><p>Assets werden mit Typprüfung, Quota und SHA-256 gespeichert.</p><form id="assetForm" class="form-grid"><input type="hidden" name="kind" value="${kind}"><label class="full file-picker-field">📂 Datei auswählen<input type="file" name="file"></label><label class="full">Titel<input name="title" placeholder="Optional: eigener Titel"></label><details class="full advanced-import"><summary>Profi: lokalen Pfad manuell verwenden</summary><label>Lokaler Dateipfad<input name="source_path" placeholder="/home/.../datei.${kind==='audio'?'wav':'pdf'}"></label></details><div class="form-actions"><button class="primary">Sicher importieren</button></div></form></section><section class="list-card"><h3>Asset-Sicherheit</h3><p>Erlaubte Typen, Quota, Prüfsumme, Manifest und Quarantäne sind aktiv.</p><div id="quotaBox"></div></section></div>`}
async function audioView(){const pls=await api('/api/playlists');return `<div class="module-grid"><section class="form-card"><h3>Persistente Playlist</h3><form id="playlistForm" class="form-grid"><label class="full">Playlist-Titel<input name="title" value="Meine Playlist" placeholder="z. B. Sprachmemos heute"></label><div class="form-actions"><button class="primary">Playlist erstellen</button></div></form></section><section class="list-card"><h3>Playlists (${pls.length})</h3><div class="item-list">${pls.map(x=>`<article class="item"><div><h4>${esc(x.title)}</h4><div class="item-meta">${(x.payload.items||[]).length} Assets · Rev ${x.revision}</div></div></article>`).join('')||'<p>Noch keine Playlist.</p>'}</div></section></div>`}
function placeholder(name){return `<section class="dash-card"><h3>${esc(name)}</h3><p>Dieser Bereich ist in der Referenzoberfläche noch nicht aktiv. Die vorhandenen Kernbereiche bleiben unverändert nutzbar.</p></section>`}
function settingsView(){return `<section class="form-card simple-settings"><h3>Einstellungen</h3><p>Darstellung stellst du direkt oben im Dashboard ein. Hier bleibt nur die gewünschte Hilfetiefe.</p><form id="settingsForm" class="form-grid"><label class="full">Hilfemodus<select name="help_mode"><option value="1">1 · knapp</option><option value="2">2 · geführt</option><option value="3">3 · ausführlich</option></select></label><div class="form-actions"><button class="primary">Speichern</button></div></form></section>`}
async function render(view){current=view;updateWorkspaceMeta(view);const host=$('moduleHost');let html;if(view==='dashboard')html=dash();else if(view==='memo')html=await memoView();else if(view==='todo')html=await todoView();else if(view==='calendar')html=await calendarView();else if(view==='trash')html=await trashView();else if(view==='diagnostics')html=await diagnosticView();
else if(view==='voice')html=await voiceView();
else if(view==='docs')html=await documentView();
else if(view==='audio')html=await audioView();
else if(view==='settings')html=settingsView();else html=placeholder(view);host.innerHTML=html;bindModule();applyFieldGuidance(host)}
function findEntity(type,id){return api(type==='memo'?'/api/memos':type==='todo'?'/api/todos':'/api/events').then(xs=>xs.find(x=>x.id===id))}
function resetForm(form){form?.reset();if(form?.elements.id)form.elements.id.value='';if(form?.elements.revision)form.elements.revision.value=''}
function bindModule(){
 const mf=$('memoForm');if(mf){mf.onsubmit=async e=>{e.preventDefault();const f=new FormData(mf),id=f.get('id');const body={title:f.get('title'),body:f.get('body'),tags:String(f.get('tags')||'').split(',').map(x=>x.trim()).filter(Boolean)};try{id?await api(`/api/memos/${id}/edit`,'POST',{...body,revision:+f.get('revision')}):await api('/api/memos','POST',body);toast(id?'Memo aktualisiert.':'Memo gespeichert.');await refresh()}catch(e){toast(e.message,true)}};$('memoCancel').onclick=()=>resetForm(mf)}
 document.querySelectorAll('[data-edit-memo]').forEach(b=>b.onclick=async()=>{const x=await findEntity('memo',b.dataset.editMemo);mf.elements.id.value=x.id;mf.elements.revision.value=x.revision;mf.elements.title.value=x.title;mf.elements.body.value=x.payload.body||'';mf.elements.tags.value=(x.payload.tags||[]).join(', ');mf.elements.title.focus()});
 document.querySelectorAll('[data-trash-memo]').forEach(b=>b.onclick=async()=>{try{await api(`/api/memos/${b.dataset.trashMemo}/trash`,'POST',{revision:+b.dataset.rev});toast('Memo im Papierkorb.');await refresh()}catch(e){toast(e.message,true)}})
 const tf=$('todoForm');if(tf){tf.onsubmit=async e=>{e.preventDefault();const f=new FormData(tf),id=f.get('id');const body={title:f.get('title'),description:f.get('description'),due_at:localToIso(f.get('due_at')),reminder_at:localToIso(f.get('reminder_at')),priority:f.get('priority')};try{id?await api(`/api/todos/${id}/edit`,'POST',{...body,revision:+f.get('revision')}):await api('/api/todos','POST',body);toast(id?'Todo aktualisiert.':'Todo gespeichert.');await refresh()}catch(e){toast(e.message,true)}};$('todoCancel').onclick=()=>resetForm(tf)}
 document.querySelectorAll('[data-edit-todo]').forEach(b=>b.onclick=async()=>{const x=await findEntity('todo',b.dataset.editTodo);tf.elements.id.value=x.id;tf.elements.revision.value=x.revision;tf.elements.title.value=x.title;tf.elements.description.value=x.payload.description||'';tf.elements.due_at.value=isoToLocalInput(x.payload.due_at);tf.elements.reminder_at.value=isoToLocalInput(x.payload.reminder_at);tf.elements.priority.value=x.payload.priority||'NORMAL';tf.elements.title.focus()})
 document.querySelectorAll('[data-complete-todo]').forEach(b=>b.onclick=async()=>{try{await api(`/api/todos/${b.dataset.completeTodo}/complete`,'POST',{revision:+b.dataset.rev});toast('Todo erledigt.');await refresh()}catch(e){toast(e.message,true)}})
 document.querySelectorAll('[data-trash-todo]').forEach(b=>b.onclick=async()=>{try{await api(`/api/todos/${b.dataset.trashTodo}/trash`,'POST',{revision:+b.dataset.rev});toast('Todo im Papierkorb.');await refresh()}catch(e){toast(e.message,true)}})
 const ef=$('eventForm');if(ef){ef.onsubmit=async e=>{e.preventDefault();const f=new FormData(ef),id=f.get('id');const body={title:f.get('title'),start_at:localToIso(f.get('start_at')),end_at:localToIso(f.get('end_at')),reminder_at:localToIso(f.get('reminder_at')),color_id:f.get('color_id'),all_day:f.get('all_day')==='on'};try{id?await api(`/api/events/${id}/edit`,'POST',{...body,revision:+f.get('revision')}):await api('/api/events','POST',body);toast(id?'Termin aktualisiert.':'Termin gespeichert.');await refresh()}catch(e){toast(e.message,true)}};$('eventCancel').onclick=()=>resetForm(ef)}
 document.querySelectorAll('[data-edit-event]').forEach(b=>b.onclick=async()=>{const x=await findEntity('event',b.dataset.editEvent);ef.elements.id.value=x.id;ef.elements.revision.value=x.revision;ef.elements.title.value=x.title;ef.elements.start_at.value=isoToLocalInput(x.payload.start_at);ef.elements.end_at.value=isoToLocalInput(x.payload.end_at);ef.elements.reminder_at.value=isoToLocalInput(x.payload.reminder_at);ef.elements.color_id.value=x.payload.color_id||'';ef.elements.all_day.checked=!!x.payload.all_day;ef.elements.title.focus()})
 document.querySelectorAll('[data-trash-event]').forEach(b=>b.onclick=async()=>{try{await api(`/api/events/${b.dataset.trashEvent}/trash`,'POST',{revision:+b.dataset.rev});toast('Termin im Papierkorb.');await refresh()}catch(e){toast(e.message,true)}})
 document.querySelectorAll('[data-restore]').forEach(b=>b.onclick=async()=>{try{await api(`/api/trash/${b.dataset.restore}/restore`,'POST',{revision:+b.dataset.rev});toast('Wiederhergestellt.');await refresh()}catch(e){toast(e.message,true)}})
 document.querySelectorAll('[data-day]').forEach(b=>b.onclick=async()=>{if(!state.colors.length)return;const current=state.day_colors?.[b.dataset.day]?.color_id;let idx=Math.max(0,state.colors.findIndex(c=>c.id===current));idx=(idx+1)%state.colors.length;try{await api('/api/calendar/day-color','POST',{day:b.dataset.day,color_id:state.colors[idx].id});toast(`${b.dataset.day}: ${state.colors[idx].title}`);await refresh()}catch(e){toast(e.message,true)}})
 
 document.querySelectorAll('[data-cal-mode]').forEach(b=>b.onclick=async()=>{calendarMode=b.dataset.calMode;await render('calendar')})
 document.querySelectorAll('[data-year-month]').forEach(b=>b.onclick=async()=>{calendarCursor=new Date(calendarCursor.getFullYear(),+b.dataset.yearMonth,1);calendarMode='month';await render('calendar')})

 if($('monthPrev'))$('monthPrev').onclick=async()=>{calendarCursor=new Date(calendarCursor.getFullYear(),calendarCursor.getMonth()-1,1);await render('calendar')}
 if($('monthNext'))$('monthNext').onclick=async()=>{calendarCursor=new Date(calendarCursor.getFullYear(),calendarCursor.getMonth()+1,1);await render('calendar')}
 if($('monthToday'))$('monthToday').onclick=async()=>{calendarCursor=new Date();await render('calendar')}
 const cf=$('colorForm');if(cf)cf.onsubmit=async e=>{e.preventDefault();const f=new FormData(cf),entries=[];for(let i=0;i<5;i++)entries.push({title:f.get(`title${i}`),token:f.get(`token${i}`)});try{await api('/api/calendar/colors','POST',{entries});toast('5er-Legende gespeichert.');await refresh()}catch(e){toast(e.message,true)}}
 const sf=$('settingsForm');if(sf){if(state?.settings?.help_mode)sf.elements.help_mode.value=String(state.settings.help_mode);sf.onsubmit=async e=>{e.preventDefault();const f=new FormData(sf);try{await api('/api/settings','POST',{help_mode:+f.get('help_mode')});toast('Hilfemodus gespeichert.');await refresh()}catch(e){toast(e.message,true)}}}
 

 if($('recordStart'))$('recordStart').onclick=async()=>{try{await api('/api/audio/start','POST',{backend:'pulse',device:'default'});toast('Aufnahme läuft.')}catch(e){toast(e.message,true)}}
 if($('recordStop'))$('recordStop').onclick=async()=>{const title=prompt('Titel der Sprachaufnahme','Sprachmemo')||'Sprachmemo';try{await api('/api/audio/stop','POST',{title});toast('Sprachmemo sicher gespeichert.');await refresh()}catch(e){toast(e.message,true)}}
 document.querySelectorAll('[data-view-doc]').forEach(b=>b.onclick=async()=>{const name=b.dataset.name||'',aid=b.dataset.viewDoc;try{const url=await assetUrl(aid);if(/\.pdf$/i.test(name)){showModal(name,`<iframe class="pdf-frame" src="${url}" title="PDF ${esc(name)}"></iframe>`)}else{showModal(name,`<p>Dieses Format wird sicher bereitgestellt.</p><p><a href="${url}" target="_blank" rel="noopener">Dokument öffnen</a></p>`)}}catch(e){toast(e.message,true)}})
 document.querySelectorAll('[data-edit-doc]').forEach(b=>b.onclick=async()=>{try{const x=await api(`/api/assets/${b.dataset.editDoc}/text`);showModal(x.manifest.title,`<textarea id="docEditor" rows="18">${esc(x.text)}</textarea><p class="item-meta">Revision ${x.manifest.revision||1}</p>`,`<button class="primary" id="docSave">Revision speichern</button>`);$('docSave').onclick=async()=>{try{await api('/api/assets/edit-text','POST',{asset_id:x.manifest.asset_id,text:$('docEditor').value,revision:x.manifest.revision||1});document.querySelector('.modal')?.remove();toast('Dokument revisionsgesichert gespeichert.');await refresh()}catch(e){toast(e.message,true)}}}catch(e){toast(e.message,true)}})

 const af=$('assetForm');if(af){af.onsubmit=async e=>{e.preventDefault();const f=new FormData(af);try{let x;const file=f.get('file'),kind=f.get('kind'),title=f.get('title');if(file instanceof File&&file.size){x=await uploadAsset(file,kind,title)}else{const source=f.get('source_path');if(window.ProvowareMobileApi?.active)throw new Error('Bitte eine Datei auswählen.');if(!String(source||'').trim())throw new Error('Bitte eine Datei auswählen.');x=await api('/api/assets/import','POST',{source_path:source,kind,title})}toast(`Asset importiert: ${x.asset_id}`);const q=await api('/api/assets/quota');if($('quotaBox'))$('quotaBox').textContent=`${q.used} / ${q.quota} Bytes (${q.percent} %) verwendet.`;await refresh()}catch(e){toast(e.message,true)}};api('/api/assets/quota').then(q=>{if($('quotaBox'))$('quotaBox').textContent=`${q.used} / ${q.quota} Bytes (${q.percent} %) verwendet.`})}
 const pf=$('playlistForm');if(pf)pf.onsubmit=async e=>{e.preventDefault();const f=new FormData(pf);try{await api('/api/playlists','POST',{title:f.get('title')});toast('Playlist erstellt.');await refresh()}catch(e){toast(e.message,true)}}

 document.querySelectorAll('[data-audio-asset]').forEach(async el=>{if(window.ProvowareMobileApi?.active){try{el.src=await assetUrl(el.dataset.audioAsset)}catch(e){console.warn(e)}}})
 if($('diagCreate'))$('diagCreate').onclick=async()=>{if(!confirm('Diagnosebericht jetzt lokal mit den angezeigten, gefilterten Daten erzeugen?'))return;try{const x=await api('/api/diagnostics/create','POST',{confirmed:true});toast(`Diagnose erstellt: ${x.name}`)}catch(e){toast(e.message,true)}}
}
async function quickSave(){const text=$('quickInput').value;if(!text.trim())return toast('Bitte zuerst Text eingeben.',true);try{await api('/api/quick-note','POST',{title:$('quickTitle').value,text});$('quickInput').value='';toast('Textdatei ergänzt.')}catch(e){toast(e.message,true)}}
$('quickSave').onclick=quickSave;$('quickInput').addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();quickSave()}})
$('quickOpen').onclick=async()=>{try{const x=await api('/api/quick-note/open','POST',{title:$('quickTitle').value});toast(x.opened?'Standardprogramm angefordert.':'Öffnen nicht verfügbar.')}catch(e){toast(e.message,true)}}
$('quickShare').onclick=async()=>{try{const x=await api('/api/quick-note/share','POST',{title:$('quickTitle').value});toast(x.opened?'Mailprogramm geöffnet. Versand erst nach Bestätigung.':'Teilen nicht verfügbar.')}catch(e){toast(e.message,true)}}
$('undoBtn').onclick=async()=>{try{await api('/api/undo','POST',{});toast('Rückgängig.');await refresh()}catch(e){toast(e.message,true)}}
$('redoBtn').onclick=async()=>{try{await api('/api/redo','POST',{});toast('Wiederholt.');await refresh()}catch(e){toast(e.message,true)}}
document.querySelectorAll('.nav-item[data-view], [data-open]').forEach(b=>b.onclick=async()=>{const v=b.dataset.view||b.dataset.open;document.querySelectorAll('.nav-item[data-view]').forEach(x=>{const active=x.dataset.view===v;x.classList.toggle('active',active);if(active)x.setAttribute('aria-current','page');else x.removeAttribute('aria-current')});await render(v);if(innerWidth<=720)drawer(false)})
const nav=$('mainNav'),scrim=$('scrim');function drawer(open){nav.classList.toggle('open',open);scrim.hidden=!open;$('menuBtn').setAttribute('aria-expanded',String(open))}$('menuBtn').onclick=()=>drawer(true);$('closeMenuBtn').onclick=()=>drawer(false);scrim.onclick=()=>drawer(false)
function clamp(v,a,b){return Math.max(a,Math.min(b,v))}
$('themeBtn').onclick=async()=>{themeIndex=(themeIndex+1)%themeOptions.length;const opt=themeOptions[themeIndex];applyThemeUi(opt.service);try{await api('/api/settings','POST',{theme:opt.service});if(state?.settings)state.settings.theme=opt.service}catch(e){toast('Theme lokal geändert; Speichern im Profil nicht möglich.',true)}};
const localTheme=localStorage.getItem('v08-theme-service');if(localTheme)applyThemeUi(localTheme,false);
async function setFont(d){applyFontUi(font+d);try{await api('/api/settings','POST',{font_scale:font});if(state?.settings)state.settings.font_scale=font}catch(e){toast('Schrift lokal geändert; Speichern im Profil nicht möglich.',true)}}
$('fontDown').onclick=()=>setFont(-.1);$('fontUp').onclick=()=>setFont(.1);
const sfStored=parseFloat(localStorage.getItem('v08-font'));if(sfStored>=.8&&sfStored<=2)applyFontUi(sfStored,false);else applyFontUi(1,false);
function setZoom(d){zoom=clamp(zoom+d,.8,2);root.style.setProperty('--area-zoom',zoom.toFixed(2));const host=$('moduleHost');if(host)host.dataset.zoomTier=zoom>=1.7?'xl':zoom>=1.4?'large':zoom>=1.2?'medium':'normal';if($('zoomValue'))$('zoomValue').value=`${Math.round(zoom*100)} %`;localStorage.setItem('v012-area-zoom',zoom)}
$('zoomOut').onclick=()=>setZoom(-.1);$('zoomIn').onclick=()=>setZoom(.1);$('zoomReset').onclick=()=>{zoom=1;setZoom(0)}
const savedZoom=parseFloat(localStorage.getItem('v012-area-zoom'));if(savedZoom>=.8&&savedZoom<=2){zoom=savedZoom;setZoom(0)}else setZoom(0);
$('devToggle').onclick=()=>{const p=$('devPanel'),o=!p.hidden;p.hidden=o;$('devToggle').setAttribute('aria-expanded',String(!o))}
function layout(){$('layoutMode').textContent=innerWidth<=720?'Mobil':innerWidth<=1050?'Kompakt':'Desktop'}addEventListener('resize',layout,{passive:true});layout()
applyFieldGuidance(document);
refresh().catch(e=>{toast('Backend nicht erreichbar. Bitte STARTEN_LINUX.sh verwenden.',true);$('startStatus').textContent='Backend fehlt';$('debugState').textContent='1 Fehler';if($('systemState'))$('systemState').textContent='Start prüfen';$('moduleHost').innerHTML='<section class="dash-card"><h3>Start erforderlich</h3><p>Auf Desktop wird der lokale Service benötigt. Android/iOS verwenden den eingebetteten Mobile-Runtime-Adapter.</p></section>'})
})();