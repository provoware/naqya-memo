CREATE TABLE IF NOT EXISTS profile_settings (
    profile_id TEXT NOT NULL,
    setting_key TEXT NOT NULL,
    value_json TEXT NOT NULL,
    revision INTEGER NOT NULL DEFAULT 1,
    updated_at TEXT NOT NULL,
    PRIMARY KEY(profile_id, setting_key),
    FOREIGN KEY(profile_id) REFERENCES profiles(id)
);
CREATE TABLE IF NOT EXISTS profile_access_log (
    access_id TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL,
    attempted_at TEXT NOT NULL,
    result TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'LOCAL',
    FOREIGN KEY(profile_id) REFERENCES profiles(id)
);
CREATE INDEX IF NOT EXISTS idx_profile_access_profile_time ON profile_access_log(profile_id, attempted_at);
CREATE TABLE IF NOT EXISTS startup_runs (
    run_id TEXT PRIMARY KEY,
    profile_id TEXT,
    platform_id TEXT NOT NULL,
    state TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    project_path TEXT,
    report_json TEXT NOT NULL,
    FOREIGN KEY(profile_id) REFERENCES profiles(id)
);
CREATE TABLE IF NOT EXISTS capability_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    startup_run_id TEXT NOT NULL,
    platform_id TEXT NOT NULL,
    capability_json TEXT NOT NULL,
    permission_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(startup_run_id) REFERENCES startup_runs(run_id)
);
CREATE TABLE IF NOT EXISTS project_registry (
    project_id TEXT PRIMARY KEY,
    profile_id TEXT,
    project_path TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    last_verified_at TEXT NOT NULL,
    FOREIGN KEY(profile_id) REFERENCES profiles(id)
);
UPDATE meta SET value='2' WHERE key='database_schema_version';
INSERT OR REPLACE INTO meta(key,value) VALUES('application_data_contract','0.5');
