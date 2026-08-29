from dataclasses import dataclass
from .common import require_title
@dataclass
class MemoService:
    store: object; queue: object
    def create(self,pid,title,body,tags=None):
        title=require_title(title,"MEMO_TITLE_REQUIRED"); payload={"body":body or "","tags":tags or [],"pinned":False,"archived":False}
        return self.queue.wait(self.queue.submit("memo.create",lambda:self.store.upsert_entity(profile_id=pid,entity_type="memo",title=title,payload=payload)))
    def edit(self,eid,pid,rev,title,body,tags=None):
        before=self.store.get_entity(eid)
        if before is None: raise KeyError("MEMO_NOT_FOUND")
        title=require_title(title,"MEMO_TITLE_REQUIRED"); payload=dict(before["payload"]); payload.update({"body":body or "","tags":tags or []})
        result=self.queue.wait(self.queue.submit("memo.edit",lambda:self.store.upsert_entity(profile_id=pid,entity_type="memo",title=title,payload=payload,entity_id=eid,expected_revision=rev)))
        self.store.record_undo(profile_id=pid,operation_type="memo.edit",target_id=eid,forward={"title":title,"payload":payload},inverse={"title":before["title"],"payload":before["payload"]})
        return result
    def trash(self,eid,pid,rev):
        before=self.store.get_entity(eid)
        if before is None: raise KeyError("MEMO_NOT_FOUND")
        newrev=self.queue.wait(self.queue.submit("memo.trash",lambda:self.store.soft_delete(eid,rev)))
        self.store.record_undo(profile_id=pid,operation_type="memo.trash",target_id=eid,forward={"status":"TRASHED"},inverse={"status":"ACTIVE"})
        return newrev

    def restore(self,eid,pid,rev):
        return self.queue.wait(self.queue.submit("memo.restore",lambda:self.store.restore_entity(eid,rev)))
