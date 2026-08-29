(function(global){
'use strict';

const STORE_NAMES=['entities','undo','meta','assets','assetMeta','backups','backupAssets'];
const DEFAULT_COLORS=[
  {id:'cal-arbeit',title:'Arbeit',token:'neon-tuerkis',order:0},
  {id:'cal-privat',title:'Privat',token:'lila',order:1},
  {id:'cal-wichtig',title:'Wichtig',token:'knallgelb',order:2},
  {id:'cal-info',title:'Info',token:'orange',order:3},
  {id:'cal-frei',title:'Frei',token:'gruen',order:4},
];
const ALLOWED_AUDIO=['wav','mp3','ogg','m4a','flac','mp4','aac'];
const ALLOWED_DOC=['pdf','txt','md','rtf','docx'];

function deepClone(v){
  if (typeof structuredClone==='function') return structuredClone(v);
  return JSON.parse(JSON.stringify(v));
}
function uuid(){
  if (global.crypto && typeof global.crypto.randomUUID==='function') return global.crypto.randomUUID();
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g,c=>{const r=Math.random()*16|0,v=c==='x'?r:(r&3|8);return v.toString(16)});
}
function nowIso(){return new Date().toISOString()}
function extOf(name){const m=String(name||'').toLowerCase().match(/\.([a-z0-9]+)$/);return m?m[1]:''}
function stable(value){
  if(Array.isArray(value)) return '['+value.map(stable).join(',')+']';
  if(value && typeof value==='object') return '{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+stable(value[k])).join(',')+'}';
  return JSON.stringify(value);
}
async function sha256(value){
  let bytes;
  if(value instanceof ArrayBuffer) bytes=new Uint8Array(value);
  else if(ArrayBuffer.isView(value)) bytes=new Uint8Array(value.buffer,value.byteOffset,value.byteLength);
  else if(typeof Blob!=='undefined' && value instanceof Blob) bytes=new Uint8Array(await value.arrayBuffer());
  else bytes=new TextEncoder().encode(typeof value==='string'?value:stable(value));
  if(global.crypto && global.crypto.subtle){
    const digest=await global.crypto.subtle.digest('SHA-256',bytes);
    return Array.from(new Uint8Array(digest)).map(x=>x.toString(16).padStart(2,'0')).join('');
  }
  // Fallback is intentionally not a cryptographic proof. It exists only for
  // unsupported test runtimes; production WebView/Safari/Chrome use WebCrypto.
  let h=2166136261;
  for(const b of bytes){h^=b;h=Math.imul(h,16777619)}
  return ('fallback-'+(h>>>0).toString(16).padStart(8,'0'));
}

function bytesToB64(bytes){
  let s='';for(const b of bytes)s+=String.fromCharCode(b);
  return global.btoa?global.btoa(s):Buffer.from(bytes).toString('base64');
}
function b64ToBytes(s){
  const bin=global.atob?global.atob(s):Buffer.from(s,'base64').toString('binary');
  const out=new Uint8Array(bin.length);for(let i=0;i<bin.length;i++)out[i]=bin.charCodeAt(i);return out;
}
async function pinHash(pin,saltB64){
  if(!/^\d{4}$/.test(String(pin||'')))throw new Error('PIN_MUST_BE_4_DIGITS');
  if(!global.crypto?.subtle)throw new Error('WEBCRYPTO_REQUIRED_FOR_PIN');
  const key=await global.crypto.subtle.importKey('raw',new TextEncoder().encode(String(pin)),'PBKDF2',false,['deriveBits']);
  const bits=await global.crypto.subtle.deriveBits({name:'PBKDF2',salt:b64ToBytes(saltB64),iterations:150000,hash:'SHA-256'},key,256);
  return bytesToB64(new Uint8Array(bits));
}

function b64ToBlob(base64,mime='application/octet-stream'){
  const bin=global.atob?global.atob(base64):Buffer.from(base64,'base64').toString('binary');
  const arr=new Uint8Array(bin.length);for(let i=0;i<bin.length;i++)arr[i]=bin.charCodeAt(i);
  return new Blob([arr],{type:mime});
}

class MemoryStore{
  constructor(){this.db=new Map();for(const n of STORE_NAMES)this.db.set(n,new Map())}
  async open(){return this}
  async get(store,key){const v=this.db.get(store).get(String(key));return v===undefined?undefined:deepClone(v)}
  async put(store,key,value){this.db.get(store).set(String(key),deepClone(value));return key}
  async delete(store,key){this.db.get(store).delete(String(key))}
  async clear(store){this.db.get(store).clear()}
  async all(store){return Array.from(this.db.get(store).values()).map(deepClone)}
  async keys(store){return Array.from(this.db.get(store).keys())}
}

class IndexedDbStore{
  constructor(name='OI_PROVOWARE_IO_MOBILE_V1'){this.name=name;this.db=null}
  open(){
    if(this.db)return Promise.resolve(this);
    return new Promise((resolve,reject)=>{
      const req=indexedDB.open(this.name,2);
      req.onupgradeneeded=()=>{for(const n of STORE_NAMES)if(!req.result.objectStoreNames.contains(n))req.result.createObjectStore(n)};
      req.onsuccess=()=>{this.db=req.result;resolve(this)};req.onerror=()=>reject(req.error);
    })
  }
  _req(store,mode,fn){return new Promise((resolve,reject)=>{const tx=this.db.transaction(store,mode),os=tx.objectStore(store),r=fn(os);r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error);tx.onabort=()=>reject(tx.error)})}
  get(s,k){return this._req(s,'readonly',os=>os.get(String(k)))}
  put(s,k,v){return this._req(s,'readwrite',os=>os.put(v,String(k)))}
  delete(s,k){return this._req(s,'readwrite',os=>os.delete(String(k)))}
  clear(s){return this._req(s,'readwrite',os=>os.clear())}
  all(s){return this._req(s,'readonly',os=>os.getAll())}
  keys(s){return this._req(s,'readonly',os=>os.getAllKeys())}
}

class MobileCore{
  constructor(storage,nativeBridge={}){
    this.storage=storage;this.native=nativeBridge;this.profile=null;
    this.ready=false;this.recording=false;this.mutationCount=0;this.assetQuota=2*1024*1024*1024;
  }
  async init(){
    if(this.ready)return this;
    await this.storage.open();
    if(!await this.storage.get('meta','profiles'))await this.storage.put('meta','profiles',[]);
    // A stored profile hint may preselect the login UI, but a PIN is required
    // again for every native app session. No persisted "unlocked" flag exists.
    this.ready=true;return this;
  }
  _requireProfile(){if(!this.profile)throw new Error('PROFILE_AUTH_REQUIRED');return this.profile}
  _pk(name){this._requireProfile();return `${name}:${this.profile.id}`}
  async _ensureProfileDefaults(){
    const ck=this._pk('colors'),sk=this._pk('settings'),qk=this._pk('quicknotes');
    if(!await this.storage.get('meta',ck))await this.storage.put('meta',ck,DEFAULT_COLORS.map(x=>({...x,id:`${this.profile.id}-${x.id}`})));
    if(!await this.storage.get('meta',sk))await this.storage.put('meta',sk,{font_scale:1,help_mode:2,theme:'neon-core'});
    if(!await this.storage.get('meta',qk))await this.storage.put('meta',qk,{});
  }
  async listProfiles(){return (await this.storage.get('meta','profiles')||[]).map(p=>({id:p.id,name:p.name,created_at:p.created_at}))}
  async createProfile(name,pin){
    name=String(name||'').trim();if(!name)throw new Error('PROFILE_NAME_EMPTY');if(!/^\d{4}$/.test(String(pin||'')))throw new Error('PIN_MUST_BE_4_DIGITS');
    const profiles=await this.storage.get('meta','profiles')||[];if(profiles.some(p=>p.name.toLowerCase()===name.toLowerCase()))throw new Error('PROFILE_NAME_EXISTS');
    const salt=new Uint8Array(16);global.crypto.getRandomValues(salt);const saltB64=bytesToB64(salt),hash=await pinHash(pin,saltB64);const p={id:uuid(),name,salt:saltB64,pin_hash:hash,created_at:nowIso()};profiles.push(p);await this.storage.put('meta','profiles',profiles);await this.storage.put('meta','lastProfileId',p.id);this.profile={id:p.id,name:p.name};await this._ensureProfileDefaults();return {id:p.id,name:p.name}
  }
  async verifyProfile(profileId,pin){
    const profiles=await this.storage.get('meta','profiles')||[],p=profiles.find(x=>x.id===profileId);if(!p)throw new Error('PROFILE_NOT_FOUND');const hash=await pinHash(pin,p.salt);if(hash!==p.pin_hash)throw new Error('PIN_INVALID');await this.storage.put('meta','lastProfileId',p.id);this.profile={id:p.id,name:p.name};await this._ensureProfileDefaults();return {id:p.id,name:p.name}
  }
  async lockProfile(){this.profile=null}
  async _verified(entity){
    if(!entity)return entity;
    const expected=await sha256({title:entity.title,payload:entity.payload,revision:entity.revision,status:entity.status});
    if(entity.checksum && entity.checksum!==expected)throw new Error('CHECKSUM_MISMATCH');
    return entity;
  }
  async _putEntity(entity){
    entity.checksum=await sha256({title:entity.title,payload:entity.payload,revision:entity.revision,status:entity.status});
    await this.storage.put('entities',entity.id,entity);return entity;
  }
  async _entity(id){const e=await this.storage.get('entities',id);if(e&&e.profile_id!==this._requireProfile().id)return null;return this._verified(e)}
  async _list(type,includeTrash=false){
    const all=await this.storage.all('entities');
    const out=[];const profile=this._requireProfile();for(const e of all){if(e.profile_id===profile.id&&e.entity_type===type && (includeTrash||e.status==='ACTIVE'))out.push(await this._verified(e))}
    out.sort((a,b)=>String(b.updated_at).localeCompare(String(a.updated_at)));return out;
  }
  async _clearRedo(){for(const u of await this.storage.all('undo'))if(u.profile_id===this._requireProfile().id&&u.state==='UNDONE')await this.storage.delete('undo',u.id)}
  async _recordUndo(type,target,before,after){
    await this._clearRedo();const u={id:uuid(),profile_id:this._requireProfile().id,type,target,before:before?deepClone(before):null,after:after?deepClone(after):null,state:'READY',created_at:nowIso()};
    await this.storage.put('undo',u.id,u);return u.id;
  }
  async _afterMutation(){
    this.mutationCount++;
    if(this.mutationCount%20===0)await this.createStructuredBackup();
  }
  async createEntity(type,title,payload){
    title=String(title||'').trim();if(!title)throw new Error(type==='memo'?'MEMO_TITLE_REQUIRED':type==='todo'?'TODO_TITLE_REQUIRED':'EVENT_TITLE_REQUIRED');
    const profile=this._requireProfile();const t=nowIso();const e={id:uuid(),profile_id:profile.id,entity_type:type,schema_version:2,revision:1,status:'ACTIVE',title,payload:deepClone(payload||{}),created_at:t,updated_at:t,deleted_at:null};
    await this._putEntity(e);await this._recordUndo(type+'.create',e.id,null,e);await this._afterMutation();await this._syncReminder(e);return deepClone(e);
  }
  async editEntity(id,revision,title,payload,op='edit'){
    const before=await this._entity(id);if(!before)throw new Error('ENTITY_NOT_FOUND');if(Number(revision)!==Number(before.revision))throw new Error('REVISION_CONFLICT');
    const after=deepClone(before);after.title=String(title||'').trim();if(!after.title)throw new Error('TITLE_REQUIRED');after.payload=deepClone(payload);after.revision++;after.updated_at=nowIso();
    await this._putEntity(after);await this._recordUndo(before.entity_type+'.'+op,id,before,after);await this._afterMutation();await this._syncReminder(after);return deepClone(after);
  }
  async trash(id,revision){
    const before=await this._entity(id);if(!before)throw new Error('ENTITY_NOT_FOUND');if(Number(revision)!==Number(before.revision))throw new Error('REVISION_CONFLICT');
    const after=deepClone(before);after.status='TRASHED';after.deleted_at=nowIso();after.updated_at=after.deleted_at;after.revision++;
    await this._putEntity(after);await this._recordUndo(before.entity_type+'.trash',id,before,after);await this._afterMutation();await this._syncReminder(after);return after;
  }
  async restore(id,revision){
    const before=await this._entity(id);if(!before)throw new Error('ENTITY_NOT_FOUND');if(before.status!=='TRASHED')throw new Error('ENTITY_NOT_TRASHED');if(Number(revision)!==Number(before.revision))throw new Error('REVISION_CONFLICT');
    const after=deepClone(before);after.status='ACTIVE';after.deleted_at=null;after.updated_at=nowIso();after.revision++;
    await this._putEntity(after);await this._recordUndo(before.entity_type+'.restore',id,before,after);await this._afterMutation();await this._syncReminder(after);return after;
  }
  async _applyUndoSnapshot(snapshot,targetId){
    const cur=await this._entity(targetId);
    if(snapshot===null){if(cur){cur.status='TRASHED';cur.deleted_at=nowIso();cur.revision++;cur.updated_at=nowIso();await this._putEntity(cur)}return}
    const next=deepClone(snapshot);next.revision=(cur?.revision||snapshot.revision)+1;next.updated_at=nowIso();await this._putEntity(next);
  }
  async undo(){
    const list=(await this.storage.all('undo')).filter(x=>x.profile_id===this._requireProfile().id&&x.state==='READY').sort((a,b)=>String(b.created_at).localeCompare(String(a.created_at)));
    if(!list.length)throw new Error('UNDO_EMPTY');const u=list[0];await this._applyUndoSnapshot(u.before,u.target);u.state='UNDONE';u.applied_at=nowIso();await this.storage.put('undo',u.id,u);return {target:u.target}
  }
  async redo(){
    const list=(await this.storage.all('undo')).filter(x=>x.profile_id===this._requireProfile().id&&x.state==='UNDONE').sort((a,b)=>String(b.applied_at||b.created_at).localeCompare(String(a.applied_at||a.created_at)));
    if(!list.length)throw new Error('REDO_EMPTY');const u=list[0];await this._applyUndoSnapshot(u.after,u.target);u.state='READY';u.applied_at=nowIso();await this.storage.put('undo',u.id,u);return {target:u.target}
  }
  async colors(){return deepClone(await this.storage.get('meta',this._pk('colors'))||DEFAULT_COLORS)}
  async setColors(entries){if(!Array.isArray(entries)||entries.length!==5)throw new Error('CALENDAR_REQUIRES_EXACTLY_FIVE_COLORS');const old=await this.colors();const next=entries.map((x,i)=>({id:old[i]?.id||uuid(),title:String(x.title||'').trim()||`Farbe ${i+1}`,token:String(x.token||'').trim()||DEFAULT_COLORS[i].token,order:i}));await this.storage.put('meta',this._pk('colors'),next);await this._afterMutation();return next}
  async dayColors(){const arr=await this._list('calendar_day_color');const out={};for(const e of arr)out[e.payload.day]={id:e.id,color_id:e.payload.color_id,revision:e.revision};return out}
  async setDayColor(day,colorId){const arr=await this._list('calendar_day_color');const old=arr.find(x=>x.payload.day===day);if(old)return this.editEntity(old.id,old.revision,day,{day,color_id:colorId},'day-color');return this.createEntity('calendar_day_color',day,{day,color_id:colorId})}
  async nextItems(limit=10){const all=[...(await this._list('todo')),...(await this._list('calendar_event'))].filter(x=>!x.payload.completed);all.sort((a,b)=>String(a.payload.due_at||a.payload.start_at||'9999').localeCompare(String(b.payload.due_at||b.payload.start_at||'9999')));return all.slice(0,limit)}
  async counts(){const all=await this.storage.all('entities'),pid=this._requireProfile().id;return {memos:all.filter(x=>x.profile_id===pid&&x.entity_type==='memo'&&x.status==='ACTIVE').length,todos:all.filter(x=>x.profile_id===pid&&x.entity_type==='todo'&&x.status==='ACTIVE').length,events:all.filter(x=>x.profile_id===pid&&x.entity_type==='calendar_event'&&x.status==='ACTIVE').length,trash:all.filter(x=>x.profile_id===pid&&x.status==='TRASHED').length}}
  async backupStatus(){const pid=this._requireProfile().id,all=(await this.storage.all('backups')).filter(x=>x.profile_id===pid);return {generations:all.length,state:all.length?'READY':'EMPTY',label:all.length?`${all.length} Gen.`:'Noch keine'}}
  async state(){return {version:global.PROVOWARE_BUILD_INFO?.version||'UNKNOWN',profile:this.profile,settings:await this.settings(),counts:await this.counts(),next:await this.nextItems(10),colors:await this.colors(),day_colors:await this.dayColors(),integrity:'ok',asset_quota:await this.assetQuotaStatus(),backup:await this.backupStatus()}}
  async settings(){return await this.storage.get('meta',this._pk('settings'))||{font_scale:1,help_mode:2,theme:'NEON_TUERKIS'}}
  async setSettings(body){const prev=await this.settings(),next={...prev,...deepClone(body||{})};await this.storage.put('meta',this._pk('settings'),next);return next}
  async reminderPending(){
    const now=Date.now(),out=[];for(const e of [...await this._list('todo'),...await this._list('calendar_event')]){const r=e.payload.reminder_at;if(!r||new Date(r).getTime()>now)continue;const key=this._pk(`reminder:${e.id}:${r}`);if(!await this.storage.get('meta',key))out.push(e)}return out
  }
  async markReminderDelivered(e){if(e?.payload?.reminder_at)await this.storage.put('meta',this._pk(`reminder:${e.id}:${e.payload.reminder_at}`),{delivered_at:nowIso()})}
  async _syncReminder(e){
    if(!e)return;
    const shouldCancel=e.status!=='ACTIVE'||e.payload?.completed||!e.payload?.reminder_at;
    if(shouldCancel){if(typeof this.native.cancelReminder==='function')try{await this.native.cancelReminder({id:e.id})}catch(_){};return}
    if(typeof this.native.cancelReminder==='function')try{await this.native.cancelReminder({id:e.id})}catch(_){}
    if(typeof this.native.scheduleReminder==='function')try{await this.native.scheduleReminder({id:e.id,title:e.title,body:e.payload.description||'Erinnerung',at:e.payload.reminder_at})}catch(_){}
  }
  async platformCapabilities(){const info=typeof this.native.platformInfo==='function'?await this.native.platformInfo():{platform:'mobile-web-runtime',native_bridge:false};return {mobile:info,android:{evidence_type:info.platform==='android'?'NATIVE_BRIDGE_RUNTIME':'NOT_THIS_PLATFORM'},ios:{evidence_type:info.platform==='ios'?'NATIVE_BRIDGE_RUNTIME':'NOT_THIS_PLATFORM'}}}
  async quickNote(body){const title=String(body?.title||'Notizen').trim()||'Notizen',text=String(body?.text||'');const notes=await this.storage.get('meta',this._pk('quicknotes'))||{};notes[title]=(notes[title]||'')+`[${new Date().toLocaleString()}] ${text}\n`;await this.storage.put('meta',this._pk('quicknotes'),notes);return {title,text_length:notes[title].length}}
  async shareQuick(title){const notes=await this.storage.get('meta',this._pk('quicknotes'))||{},text=notes[title]||'';if(typeof this.native.shareText==='function'){await this.native.shareText({title,text});return {opened:true}}return {opened:false}}
  async diagnosticsPreview(){return {tool:'OI - PROVOWARE - IO',version:global.PROVOWARE_BUILD_INFO?.version||'UNKNOWN',timestamp:nowIso(),profile:this.profile.name,platform:await this.platformCapabilities(),integrity:'ok',counts:await this.counts(),asset_quota:await this.assetQuotaStatus(),privacy:{memo_contents:'NICHT ENTHALTEN',pin:'NICHT ENTHALTEN',tokens:'NICHT ENTHALTEN',full_home_path:'NICHT VERWENDET'}}}
  async diagnosticsCreate(){const p=await this.diagnosticsPreview();const text='OI - PROVOWARE - IO – MOBILE DIAGNOSE\n'+JSON.stringify(p,null,2);const blob=new Blob([text],{type:'text/plain'});return this.importBlob(blob,'diagnose.txt','document','Diagnose')}
  async _profileMetaSnapshot(pid){
    const out=[];for(const key of await this.storage.keys('meta')){const k=String(key);if(k.endsWith(':'+pid))out.push({key:k,value:await this.storage.get('meta',k)})}return out
  }
  async _assetBackupEntries(pid){
    const metas=(await this.storage.all('assetMeta')).filter(x=>x.profile_id===pid&&x.status==='ACTIVE'),entries=[];
    for(const meta of metas){
      const keys=[{source_key:meta.asset_id,sha256:meta.sha256,role:'current'}];
      for(const h of meta.revision_history||[])if(h.snapshot_key)keys.push({source_key:h.snapshot_key,sha256:h.sha256,role:'revision'});
      for(const item of keys){const blob=await this.storage.get('assets',item.source_key);if(!blob)throw new Error('BACKUP_ASSET_MISSING');const digest=await sha256(blob);if(digest!==item.sha256)throw new Error('BACKUP_ASSET_CHECKSUM_MISMATCH');entries.push({...item,asset_id:meta.asset_id,size_bytes:blob.size||0,blob})}
    }
    return {metas,entries}
  }
  async createStructuredBackup(){
    const pid=this._requireProfile().id,entities=(await this.storage.all('entities')).filter(x=>x.profile_id===pid),undo=(await this.storage.all('undo')).filter(x=>x.profile_id===pid),profile_meta=await this._profileMetaSnapshot(pid),assets=await this._assetBackupEntries(pid),backupId=uuid();
    const bytes=assets.entries.reduce((sum,x)=>sum+(x.size_bytes||0),0);
    if(global.navigator?.storage?.estimate){const e=await global.navigator.storage.estimate();if(Number.isFinite(e.quota)&&Number.isFinite(e.usage)&&(e.quota-e.usage)<bytes+5*1024*1024)throw new Error('BACKUP_STORAGE_INSUFFICIENT')}
    const backup={id:backupId,profile_id:pid,created_at:nowIso(),entities,undo,profile_meta,asset_meta:assets.metas,asset_entries:assets.entries.map(({blob,...x})=>x),asset_bytes:bytes,binary_redundancy:'FULL_COPY_PER_GENERATION'};
    for(const item of assets.entries)await this.storage.put('backupAssets',`${backupId}:${item.source_key}`,item.blob);
    await this.storage.put('backups',backup.id,backup);
    const all=(await this.storage.all('backups')).filter(x=>x.profile_id===pid);all.sort((a,b)=>String(b.created_at).localeCompare(String(a.created_at)));
    for(const b of all.slice(4)){for(const key of await this.storage.keys('backupAssets'))if(String(key).startsWith(b.id+':'))await this.storage.delete('backupAssets',key);await this.storage.delete('backups',b.id)}
    return backup
  }
  async validateStructuredBackup(backupId){
    const b=await this.storage.get('backups',backupId);if(!b||b.profile_id!==this._requireProfile().id)throw new Error('BACKUP_NOT_FOUND');
    let checked=0;for(const item of b.asset_entries||[]){const blob=await this.storage.get('backupAssets',`${b.id}:${item.source_key}`);if(!blob)throw new Error('BACKUP_BINARY_MISSING');if(await sha256(blob)!==item.sha256)throw new Error('BACKUP_BINARY_CHECKSUM_MISMATCH');checked++}
    return {id:b.id,profile_id:b.profile_id,entities:(b.entities||[]).length,assets:(b.asset_meta||[]).length,binary_entries:checked,asset_bytes:b.asset_bytes||0,status:'OK'}
  }
  async restoreStructuredBackup(backupId){
    const b=await this.storage.get('backups',backupId);if(!b||b.profile_id!==this._requireProfile().id)throw new Error('BACKUP_NOT_FOUND');await this.validateStructuredBackup(backupId);const pid=b.profile_id;
    for(const e of await this.storage.all('entities'))if(e.profile_id===pid)await this.storage.delete('entities',e.id);
    for(const u of await this.storage.all('undo'))if(u.profile_id===pid)await this.storage.delete('undo',u.id);
    for(const m of await this.storage.all('assetMeta'))if(m.profile_id===pid){await this.storage.delete('assets',m.asset_id);for(const h of m.revision_history||[])if(h.snapshot_key)await this.storage.delete('assets',h.snapshot_key);await this.storage.delete('assetMeta',m.asset_id)}
    for(const key of await this.storage.keys('meta'))if(String(key).endsWith(':'+pid))await this.storage.delete('meta',key);
    for(const e of b.entities||[])await this.storage.put('entities',e.id,e);for(const u of b.undo||[])await this.storage.put('undo',u.id,u);for(const m of b.asset_meta||[])await this.storage.put('assetMeta',m.asset_id,m);for(const m of b.profile_meta||[])await this.storage.put('meta',m.key,m.value);
    for(const item of b.asset_entries||[]){const blob=await this.storage.get('backupAssets',`${b.id}:${item.source_key}`);await this.storage.put('assets',item.source_key,blob)}
    return {restored:true,backup_id:b.id,entities:(b.entities||[]).length,assets:(b.asset_meta||[]).length}
  }
  async assetQuotaStatus(){const pid=this._requireProfile().id,metas=await this.storage.all('assetMeta');const used=metas.filter(x=>x.profile_id===pid&&x.status==='ACTIVE').reduce((s,x)=>s+(x.size_bytes||0),0);return {used,quota:this.assetQuota,free:Math.max(0,this.assetQuota-used),percent:+((used/this.assetQuota)*100).toFixed(2)}}
  async importBlob(blob,name,kind,title=''){
    if(!(blob instanceof Blob))throw new Error('ASSET_BLOB_REQUIRED');const ext=extOf(name),allowed=kind==='audio'?ALLOWED_AUDIO:kind==='document'?ALLOWED_DOC:[];if(!allowed.includes(ext))throw new Error('ASSET_EXTENSION_BLOCKED');const q=await this.assetQuotaStatus();if(q.used+blob.size>q.quota)throw new Error('ASSET_QUOTA_EXCEEDED');
    const pid=this._requireProfile().id,id=uuid(),digest=await sha256(blob),meta={asset_id:id,profile_id:pid,kind,title:title||String(name).replace(/\.[^.]+$/,''),original_name:name,stored_name:id+'.'+ext,size_bytes:blob.size,sha256:digest,created_at:nowIso(),status:'ACTIVE',revision:1};await this.storage.put('assets',id,blob);await this.storage.put('assetMeta',id,meta);await this._afterMutation();return meta
  }
  async listAssets(){const pid=this._requireProfile().id,all=await this.storage.all('assetMeta');return all.filter(x=>x.profile_id===pid&&x.status==='ACTIVE').sort((a,b)=>String(b.created_at).localeCompare(String(a.created_at)))}
  async getAssetBlob(id){const meta=await this.storage.get('assetMeta',id),blob=await this.storage.get('assets',id);if(!meta||!blob||meta.profile_id!==this._requireProfile().id)throw new Error('ASSET_FILE_MISSING');if(await sha256(blob)!==meta.sha256)throw new Error('ASSET_CHECKSUM_MISMATCH');return {meta,blob}}
  async assetUrl(id){const x=await this.getAssetBlob(id);return URL.createObjectURL(x.blob)}
  async readTextAsset(id){const x=await this.getAssetBlob(id);if(!/\.(txt|md)$/i.test(x.meta.original_name))throw new Error('ASSET_TEXT_EDIT_UNSUPPORTED');return {manifest:x.meta,text:await x.blob.text()}}
  async editTextAsset(id,text,revision){const x=await this.getAssetBlob(id);if(Number(revision)!==Number(x.meta.revision))throw new Error('ASSET_REVISION_CONFLICT');if(!/\.(txt|md)$/i.test(x.meta.original_name))throw new Error('ASSET_TEXT_EDIT_UNSUPPORTED');await this.storage.put('assets',`${id}:rev:${x.meta.revision}`,x.blob);const blob=new Blob([String(text)],{type:'text/plain'}),meta={...x.meta,revision:x.meta.revision+1,size_bytes:blob.size,sha256:await sha256(blob),updated_at:nowIso(),revision_history:[...(x.meta.revision_history||[]),{revision:x.meta.revision,sha256:x.meta.sha256,snapshot_key:`${id}:rev:${x.meta.revision}`,saved_at:nowIso()}].slice(-20)};await this.storage.put('assets',id,blob);await this.storage.put('assetMeta',id,meta);return meta}
  async audioCapability(){const info=await this.platformCapabilities();return {available:typeof this.native.audioStart==='function'&&typeof this.native.audioStop==='function',backend:'native-bridge',platform:info.mobile?.platform||'unknown',evidence:'NATIVE_RUNTIME_REQUIRED'} }
  async audioStart(){if(typeof this.native.audioStart!=='function')throw new Error('MICROPHONE_CAPTURE_UNAVAILABLE');await this.native.audioStart();this.recording=true;return {started:true}}
  async audioStop(title='Sprachmemo'){if(!this.recording)throw new Error('RECORDING_NOT_ACTIVE');if(typeof this.native.audioStop!=='function')throw new Error('MICROPHONE_CAPTURE_UNAVAILABLE');const out=await this.native.audioStop();this.recording=false;const blob=b64ToBlob(out.base64,out.mime||'audio/mp4');return this.importBlob(blob,out.name||'sprachmemo.m4a','audio',title)}
  async playlists(){return this._list('playlist')}
  async createPlaylist(title){return this.createEntity('playlist',title||'Playlist',{items:[],current_index:0,shuffle:false})}

  async request(path,method='GET',body={}){
    await this.init();method=String(method||'GET').toUpperCase();body=body||{};
    if(path==='/api/state'&&method==='GET')return this.state();
    if(path==='/api/memos'&&method==='GET')return this._list('memo');
    if(path==='/api/memos'&&method==='POST')return this.createEntity('memo',body.title,{body:body.body||'',tags:body.tags||[],pinned:false,archived:false});
    let m=path.match(/^\/api\/memos\/([^/]+)\/(edit|trash)$/);if(m){const e=await this._entity(m[1]);if(m[2]==='trash')return this.trash(m[1],body.revision);return this.editEntity(m[1],body.revision,body.title,{...e.payload,body:body.body||'',tags:body.tags||[]},'edit')}
    if(path==='/api/todos'&&method==='GET')return this._list('todo');
    if(path==='/api/todos'&&method==='POST'){if(body.reminder_at&&!body.due_at)throw new Error('REMINDER_REQUIRES_DUE_DATE');return this.createEntity('todo',body.title,{description:body.description||'',due_at:body.due_at||null,reminder_at:body.reminder_at||null,priority:body.priority||'NORMAL',completed:false,completed_at:null,archived:false})}
    m=path.match(/^\/api\/todos\/([^/]+)\/(edit|complete|trash)$/);if(m){const e=await this._entity(m[1]);if(m[2]==='trash')return this.trash(m[1],body.revision);if(m[2]==='complete')return this.editEntity(m[1],body.revision,e.title,{...e.payload,completed:true,completed_at:nowIso()},'complete');if(body.reminder_at&&!body.due_at)throw new Error('REMINDER_REQUIRES_DUE_DATE');return this.editEntity(m[1],body.revision,body.title,{...e.payload,description:body.description||'',due_at:body.due_at||null,reminder_at:body.reminder_at||null,priority:body.priority||'NORMAL'},'edit')}
    if(path==='/api/events'&&method==='GET')return this._list('calendar_event');
    if(path==='/api/events'&&method==='POST'){if(body.end_at&&body.start_at&&body.end_at<body.start_at)throw new Error('EVENT_END_BEFORE_START');return this.createEntity('calendar_event',body.title,{start_at:body.start_at,end_at:body.end_at||null,all_day:!!body.all_day,color_id:body.color_id||null,reminder_at:body.reminder_at||null,archived:false})}
    m=path.match(/^\/api\/events\/([^/]+)\/(edit|trash)$/);if(m){const e=await this._entity(m[1]);if(m[2]==='trash')return this.trash(m[1],body.revision);if(body.end_at&&body.start_at&&body.end_at<body.start_at)throw new Error('EVENT_END_BEFORE_START');return this.editEntity(m[1],body.revision,body.title,{...e.payload,start_at:body.start_at,end_at:body.end_at||null,all_day:!!body.all_day,color_id:body.color_id||null,reminder_at:body.reminder_at||null},'edit')}
    if(path==='/api/trash'&&method==='GET'){const pid=this._requireProfile().id,all=await this.storage.all('entities');return all.filter(x=>x.profile_id===pid&&x.status==='TRASHED').sort((a,b)=>String(b.updated_at).localeCompare(String(a.updated_at)))}
    m=path.match(/^\/api\/trash\/([^/]+)\/restore$/);if(m)return this.restore(m[1],body.revision);
    if(path==='/api/calendar/day-color'&&method==='POST')return this.setDayColor(body.day,body.color_id);
    if(path==='/api/calendar/colors'&&method==='POST')return this.setColors(body.entries);
    if(path==='/api/undo'&&method==='POST')return this.undo();if(path==='/api/redo'&&method==='POST')return this.redo();
    if(path==='/api/settings'&&method==='GET')return this.settings();if(path==='/api/settings'&&method==='POST')return this.setSettings(body);
    if(path==='/api/reminders/pending'&&method==='GET')return this.reminderPending();
    if(path==='/api/platform/capabilities'&&method==='GET')return this.platformCapabilities();
    if(path==='/api/quick-note'&&method==='POST')return this.quickNote(body);
    if(path==='/api/quick-note/open'&&method==='POST')return {opened:false,mobile:true};
    if(path==='/api/quick-note/share'&&method==='POST')return this.shareQuick(body.title||'Notizen');
    if(path==='/api/diagnostics/preview'&&method==='GET')return this.diagnosticsPreview();
    if(path==='/api/diagnostics/create'&&method==='POST'){if(body.confirmed!==true)throw new Error('DIAG_CONFIRM_REQUIRED');return this.diagnosticsCreate()}
    if(path==='/api/assets/quota'&&method==='GET')return this.assetQuotaStatus();
    if(path==='/api/assets/list'&&method==='GET')return this.listAssets();
    m=path.match(/^\/api\/assets\/([^/]+)\/text$/);if(m&&method==='GET')return this.readTextAsset(m[1]);
    if(path==='/api/assets/edit-text'&&method==='POST')return this.editTextAsset(body.asset_id,body.text,body.revision);
    if(path==='/api/assets/import'&&method==='POST')throw new Error('MOBILE_FILE_PICKER_REQUIRED');
    if(path==='/api/audio/capability'&&method==='GET')return this.audioCapability();
    if(path==='/api/audio/start'&&method==='POST')return this.audioStart();
    if(path==='/api/audio/stop'&&method==='POST')return this.audioStop(body.title||'Sprachmemo');
    if(path==='/api/playlists'&&method==='GET')return this.playlists();
    if(path==='/api/playlists'&&method==='POST')return this.createPlaylist(body.title);
    throw new Error('MOBILE_API_ROUTE_UNSUPPORTED: '+method+' '+path);
  }
}

global.ProvowareMobileCore={MobileCore,MemoryStore,IndexedDbStore,sha256,DEFAULT_COLORS};
if(typeof module!=='undefined'&&module.exports)module.exports=global.ProvowareMobileCore;
})(typeof globalThis!=='undefined'?globalThis:this);
