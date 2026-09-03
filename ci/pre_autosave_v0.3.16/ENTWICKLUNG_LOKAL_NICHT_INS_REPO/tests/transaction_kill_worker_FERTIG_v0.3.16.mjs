import fs from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import {MemoTransaktionsKern, MEMO_TX_KEYS} from '../../BASIS_RELEASE/basis/skripte/transaktion_FERTIG_v0.3.16.js';

const [mode, storeDir, scenario=''] = process.argv.slice(2);
if(!mode || !storeDir){console.error('usage: worker <write|recover|stress> <storeDir> [scenario]');process.exit(64)}
await fs.mkdir(storeDir,{recursive:true});
const marker=path.join(storeDir,'PHASE.marker');
const keyPath=k=>path.join(storeDir,Buffer.from(k).toString('base64url')+'.json');
class FileStore{
  async setzen(k,v){
    const p=keyPath(k),tmp=p+'.tmp';
    await fs.writeFile(tmp,JSON.stringify(v),'utf8');
    await fs.rename(tmp,p);
    if(k===MEMO_TX_KEYS.TX_KEY && v?.status){
      const phase=v.status;
      const wanted=scenario==='after_journal'?'PREPARED':scenario==='after_record'?'RECORD_WRITTEN':scenario==='after_index'?'INDEX_WRITTEN':'';
      if(mode==='write' && phase===wanted){
        await fs.writeFile(marker,phase,'utf8');
        // Parent process performs the real OS-level kill while the worker is paused here.
        await new Promise(()=>{});
      }
    }
  }
  async holen(k){try{return JSON.parse(await fs.readFile(keyPath(k),'utf8'))}catch(e){if(e?.code==='ENOENT')return null;throw e}}
  async entfernen(k){try{await fs.unlink(keyPath(k))}catch(e){if(e?.code!=='ENOENT')throw e}}
}
const store=new FileStore();
const tx=new MemoTransaktionsKern(store);
if(mode==='write'){
  await tx.schreibe({id:'kill-memo',title:'Kill Probe',text:'Datensatz für echten Prozessabbruch'});
  console.log(JSON.stringify({ok:true,mode:'write',scenario}));
}else if(mode==='recover'){
  const recovery=await tx.recovery();
  const record=await tx.lesen('kill-memo');
  const index=await tx.index();
  const journal=await store.holen(MEMO_TX_KEYS.TX_KEY);
  console.log(JSON.stringify({ok:Boolean(recovery.ok)&&Boolean(record)===index.includes('kill-memo')&&!journal,recovery,recordExists:Boolean(record),indexed:index.includes('kill-memo'),journalExists:Boolean(journal)}));
}else if(mode==='stress'){
  class MemStore{constructor(){this.m=new Map()}async setzen(k,v){this.m.set(k,structuredClone(v))}async holen(k){return this.m.has(k)?structuredClone(this.m.get(k)):null}async entfernen(k){this.m.delete(k)}}
  const fastTx=new MemoTransaktionsKern(new MemStore());
  const start=performance.now();
  for(let i=0;i<5000;i++)await fastTx.schreibe({id:`m-${i}`,title:`Memo ${i}`,text:`Text ${i}`});
  const idx=await fastTx.index();
  const samples=[];
  for(let i=0;i<5000;i+=499){const r=await fastTx.lesen(`m-${i}`);samples.push({id:`m-${i}`,ok:r?.title===`Memo ${i}`})}
  console.log(JSON.stringify({ok:idx.length===5000&&samples.every(x=>x.ok),count:idx.length,durationMs:Math.round(performance.now()-start),samples,store:'isolierter Arbeitsspeicher; gleicher Transaktionskern'}));
}else{console.error('unknown mode');process.exit(64)}
