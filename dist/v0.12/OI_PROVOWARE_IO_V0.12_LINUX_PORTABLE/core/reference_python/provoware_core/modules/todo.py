from dataclasses import dataclass
from .common import require_title,ensure_iso_datetime
import datetime
@dataclass
class TodoService:
    store: object; queue: object
    def create(self,pid,title,description="",due_at=None,reminder_at=None,priority="NORMAL"):
        title=require_title(title,"TODO_TITLE_REQUIRED"); due_at=ensure_iso_datetime(due_at); reminder_at=ensure_iso_datetime(reminder_at)
        if reminder_at and not due_at: raise ValueError("REMINDER_REQUIRES_DUE_DATE")
        payload={"description":description or "","due_at":due_at,"reminder_at":reminder_at,"priority":priority,"completed":False,"completed_at":None,"archived":False}
        return self.queue.wait(self.queue.submit("todo.create",lambda:self.store.upsert_entity(profile_id=pid,entity_type="todo",title=title,payload=payload)))
    def complete(self,eid,pid,rev):
        before=self.store.get_entity(eid)
        if before is None: raise KeyError("TODO_NOT_FOUND")
        payload=dict(before["payload"]); payload["completed"]=True; payload["completed_at"]=datetime.datetime.now(datetime.timezone.utc).isoformat()
        result=self.queue.wait(self.queue.submit("todo.complete",lambda:self.store.upsert_entity(profile_id=pid,entity_type="todo",title=before["title"],payload=payload,entity_id=eid,expected_revision=rev)))
        self.store.record_undo(profile_id=pid,operation_type="todo.complete",target_id=eid,forward={"payload":payload,"title":before["title"]},inverse={"payload":before["payload"],"title":before["title"]})
        return result

    def edit(self,eid,pid,rev,title,description="",due_at=None,reminder_at=None,priority="NORMAL"):
        before=self.store.get_entity(eid)
        if before is None: raise KeyError("TODO_NOT_FOUND")
        title=require_title(title,"TODO_TITLE_REQUIRED"); due_at=ensure_iso_datetime(due_at); reminder_at=ensure_iso_datetime(reminder_at)
        if reminder_at and not due_at: raise ValueError("REMINDER_REQUIRES_DUE_DATE")
        payload=dict(before["payload"])
        payload.update({"description":description or "","due_at":due_at,"reminder_at":reminder_at,"priority":priority})
        result=self.queue.wait(self.queue.submit("todo.edit",lambda:self.store.upsert_entity(profile_id=pid,entity_type="todo",title=title,payload=payload,entity_id=eid,expected_revision=rev)))
        self.store.record_undo(profile_id=pid,operation_type="todo.edit",target_id=eid,forward={"payload":payload,"title":title},inverse={"payload":before["payload"],"title":before["title"]})
        return result
    def trash(self,eid,pid,rev):
        before=self.store.get_entity(eid)
        if before is None: raise KeyError("TODO_NOT_FOUND")
        newrev=self.queue.wait(self.queue.submit("todo.trash",lambda:self.store.soft_delete(eid,rev)))
        self.store.record_undo(profile_id=pid,operation_type="todo.trash",target_id=eid,forward={"status":"TRASHED"},inverse={"status":"ACTIVE"})
        return newrev
