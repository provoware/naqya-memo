from __future__ import annotations
import json, uuid, datetime

def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

class PlaylistService:
    def __init__(self, store, queue): self.store=store; self.queue=queue

    def create(self, profile_id: str, title: str):
        payload={"items":[],"current_index":0,"shuffle":False}
        return self.queue.wait(self.queue.submit("playlist.create",lambda:self.store.upsert_entity(
            profile_id=profile_id,entity_type="playlist",title=title or "Playlist",payload=payload
        )))

    def add_asset(self, playlist_id: str, profile_id: str, revision: int, asset_id: str):
        before=self.store.get_entity(playlist_id)
        if before is None: raise KeyError("PLAYLIST_NOT_FOUND")
        payload=dict(before["payload"]); items=list(payload.get("items",[]))
        if asset_id not in items: items.append(asset_id)
        payload["items"]=items
        result=self.queue.wait(self.queue.submit("playlist.add",lambda:self.store.upsert_entity(
            profile_id=profile_id,entity_type="playlist",title=before["title"],payload=payload,
            entity_id=playlist_id,expected_revision=revision
        )))
        self.store.record_undo(profile_id=profile_id,operation_type="playlist.add",target_id=playlist_id,
            forward={"payload":payload,"title":before["title"]},inverse={"payload":before["payload"],"title":before["title"]})
        return result
