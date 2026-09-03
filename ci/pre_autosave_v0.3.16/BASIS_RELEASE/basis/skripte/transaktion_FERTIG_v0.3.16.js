const TX_KEY="memo_tx_aktiv_v1", INDEX_KEY="memo_index_v1", RECORD_PREFIX="memo_record_v1_";
function clone(v){return typeof structuredClone==="function"?structuredClone(v):JSON.parse(JSON.stringify(v))}
function now(){return new Date().toISOString()}
function cleanText(v,max){return String(v??"").trim().slice(0,max)}
function validMemo(m){return m&&typeof m.id==="string"&&m.id.length>0&&typeof m.title==="string"&&typeof m.text==="string"&&Number.isInteger(m.revision)&&m.revision>0}
function validStore(s){return s&&["setzen","holen","entfernen"].every(k=>typeof s[k]==="function")}
function uniqueIndex(x){return [...new Set(Array.isArray(x)?x.filter(v=>typeof v==="string"&&v.length):[])]}
export class MemoTransaktionsKern{
  constructor(speicher,protokoll=null){
    if(!validStore(speicher))throw new Error("NQ-TX-SPEICHER-UNGUELTIG");
    this.s=speicher;this.p=protokoll;this.letzteRecovery=null;this._queue=Promise.resolve();
  }
  async index(){return uniqueIndex(await this.s.holen(INDEX_KEY))}
  async lesen(id){return await this.s.holen(RECORD_PREFIX+cleanText(id,120))}
  async schreibe(memo,optionen={}){
    const task=()=>this.#schreibeIntern(memo,optionen);
    const run=this._queue.then(task,task);
    this._queue=run.catch(()=>undefined);
    return run;
  }
  async #schreibeIntern(memo,{killAt=null}={}){
    const id=cleanText(memo?.id,120), title=cleanText(memo?.title,200), text=String(memo?.text??"");
    if(!id)throw new Error("NQ-TX-ID-FEHLT");
    const alt=await this.lesen(id), idxAlt=await this.index();
    const neu={id,title,text,revision:(Number(alt?.revision)||0)+1,updatedAt:now()};
    const tx={schemaVersion:1,id:`tx-${Date.now()}-${Math.random().toString(16).slice(2)}`,memoId:id,status:"PREPARED",createdAt:now(),beforeRecord:alt?clone(alt):null,beforeIndex:clone(idxAlt),target:clone(neu)};
    await this.s.setzen(TX_KEY,tx);
    if(killAt==="after_journal")throw new Error("SIMULATED_KILL_AFTER_JOURNAL");
    await this.s.setzen(RECORD_PREFIX+id,neu);tx.status="RECORD_WRITTEN";await this.s.setzen(TX_KEY,tx);
    if(killAt==="after_record")throw new Error("SIMULATED_KILL_AFTER_RECORD");
    const idx=idxAlt.includes(id)?idxAlt:[...idxAlt,id];await this.s.setzen(INDEX_KEY,uniqueIndex(idx));tx.status="INDEX_WRITTEN";await this.s.setzen(TX_KEY,tx);
    if(killAt==="after_index")throw new Error("SIMULATED_KILL_AFTER_INDEX");
    const proof=await this.#verify(id,neu.revision);if(!proof.ok)throw new Error("NQ-TX-NACHPRUEFUNG_FEHLGESCHLAGEN");
    await this.s.entfernen(TX_KEY);
    this.p?.erfolg?.("NQ-TX-COMMIT",`Transaktion für ${id} vollständig bestätigt.`,{ort:"Transaktionskern / Commit",modul:"TRANSAKTION",technisch:proof});
    return clone(neu)
  }
  async recovery(){
    await this._queue;
    const tx=await this.s.holen(TX_KEY);
    if(!tx){this.letzteRecovery={ok:true,aktion:"NICHTS_ZU_TUN"};return clone(this.letzteRecovery)}
    if(!tx||tx.schemaVersion!==1||typeof tx.memoId!=="string"){
      this.letzteRecovery={ok:false,aktion:"JOURNAL_UNGUELTIG",memoId:tx?.memoId??null,proof:{ok:false}};
      this.p?.fehler?.("NQ-TX-JOURNAL-UNGUELTIG","Ein unterbrochener Schreibvorgang kann nicht sicher gelesen werden.",{ort:"Startzentrale / Recovery",modul:"TRANSAKTION",technisch:this.letzteRecovery});
      return clone(this.letzteRecovery)
    }
    const id=tx.memoId,target=tx.target;let action="";
    if(!validMemo(target)){await this.#rollback(tx);action="ROLLBACK_UNGUELTIGES_JOURNAL"}
    else{
      const record=await this.lesen(id),idx=await this.index();
      if(record&&record.revision===target.revision){if(!idx.includes(id))await this.s.setzen(INDEX_KEY,uniqueIndex([...idx,id]));action="FORWARD_COMPLETE"}
      else if(idx.includes(id)){const restored=uniqueIndex(tx.beforeIndex||[]);await this.s.setzen(INDEX_KEY,restored);if(tx.beforeRecord)await this.s.setzen(RECORD_PREFIX+id,tx.beforeRecord);else await this.s.entfernen(RECORD_PREFIX+id);action="ROLLBACK_INDEX_OHNE_RECORD"}
      else if(tx.status==="PREPARED"){await this.#rollback(tx);action="ROLLBACK_PREPARED"}
      else {await this.#rollback(tx);action="ROLLBACK_INKONSISTENT"}
    }
    const proof=await this.#verifyConsistency(id);
    if(proof.ok)await this.s.entfernen(TX_KEY);
    this.letzteRecovery={ok:proof.ok,aktion:action,memoId:id,proof,journalErhalten:!proof.ok};
    const method=proof.ok?"hinweis":"fehler";
    this.p?.[method]?.("NQ-TX-RECOVERY",proof.ok?`Unterbrochener Schreibvorgang wurde behandelt: ${action}.`:"Recovery konnte die Konsistenz nicht bestätigen; das Journal bleibt zur weiteren Reparatur erhalten.",{ort:"Startzentrale / Recovery",modul:"TRANSAKTION",technisch:this.letzteRecovery});
    return clone(this.letzteRecovery)
  }
  async #rollback(tx){if(tx.beforeRecord)await this.s.setzen(RECORD_PREFIX+tx.memoId,tx.beforeRecord);else await this.s.entfernen(RECORD_PREFIX+tx.memoId);await this.s.setzen(INDEX_KEY,uniqueIndex(tx.beforeIndex||[]))}
  async #verify(id,revision){const r=await this.lesen(id),idx=await this.index();return{ok:Boolean(r&&r.revision===revision&&idx.includes(id)),recordRevision:r?.revision||null,indexed:idx.includes(id)}}
  async #verifyConsistency(id){const r=await this.lesen(id),idx=await this.index();return{ok:Boolean(r)===idx.includes(id),recordExists:Boolean(r),indexed:idx.includes(id),indexDuplicates:idx.length!==new Set(idx).size}}
}
export const MEMO_TX_KEYS={TX_KEY,INDEX_KEY,RECORD_PREFIX};
