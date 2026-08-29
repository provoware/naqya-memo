await import('../../ui/reference_web/mobile/mobile_core.js');
const {MobileCore,MemoryStore}=globalThis.ProvowareMobileCore;
const core=new MobileCore(new MemoryStore(),{});await core.init();await core.createProfile('Parity','1234');
let m=await core.request('/api/memos','POST',{title:'M',body:'one',tags:[]});m=await core.request(`/api/memos/${m.id}/edit`,'POST',{revision:m.revision,title:'M2',body:'two',tags:['a']});
let t=await core.request('/api/todos','POST',{title:'T',description:'d',due_at:'2026-09-01T12:00:00.000Z',reminder_at:'2026-09-01T11:00:00.000Z',priority:'NORMAL'});t=await core.request(`/api/todos/${t.id}/complete`,'POST',{revision:t.revision});
let e=await core.request('/api/events','POST',{title:'E',start_at:'2026-09-02T10:00:00.000Z',end_at:'2026-09-02T11:00:00.000Z'});
const st=await core.request('/api/state');await core.request('/api/calendar/day-color','POST',{day:'2026-09-02',color_id:st.colors[0].id});
const out={memo:{title:m.title,body:m.payload.body,revision:m.revision,status:m.status},todo:{completed:t.payload.completed,revision:t.revision,status:t.status},event:{title:e.title,revision:e.revision,status:e.status},colors:(await core.request('/api/state')).colors.length,day_color:!!(await core.request('/api/state')).day_colors['2026-09-02']};
console.log(JSON.stringify(out));
