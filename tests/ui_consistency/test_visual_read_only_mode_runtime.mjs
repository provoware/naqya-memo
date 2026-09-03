import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const mutationSource=fs.readFileSync(new URL('../../ui/reference_web/mutation_status_ui.js',import.meta.url),'utf8');
const readOnlySource=fs.readFileSync(new URL('../../ui/reference_web/read_only_ui.js',import.meta.url),'utf8');

function makeAttrs(){return new Map()}
const controlAttrs=makeAttrs();
const control={
 dataset:{},
 disabled:false,
 isConnected:true,
 title:'',
 form:null,
 matches:()=>true,
 closest:()=>control,
 getAttribute:name=>controlAttrs.has(name)?controlAttrs.get(name):null,
 setAttribute:(name,value)=>{controlAttrs.set(name,String(value));if(name==='title')control.title=String(value)},
 removeAttribute:name=>{controlAttrs.delete(name);if(name==='title')control.title=''}
};
const htmlClasses={values:new Set(),toggle(name,on){if(on)this.values.add(name);else this.values.delete(name)}};
const root={dataset:{mutationMode:'ready'},classList:htmlClasses};
const hint={hidden:true,setAttribute(){},innerHTML:'',id:'',className:''};
const toolbar={appendChild:node=>{hint.hidden=node.hidden;return node}};
const statusNotice={focusCalls:0,scrollCalls:0,attrs:new Map(),hasAttribute(name){return this.attrs.has(name)},setAttribute(name,v){this.attrs.set(name,String(v))},focus(){this.focusCalls++},scrollIntoView(){this.scrollCalls++}};
const documentListeners=new Map();
const windowListeners=new Map();
const document={
 documentElement:root,
 activeElement:null,
 head:{appendChild:()=>{}},
 createElement:tag=>tag==='span'?hint:{},
 getElementById:id=>id==='readOnlyToolbarHint'?null:id==='statusNotice'?statusNotice:null,
 querySelector:sel=>sel==='.workspace-toolbar'?toolbar:null,
 querySelectorAll:()=>[control],
 addEventListener:(name,fn)=>documentListeners.set(name,fn)
};
const MutationObserver=class{constructor(fn){this.fn=fn}observe(){}};
let nativeCalls=0;
async function nativeFetch(input,init){
 nativeCalls++;
 return new Response(JSON.stringify({ok:true,data:{path:String(input),method:init?.method||'GET'}}),{status:200,headers:{'content-type':'application/json'}});
}
const windowObj={
 fetch:nativeFetch,
 addEventListener:(name,fn)=>windowListeners.set(name,fn),
 dispatchEvent:event=>windowListeners.get(event.type)?.(event)
};
const context={
 window:windowObj,document,MutationObserver,
 location:{href:'http://127.0.0.1:5173/',origin:'http://127.0.0.1:5173'},
 URL,URLSearchParams,FormData,Blob,ArrayBuffer,Object,Date,Promise,Response,Set,WeakMap,
 CustomEvent:class{constructor(type,init={}){this.type=type;this.detail=init.detail}},
 console,setTimeout,clearTimeout
};
windowObj.window=windowObj;
vm.createContext(context);
vm.runInContext(readOnlySource,context,{filename:'read_only_ui.js'});
vm.runInContext(mutationSource,context,{filename:'mutation_status_ui.js'});

assert.equal(control.disabled,false,'READY must leave mutation controls enabled');
assert.equal(root.dataset.mutationMode,'ready');

root.dataset.mutationMode='degraded';
windowObj.dispatchEvent(new context.CustomEvent('provoware:mutation-mode',{detail:{degraded:true,mode:'DEGRADED'}}));
assert.equal(control.disabled,true,'DEGRADED must disable mutation controls');
assert.equal(controlAttrs.get('aria-disabled'),'true');
assert.equal(control.dataset.readonlyLocked,'1');
assert.match(control.title,/Nur-Lese-Modus/);
assert.equal(htmlClasses.values.has('read-only-active'),true);

const beforeBlocked=nativeCalls;
const blocked=await windowObj.fetch('/api/memos',{method:'POST',body:'{"title":"A"}'});
assert.equal(nativeCalls,beforeBlocked,'DEGRADED POST must not reach native fetch');
assert.equal(blocked.status,503);
const blockedPayload=await blocked.json();
assert.equal(blockedPayload.code,'MUTATION_DEGRADED_MODE');
assert.equal(blockedPayload.degraded_mode,true);

const getResponse=await windowObj.fetch('/api/state',{method:'GET'});
assert.equal(nativeCalls,beforeBlocked+1,'GET must remain available in read-only mode');
assert.equal((await getResponse.json()).ok,true);

root.dataset.mutationMode='ready';
windowObj.dispatchEvent(new context.CustomEvent('provoware:mutation-mode',{detail:{degraded:false,mode:'READY'}}));
assert.equal(control.disabled,false,'READY after restart must restore control state');
assert.equal(controlAttrs.has('aria-disabled'),false);
assert.equal(control.dataset.readonlyLocked,undefined);
assert.equal(htmlClasses.values.has('read-only-active'),false);

const writeResponse=await windowObj.fetch('/api/memos',{method:'POST',body:'{"title":"B"}'});
assert.equal(nativeCalls,beforeBlocked+2,'POST must be allowed again in READY mode');
assert.equal((await writeResponse.json()).ok,true);

console.log('PASS read-only UI lock + transport fail-closed + restart restore');
