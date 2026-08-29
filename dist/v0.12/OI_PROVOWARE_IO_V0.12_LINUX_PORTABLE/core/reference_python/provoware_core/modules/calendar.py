from dataclasses import dataclass
from .common import require_title,ensure_iso_datetime,utc_now
import uuid,json
@dataclass
class CalendarService:
    store: object; queue: object
    def create_event(self,pid,title,start_at,end_at=None,all_day=False,color_id=None,reminder_at=None):
        title=require_title(title,"EVENT_TITLE_REQUIRED"); start_at=ensure_iso_datetime(start_at,False); end_at=ensure_iso_datetime(end_at); reminder_at=ensure_iso_datetime(reminder_at)
        if end_at and end_at<start_at: raise ValueError("EVENT_END_BEFORE_START")
        payload={"start_at":start_at,"end_at":end_at,"all_day":bool(all_day),"color_id":color_id,"reminder_at":reminder_at,"archived":False}
        return self.queue.wait(self.queue.submit("calendar.create_event",lambda:self.store.upsert_entity(profile_id=pid,entity_type="calendar_event",title=title,payload=payload)))
    def set_day_color(self,pid,day_iso,color_id):
        return self.queue.wait(self.queue.submit("calendar.set_day_color",lambda:self.store.upsert_entity(profile_id=pid,entity_type="calendar_day_color",title=day_iso,payload={"day":day_iso,"color_id":color_id})))
    def set_color_legend(self,pid,entries):
        if len(entries)!=5: raise ValueError("CALENDAR_REQUIRES_EXACTLY_FIVE_COLORS")
        now=utc_now(); ids=[]
        with self.store.conn:
            self.store.conn.execute("DELETE FROM calendar_colors WHERE profile_id=?",(pid,))
            for i,(title,token) in enumerate(entries):
                cid=str(uuid.uuid4()); title=require_title(title,"COLOR_TITLE_REQUIRED")
                self.store.conn.execute("INSERT INTO calendar_colors(id,profile_id,title,color_token,sort_order,enabled,revision,created_at,updated_at) VALUES(?,?,?,?,?,1,1,?,?)",(cid,pid,title,token,i,now,now)); ids.append(cid)
        return ids
    def next_items(self,pid,limit=10):
        rows=self.store.conn.execute("SELECT id,entity_type,title,payload_json,revision FROM entities WHERE profile_id=? AND status='ACTIVE' AND entity_type IN ('todo','calendar_event') ORDER BY updated_at ASC LIMIT ?",(pid,limit)).fetchall()
        return [{"id":r[0],"entity_type":r[1],"title":r[2],"payload":json.loads(r[3]),"revision":r[4]} for r in rows]

    def edit_event(self,eid,pid,rev,title,start_at,end_at=None,all_day=False,color_id=None,reminder_at=None):
        before=self.store.get_entity(eid)
        if before is None: raise KeyError("EVENT_NOT_FOUND")
        title=require_title(title,"EVENT_TITLE_REQUIRED"); start_at=ensure_iso_datetime(start_at,False); end_at=ensure_iso_datetime(end_at); reminder_at=ensure_iso_datetime(reminder_at)
        if end_at and end_at<start_at: raise ValueError("EVENT_END_BEFORE_START")
        payload=dict(before["payload"])
        payload.update({"start_at":start_at,"end_at":end_at,"all_day":bool(all_day),"color_id":color_id,"reminder_at":reminder_at})
        result=self.queue.wait(self.queue.submit("calendar.edit_event",lambda:self.store.upsert_entity(profile_id=pid,entity_type="calendar_event",title=title,payload=payload,entity_id=eid,expected_revision=rev)))
        self.store.record_undo(profile_id=pid,operation_type="calendar.edit",target_id=eid,forward={"payload":payload,"title":title},inverse={"payload":before["payload"],"title":before["title"]})
        return result
    def trash_event(self,eid,pid,rev):
        before=self.store.get_entity(eid)
        if before is None: raise KeyError("EVENT_NOT_FOUND")
        newrev=self.queue.wait(self.queue.submit("calendar.trash_event",lambda:self.store.soft_delete(eid,rev)))
        self.store.record_undo(profile_id=pid,operation_type="calendar.trash",target_id=eid,forward={"status":"TRASHED"},inverse={"status":"ACTIVE"})
        return newrev

    def events_between(self, profile_id: str, start_iso: str, end_iso: str):
        rows=self.store.conn.execute(
            """SELECT id,title,payload_json,revision FROM entities
               WHERE profile_id=? AND status='ACTIVE' AND entity_type='calendar_event'""",(profile_id,)
        ).fetchall()
        out=[]
        for r in rows:
            payload=__import__("json").loads(r[2])
            start=payload.get("start_at")
            if start and start_iso <= start < end_iso:
                out.append({"id":r[0],"title":r[1],"payload":payload,"revision":r[3]})
        out.sort(key=lambda x:x["payload"].get("start_at",""))
        return out
