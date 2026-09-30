import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const source=fs.readFileSync(new URL('../../ui/reference_web/mutation_status_ui.js',import.meta.url),'utf8');
const listeners=new Map();
const attrs=new Map();
const formAttrs=new Map();
const form={
  getAttribute:name=>formAttrs.has(name)?formAttrs.get(name):null,
  setAttribute:(name,value)=>formAttrs.set(name,String(value)),
  removeAttribute:name=>formAttrs.delete(name)
};
const trigger={
  dataset:{},
  classList:{values:new Set(),add(v){this.values.add(v)},remove(v){this.values.delete(v)}},
  disabled:false,
  textContent:'Speichern',
  form,
  isConnected:true,
  getAttribute:name=>attrs.has(name)?attrs.get(name):null,
  setAttribute:(name,value)=>attrs.set(name,String(value)),
  removeAttribute:name=>attrs.delete(name)
};
const clickTarget={closest:()=>trigger};
let nativeCalls=0;
let mode='resolve';
let pendingResolve;
let pendingReject;
function nativeFetch(){
  nativeCalls++;
  return new Promise((resolve,reject)=>{
    pendingResolve=resolve;pendingReject=reject;
    if(mode==='immediate')resolve(new Response(JSON.stringify({ok:true,data:{id:1}}),{status:200,headers:{'content-type':'application/json'}}));
    if(mode==='reject')reject(new Error('network down'));
  });
}
const document={
  activeElement:null,
  head:{appendChild:()=>{}},
  createElement:()=>({}),
  addEventListener:(name,fn)=>listeners.set(name,fn),
  getElementById:()=>null
};
const context={
  window:{fetch:nativeFetch},
  document,
  location:{href:'http://127.0.0.1:5173/',origin:'http://127.0.0.1:5173'},
  URL,URLSearchParams,FormData,Blob,ArrayBuffer,Object,Date,Promise,Response,
  console,setTimeout,clearTimeout
};
context.window.window=context.window;
vm.createContext(context);
vm.runInContext(source,context,{filename:'mutation_status_ui.js'});

listeners.get('click')({target:clickTarget});
const first=context.window.fetch('/api/memos',{method:'POST',body:'{"title":"A"}'});
const second=context.window.fetch('/api/memos',{method:'POST',body:'{"title":"A"}'});
await Promise.resolve();
assert.equal(nativeCalls,1,'duplicate POST must call native fetch once');
assert.equal(trigger.disabled,true);
assert.equal(trigger.textContent,'Wird gespeichert …');
assert.equal(formAttrs.get('aria-busy'),'true');
assert.equal(attrs.get('aria-disabled'),'true');

pendingResolve(new Response(JSON.stringify({ok:true,data:{id:1}}),{status:200,headers:{'content-type':'application/json'}}));
const [r1,r2]=await Promise.all([first,second]);
assert.deepEqual(await r1.json(),{ok:true,data:{id:1}});
assert.deepEqual(await r2.json(),{ok:true,data:{id:1}});
assert.equal(trigger.disabled,false);
assert.equal(trigger.textContent,'Speichern');
assert.equal(formAttrs.has('aria-busy'),false);
assert.equal(attrs.has('aria-disabled'),false);

mode='immediate';
const getResponse=await context.window.fetch('/api/state',{method:'GET'});
assert.equal(nativeCalls,2,'GET must pass through untouched');
assert.equal((await getResponse.json()).ok,true);

mode='reject';
listeners.get('click')({target:clickTarget});
await assert.rejects(context.window.fetch('/api/todos',{method:'POST',body:'{"title":"B"}'}));
assert.equal(trigger.disabled,false,'failure must restore trigger');
assert.equal(trigger.textContent,'Speichern','failure must restore label');
assert.equal(formAttrs.has('aria-busy'),false,'failure must clear aria-busy');

console.log('PASS mutation status runtime dedupe + restoration');
