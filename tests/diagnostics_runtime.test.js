'use strict';

const assert=require('node:assert/strict');
const memory=new Map();
global.localStorage={
  getItem:key=>memory.has(key)?memory.get(key):null,
  setItem:(key,value)=>memory.set(key,String(value)),
  removeItem:key=>memory.delete(key)
};

require('../services/diagnostics.js');
const diag=global.NAQYA.diagnostics;

(async()=>{
  diag.clear();
  const first=diag.record('NAQYA-STT-4002',{
    where:'live-stt.segment',
    how:'lokaler Test',
    result:'Segment fehlgeschlagen',
    context:{transcript:'streng geheim',token:'abc123',path:'/home/alice/private/model.gguf',nested:{content:'Dokumentinhalt'}}
  });
  const second=diag.record('NAQYA-STT-4002',{
    where:'live-stt.segment',
    how:'lokaler Test',
    result:'Segment fehlgeschlagen'
  });
  assert.equal(first.event_id,second.event_id,'identische Kurzzeitfehler müssen dedupliziert werden');
  assert.equal(diag.snapshot().length,1);
  assert.equal(diag.snapshot()[0].repeat_count,2);
  assert.equal(diag.snapshot()[0].context.transcript,'[REDACTED]');
  assert.equal(diag.snapshot()[0].context.token,'[REDACTED]');
  assert.equal(diag.snapshot()[0].context.nested.content,'[REDACTED]');
  assert.equal(diag.snapshot()[0].context.path,'[pfad]/model.gguf');

  for(let i=0;i<205;i++)diag.record('NAQYA-APP-1002',{where:`runtime-${i}`,result:`Fehler-${i}`});
  assert.equal(diag.snapshot().length,200,'Ringpuffer muss hart auf 200 Ereignisse begrenzt sein');

  let retries=0;
  const retryEvent=diag.record('NAQYA-RUNTIME-6003',{
    where:'runtime.retry-test',result:'temporärer Fehler',options:['retry-once'],retry:async()=>{retries+=1}
  });
  await diag.executeAction('retry-once',retryEvent.event_id);
  await diag.executeAction('retry-once',retryEvent.event_id);
  assert.equal(retries,1,'Wiederholen darf pro Ereignis höchstens einmal ausgeführt werden');

  const payload=diag.exportPayload();
  assert.equal(payload.format,'NAQYA-DIAGNOSTICS');
  assert.equal(payload.schema_version,1);
  assert.ok(payload.events.every(event=>!Object.prototype.hasOwnProperty.call(event,'dedupe_key')),'interner Dedupe-Schlüssel darf nicht exportiert werden');
  assert.ok(JSON.stringify(payload).includes('NAQYA-RUNTIME-6003'));
  assert.ok(!JSON.stringify(payload).includes('streng geheim'));
  assert.ok(!JSON.stringify(payload).includes('abc123'));

  console.log('NAQYA Diagnose-Laufzeitregression: PASS');
})().catch(error=>{console.error(error);process.exit(1)});
