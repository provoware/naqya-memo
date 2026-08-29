# 🗃️ DATENMODELL — STATUS: FREIGEGEBEN — V0.1

## Gemeinsame Metafelder
`id, schema_version, created_at, updated_at, revision, profile_id, status, tags, checksum`

## Aggregate
### Memo
title, body, pinned, archived, due_at?, attachments[], links[]

### VoiceMemo
title, audio_asset_id, duration, transcript?, markers[]

### Todo
title, description, due_at?, reminder_policy?, completed_at?, archived_at?, priority, calendar_ref?

### CalendarEvent
title, start_at, end_at?, all_day, reminder_policy[], color_id, recurrence?, links[]

### CalendarColor
id, title, color_token, order, enabled

### Document
title, type, asset_id, editable, revisions[]

### Playlist
title, items[], current_index, shuffle

### Quote
text, enabled, last_shown_at

### Profile
display_name, pin_hash_or_platform_safe_representation, created_at, preferences_ref
> PIN schützt Zugang, nicht Datenverschlüsselung.

### OperationRecord
operation_id, type, target_ids, pre_result, post_result, rollback_result, evidence_refs[]

## Zeit
UTC-basierte Persistenz + explizite IANA-Zeitzone für Termine; lokale Darstellung getrennt.
