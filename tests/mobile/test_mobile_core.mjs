import assert from 'node:assert/strict';
await import('../../ui/reference_web/mobile/mobile_core.js');
const {MobileCore,MemoryStore}=globalThis.ProvowareMobileCore;
const scheduled=[];
const native={
  async platformInfo(){return {platform:'android-test',native_bridge:true}},
  async scheduleReminder(x){scheduled.push(x);return {scheduled:true}},
  async shareText(){return {opened:true}},
  async audioStart(){return {started:true}},
  async audioStop(){return {base64:Buffer.from('FAKEAUDIO').toString('base64'),mime:'audio/mp4',name:'voice.m4a'}},
};
const core=new MobileCore(new MemoryStore(),native);await core.init();await core.createProfile('Test','1234');
let m=await core.request('/api/memos','POST',{title:'Memo',body:'eins',tags:['x']});
assert.equal(m.revision,1);m=await core.request(`/api/memos/${m.id}/edit`,'POST',{revision:1,title:'Memo 2',body:'zwei',tags:[]});assert.equal(m.revision,2);
await core.request(`/api/memos/${m.id}/trash`,'POST',{revision:2});let trash=await core.request('/api/trash');assert.equal(trash.length,1);
await core.request(`/api/trash/${m.id}/restore`,'POST',{revision:3});assert.equal((await core.request('/api/memos')).length,1);
let t=await core.request('/api/todos','POST',{title:'Todo',due_at:'2026-09-01T12:00:00.000Z',reminder_at:'2026-09-01T11:00:00.000Z',priority:'HOCH'});assert.ok(scheduled.length>=1);
let e=await core.request('/api/events','POST',{title:'Termin',start_at:'2026-09-02T10:00:00.000Z',end_at:'2026-09-02T11:00:00.000Z'});assert.equal(e.entity_type,'calendar_event');
const colors=(await core.request('/api/state')).colors;assert.equal(colors.length,5);await core.request('/api/calendar/day-color','POST',{day:'2026-09-02',color_id:colors[0].id});assert.ok((await core.request('/api/state')).day_colors['2026-09-02']);
await core.request('/api/undo','POST',{});await core.request('/api/redo','POST',{});
const txt=new Blob(['hallo'],{type:'text/plain'});let a=await core.importBlob(txt,'note.txt','document','Note');assert.equal(a.revision,1);let read=await core.request(`/api/assets/${a.asset_id}/text`);assert.equal(read.text,'hallo');a=await core.request('/api/assets/edit-text','POST',{asset_id:a.asset_id,text:'neu',revision:1});assert.equal(a.revision,2);
await core.request('/api/audio/start','POST',{});const audio=await core.request('/api/audio/stop','POST',{title:'Voice'});assert.equal(audio.kind,'audio');
const p=await core.request('/api/playlists','POST',{title:'Mix'});assert.equal(p.entity_type,'playlist');
const diag=await core.request('/api/diagnostics/preview');assert.equal(diag.privacy.pin,'NICHT ENTHALTEN');
const state=await core.request('/api/state');assert.equal(state.integrity,'ok');assert.equal(state.counts.memos,1);assert.equal(state.counts.todos,1);assert.equal(state.counts.events,1);
await core.createStructuredBackup();await core.createStructuredBackup();await core.createStructuredBackup();await core.createStructuredBackup();await core.createStructuredBackup();
const backups=await core.storage.all('backups');assert.equal(backups.length,4);for(const b of backups){const v=await core.validateStructuredBackup(b.id);assert.equal(v.status,'OK');assert.ok(v.binary_entries>=3);assert.ok(v.asset_bytes>0)}
a=await core.request('/api/assets/edit-text','POST',{asset_id:a.asset_id,text:'nach-backup',revision:2});assert.equal(a.revision,3);await core.restoreStructuredBackup(backups[0].id);read=await core.request(`/api/assets/${a.asset_id}/text`);assert.equal(read.text,'neu');assert.equal(read.manifest.revision,2);
const testProfile=core.profile.id;await core.lockProfile();let denied=false;try{await core.verifyProfile(testProfile,'0000')}catch(e){denied=e.message==='PIN_INVALID'}assert.equal(denied,true);await core.verifyProfile(testProfile,'1234');assert.equal((await core.request('/api/memos')).length,1);
await core.createProfile('Other','9999');assert.equal((await core.request('/api/memos')).length,0);await core.verifyProfile(testProfile,'1234');assert.equal((await core.listAssets()).length,2);
console.log(JSON.stringify({status:'PASS',memos:state.counts.memos,todos:state.counts.todos,events:state.counts.events,assets:(await core.listAssets()).length,backups:(await core.storage.all('backups')).length,profiles:(await core.listProfiles()).length,pin_guard:'PASS'}));
