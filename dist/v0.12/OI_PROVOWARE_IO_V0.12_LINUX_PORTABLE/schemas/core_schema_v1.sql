PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS profiles (
    id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    pin_hash TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    revision INTEGER NOT NULL DEFAULT 1,
    status TEXT NOT NULL DEFAULT 'ACTIVE'
);

CREATE TABLE IF NOT EXISTS entities (
    id TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    schema_version INTEGER NOT NULL,
    revision INTEGER NOT NULL,
    status TEXT NOT NULL,
    title TEXT NOT NULL DEFAULT '',
    payload_json TEXT NOT NULL,
    checksum_sha256 TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    deleted_at TEXT,
    FOREIGN KEY(profile_id) REFERENCES profiles(id)
);

CREATE INDEX IF NOT EXISTS idx_entities_profile_type
ON entities(profile_id, entity_type, status);

CREATE INDEX IF NOT EXISTS idx_entities_updated
ON entities(updated_at);

CREATE TABLE IF NOT EXISTS operation_journal (
    operation_id TEXT PRIMARY KEY,
    profile_id TEXT,
    operation_type TEXT NOT NULL,
    target_ids_json TEXT NOT NULL,
    state TEXT NOT NULL,
    started_at TEXT NOT NULL,
    committed_at TEXT,
    pre_result_json TEXT NOT NULL,
    post_result_json TEXT,
    rollback_result_json TEXT,
    error_code TEXT,
    evidence_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_operation_journal_started
ON operation_journal(started_at);

CREATE TABLE IF NOT EXISTS backup_generations (
    generation_id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    source_revision INTEGER NOT NULL,
    manifest_path TEXT NOT NULL,
    checksum_sha256 TEXT NOT NULL,
    verified_restore INTEGER NOT NULL DEFAULT 0,
    restore_verified_at TEXT
);

CREATE TABLE IF NOT EXISTS schema_migrations (
    migration_id TEXT PRIMARY KEY,
    from_version INTEGER NOT NULL,
    to_version INTEGER NOT NULL,
    applied_at TEXT NOT NULL,
    checksum_sha256 TEXT NOT NULL,
    result TEXT NOT NULL
);

INSERT OR IGNORE INTO meta(key, value) VALUES ('database_schema_version', '1');
INSERT OR IGNORE INTO meta(key, value) VALUES ('application_data_contract', '0.2');

CREATE TABLE IF NOT EXISTS undo_journal (entry_id TEXT PRIMARY KEY, profile_id TEXT NOT NULL, operation_type TEXT NOT NULL, target_id TEXT NOT NULL, forward_json TEXT NOT NULL, inverse_json TEXT NOT NULL, state TEXT NOT NULL, created_at TEXT NOT NULL, applied_at TEXT, FOREIGN KEY(profile_id) REFERENCES profiles(id));
CREATE INDEX IF NOT EXISTS idx_undo_journal_profile_state ON undo_journal(profile_id,state,created_at);
CREATE TABLE IF NOT EXISTS calendar_colors (id TEXT PRIMARY KEY, profile_id TEXT NOT NULL, title TEXT NOT NULL, color_token TEXT NOT NULL, sort_order INTEGER NOT NULL, enabled INTEGER NOT NULL DEFAULT 1, revision INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY(profile_id) REFERENCES profiles(id));
