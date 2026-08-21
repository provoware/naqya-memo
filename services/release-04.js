'use strict';

window.NAQYA=window.NAQYA||{};
// ENTWICKLERHINWEIS: Historischer Dateiname; Produktversion niemals erneut hart codieren. VERSION ist die kanonische PWA-/Backup-Quelle.
window.NAQYA.release={version:VERSION,phase:'TAURI-SIDECAR-INTEGRATION & REPOSITORY-KONSOLIDIERUNG'};

const originalRenderSettings=renderSettings;
renderSettings=function(){
  return originalRenderSettings()
    .replace('AUDIO & OFFLINE-STT CORE','TAURI-SIDECAR-INTEGRATION & REPOSITORY-KONSOLIDIERUNG')
    .replace('ein importiertes Modell allein aktiviert noch keine Engine.','in der Desktop-App wird das Modell beim ersten nativen Diktat geprüft und in den geschützten NAQYA-Modellpfad übertragen.');
};

exportBackup=async function(){
  const files=await all('files'),total=files.reduce((n,f)=>n+(f.size||f.blob?.size||0),0);
  if(total>BACKUP_WARN_BYTES&&!confirm(`Dieses Vollbackup enthält ${humanBytes(total)} Binärdaten und benötigt vorübergehend zusätzlichen Arbeitsspeicher. Trotzdem fortfahren?`))return;
  const packed=[];
  for(const f of files){
    const blob=f.blob instanceof Blob?f.blob:new Blob([],{type:f.type||'application/octet-stream'});
    packed.push({id:f.id,name:f.name,type:f.type||blob.type,size:blob.size,createdAt:f.createdAt||null,sha256:await sha256Blob(blob),base64:await blobToBase64(blob)});
  }
  const models=(await all('models')).map(({blob,nativePath,...meta})=>meta);
  const payload={format:'NAQYA-OFFLINE-BACKUP',schema:2,product:'PROVOWARE – NAQYA Memo Tool 2026',version:VERSION,exportedAt:new Date().toISOString(),entries:await all('entries'),projects:await all('projects'),settings:await all('settings'),files:packed,models};
  downloadJson(payload,`NAQYA_VOLLbackup_${todayKey()}.naqya-backup.json`);
};
