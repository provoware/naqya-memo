from pathlib import Path
import tempfile, sqlite3, os
from provoware_core import CoreStore, ProfileService, SettingsService, ProjectFolderService, GuidedFirstStart, migrate_v1_to_v2
from provoware_core.pin import hash_pin, verify_pin, validate_pin_format
from provoware_core.platform import LinuxAdapter, AndroidAdapter, IOSAdapter

ROOT=Path(__file__).resolve().parents[3]
SCHEMA_V1=ROOT/'schemas'/'core_schema_v1.sql'
SCHEMA_V2=ROOT/'schemas'/'core_schema_v2.sql'
MIGRATION=ROOT/'schemas'/'migrations'/'0001__V1_TO_V2__STATUS-FREIGEGEBEN.sql'

def store_v2(td): return CoreStore(Path(td)/'core.sqlite3',SCHEMA_V2)

def test_pin_hash_is_salted_and_verifiable():
    a=hash_pin('1234'); b=hash_pin('1234')
    assert a != b and verify_pin('1234',a) and not verify_pin('9999',a)

def test_pin_requires_exactly_four_ascii_digits():
    for bad in ('123','12345','12a4','１２３４',''):
        try: validate_pin_format(bad); raise AssertionError(bad)
        except ValueError as e: assert str(e)=='PIN_MUST_BE_FOUR_DIGITS'

def test_profile_create_verify_and_access_log():
    with tempfile.TemporaryDirectory() as td:
        s=store_v2(td); svc=ProfileService(s)
        pid=svc.create('Naqya','2468')
        assert svc.verify_access(pid,'2468') is True
        assert svc.verify_access(pid,'1111') is False
        hist=svc.access_history(pid)
        assert hist[0]['result']=='FAIL' and hist[1]['result']=='SUCCESS'
        s.close()

def test_pin_change_requires_current_pin():
    with tempfile.TemporaryDirectory() as td:
        s=store_v2(td); svc=ProfileService(s); pid=svc.create('P','1234')
        try: svc.change_pin(pid,'9999','5678'); raise AssertionError('expected')
        except PermissionError as e: assert str(e)=='CURRENT_PIN_INVALID'
        svc.change_pin(pid,'1234','5678')
        assert svc.verify_access(pid,'5678')
        s.close()

def test_settings_defaults_and_persistence():
    with tempfile.TemporaryDirectory() as td:
        s=store_v2(td); pid=ProfileService(s).create('P','1234'); settings=SettingsService(s)
        defaults=settings.ensure_defaults(pid)
        assert defaults['theme']=='NEON_TUERKIS' and defaults['help_mode']==2
        settings.set(pid,'theme','HOCHKONTRAST'); settings.set(pid,'font_scale',1.5); settings.set(pid,'help_mode',3)
        assert settings.get(pid,'theme')=='HOCHKONTRAST' and settings.get(pid,'font_scale')==1.5 and settings.get(pid,'help_mode')==3
        s.close()

def test_external_path_confirmation_cannot_be_disabled():
    with tempfile.TemporaryDirectory() as td:
        s=store_v2(td); pid=ProfileService(s).create('P','1234'); settings=SettingsService(s)
        try: settings.set(pid,'confirm_external_paths',False); raise AssertionError('expected')
        except ValueError as e: assert str(e)=='EXTERNAL_PATH_CONFIRMATION_CANNOT_BE_DISABLED_IN_V0_5'
        s.close()

def test_project_preflight_creates_safe_tree():
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/'Projekt'; report=ProjectFolderService(minimum_free_bytes=1).preflight(p)
        assert report.ok and report.created and report.writable
        for rel in ('daten','backups','papierkorb','temp','manifeste','nutzer-einstellungen'):
            assert (p/rel).is_dir()

def test_project_preflight_rejects_file_as_project_folder():
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/'not-folder'; p.write_text('x')
        report=ProjectFolderService(minimum_free_bytes=1).preflight(p)
        assert not report.ok and 'PROJECT_PATH_IS_NOT_DIRECTORY' in report.errors

def test_project_preflight_low_disk_is_red_deterministically():
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/'P'
        report=ProjectFolderService(minimum_free_bytes=10**30).preflight(p)
        assert not report.ok and 'LOW_DISK_SPACE' in report.errors

def test_platform_capability_contracts_are_conservative():
    linux=LinuxAdapter().scan_capabilities(); android=AndroidAdapter().scan_capabilities(); ios=IOSAdapter().scan_capabilities()
    assert linux.platform_id=='linux' and linux.capabilities['filesystem_project_folder'] is True
    assert android.capabilities['filesystem_project_folder']=='SCOPED_STORAGE_ADAPTER_REQUIRED'
    assert ios.capabilities['filesystem_project_folder']=='APP_SANDBOX_DOCUMENT_PICKER'

def test_platform_permissions_require_visible_user_action_on_mobile():
    for adapter in (AndroidAdapter(),IOSAdapter()):
        p=adapter.scan_permissions()
        assert p.permissions['microphone']=='USER_ACTION_REQUIRED'
        assert p.permissions['external_paths']=='USER_ACTION_REQUIRED'

def test_guided_first_start_creates_checkpoint_and_settings():
    with tempfile.TemporaryDirectory() as td:
        base=Path(td); s=CoreStore(base/'core.sqlite3',SCHEMA_V2); pid=ProfileService(s).create('P','1234')
        project=base/'Projekt'
        report=GuidedFirstStart(s,ProjectFolderService(minimum_free_bytes=1)).run(project_path=project,profile_id=pid,platform_id='linux')
        assert report['state'] in ('GREEN','YELLOW') and report['next_action']=='READY'
        assert (project/'manifeste'/'START_CHECKPOINT.json').exists()
        assert SettingsService(s).get(pid,'theme')=='NEON_TUERKIS'
        row=s.conn.execute('SELECT COUNT(*) FROM capability_snapshots').fetchone()[0]
        assert row==1
        s.close()

def test_guided_first_start_without_profile_leads_to_profile_selection():
    with tempfile.TemporaryDirectory() as td:
        base=Path(td); s=CoreStore(base/'core.sqlite3',SCHEMA_V2); project=base/'Projekt'
        report=GuidedFirstStart(s,ProjectFolderService(minimum_free_bytes=1)).run(project_path=project,profile_id=None,platform_id='linux')
        assert report['state']=='YELLOW' and report['next_action']=='PROFILE_SELECT_OR_CREATE'
        s.close()

def test_v1_to_v2_migration_preserves_existing_entity():
    with tempfile.TemporaryDirectory() as td:
        base=Path(td); s=CoreStore(base/'core.sqlite3',SCHEMA_V1)
        pid=s.create_profile('Alt','legacy-hash')
        eid,_=s.upsert_entity(profile_id=pid,entity_type='memo',title='Alt',payload={'body':'bleibt'})
        s.close()
        result=migrate_v1_to_v2(base/'core.sqlite3',MIGRATION)
        assert result['changed'] and result['to']==2
        c=sqlite3.connect(base/'core.sqlite3')
        assert c.execute("SELECT value FROM meta WHERE key='database_schema_version'").fetchone()[0]=='2'
        assert c.execute('SELECT COUNT(*) FROM entities WHERE id=?',(eid,)).fetchone()[0]==1
        assert c.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='profile_settings'").fetchone()[0]==1
        c.close()

if __name__=='__main__':
    tests=[v for k,v in sorted(globals().items()) if k.startswith('test_') and callable(v)]
    failed=[]
    for t in tests:
        try: t(); print('PASS',t.__name__)
        except Exception as e: failed.append((t.__name__,repr(e))); print('FAIL',t.__name__,repr(e))
    print(f'SUMMARY total={len(tests)} passed={len(tests)-len(failed)} failed={len(failed)}')
    if failed: raise SystemExit(1)
