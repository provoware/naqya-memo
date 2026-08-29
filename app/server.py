#!/usr/bin/env python3
from __future__ import annotations
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path
import json, os, sys, threading, webbrowser, subprocess, shutil, traceback, datetime, mimetypes, tempfile

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / 'core' / 'reference_python'
try:
    APP_VERSION = json.loads((ROOT/'registry'/'VERSION.json').read_text(encoding='utf-8')).get('version','UNKNOWN')
except Exception:
    APP_VERSION = 'UNKNOWN'
sys.path.insert(0, str(CORE))

from provoware_core.assets import AssetManager, AssetError
from provoware_core.reminders import ReminderEngine
from provoware_core.media import LinuxAudioRecorder, RecordingError
from provoware_core.platform import linux_capability_probe, write_probe, android_contract, ios_contract
from provoware_core.modules import PlaylistService
from provoware_core import CoreStore, MutationQueue, MemoService, TodoService, CalendarService
from provoware_core.profile import ProfileService
from provoware_core.settings import SettingsService
from provoware_core.startup import GuidedFirstStart
from provoware_core.project_folder import ProjectFolderService

PROJECT = Path(os.environ.get('PROVOWARE_PROJECT_PATH', str(ROOT / 'runtime' / 'projektordner'))).expanduser().resolve()
DATA = PROJECT / 'daten'
UI = ROOT / 'ui' / 'reference_web'
DB = DATA / 'core.sqlite3'
SCHEMA = ROOT / 'schemas' / 'core_schema_v2.sql'
DATA.mkdir(parents=True, exist_ok=True)
for rel in ['assets/audio','assets/dokumente','assets/bilder','export','papierkorb','backups','temp','manifeste','nutzer-einstellungen','notizen']:
    (PROJECT/rel).mkdir(parents=True, exist_ok=True)

store = CoreStore(DB, SCHEMA)
queue = MutationQueue(); queue.start()
profile_service = ProfileService(store)
settings_service = SettingsService(store)
memo_service = MemoService(store, queue)
todo_service = TodoService(store, queue)
calendar_service = CalendarService(store, queue)
asset_manager = AssetManager(PROJECT)
audio_recorder = LinuxAudioRecorder(asset_manager)
playlist_service = PlaylistService(store, queue)
reminder_engine = ReminderEngine(store)

# Ensure a local reference profile. Product login flow remains separate from this development reference shell.
row = store.conn.execute("SELECT id,display_name FROM profiles WHERE status='ACTIVE' ORDER BY created_at LIMIT 1").fetchone()
if row:
    PROFILE_ID, PROFILE_NAME = row[0], row[1]
else:
    PROFILE_ID = profile_service.create('Standardprofil', '0000')
    PROFILE_NAME = 'Standardprofil'
settings_service.ensure_defaults(PROFILE_ID)
try:
    GuidedFirstStart(store).run(project_path=PROJECT, profile_id=PROFILE_ID)
except Exception:
    pass

COLORS = [('Arbeit','neon-tuerkis'),('Privat','lila'),('Wichtig','knallgelb'),('Info','orange'),('Frei','gruen')]
if store.conn.execute('SELECT COUNT(*) FROM calendar_colors WHERE profile_id=?',(PROFILE_ID,)).fetchone()[0] != 5:
    calendar_service.set_color_legend(PROFILE_ID, COLORS)

QUICK_NOTE_LOCK = threading.Lock()

ERROR_TEXT = {
    'MEMO_TITLE_REQUIRED':'Bitte einen Titel für das Memo eingeben.',
    'TODO_TITLE_REQUIRED':'Bitte einen Titel für die Aufgabe eingeben.',
    'EVENT_TITLE_REQUIRED':'Bitte einen Titel für den Termin eingeben.',
    'REMINDER_REQUIRES_DUE_DATE':'Eine Erinnerung benötigt zuerst einen Termin.',
    'EVENT_END_BEFORE_START':'Das Terminende darf nicht vor dem Start liegen.',
    'REVISION_CONFLICT':'Der Inhalt wurde inzwischen geändert. Bitte neu laden.',
    'UNDO_EMPTY':'Es gibt nichts mehr rückgängig zu machen.',
    'REDO_EMPTY':'Es gibt nichts zu wiederholen.',
    'ENTITY_NOT_TRASHED':'Dieser Inhalt liegt nicht im Papierkorb.',
    'DIAG_CONFIRM_REQUIRED':'Diagnosepaket wird erst nach sichtbarer Bestätigung erzeugt.',
    'CALENDAR_REQUIRES_EXACTLY_FIVE_COLORS':'Es müssen genau fünf Kalenderfarben vorhanden sein.',
    'ASSET_TEXT_EDIT_UNSUPPORTED':'Nur TXT- und Markdown-Dateien werden im internen Editor verändert.',
    'ASSET_REVISION_CONFLICT':'Das Dokument wurde inzwischen geändert. Bitte neu laden.',
    'RECORDING_NOT_ACTIVE':'Es läuft aktuell keine Aufnahme.',
    'MICROPHONE_CAPTURE_START_FAILED':'Die Mikrofonaufnahme konnte nicht gestartet werden. Bitte Eingabegerät und Berechtigung prüfen.',
    'UPLOAD_TOO_LARGE':'Die ausgewählte Datei ist für den Browserimport zu groß.',
    'UPLOAD_EMPTY':'Die ausgewählte Datei ist leer oder wurde nicht übertragen.',
    'UPLOAD_TRUNCATED':'Die Dateiübertragung wurde unvollständig beendet.',
    'UPLOAD_FILENAME_REQUIRED':'Der Dateiname fehlt.',

}

def entity_list(entity_type, include_trashed=False):
    q="SELECT id,title,payload_json,revision,status,created_at,updated_at FROM entities WHERE profile_id=? AND entity_type=?"
    params=[PROFILE_ID,entity_type]
    if not include_trashed: q += " AND status='ACTIVE'"
    q += " ORDER BY updated_at DESC"
    rows=store.conn.execute(q,params).fetchall()
    return [dict(id=r[0],title=r[1],payload=json.loads(r[2]),revision=r[3],status=r[4],created_at=r[5],updated_at=r[6]) for r in rows]

def colors():
    rows=store.conn.execute('SELECT id,title,color_token,sort_order FROM calendar_colors WHERE profile_id=? ORDER BY sort_order',(PROFILE_ID,)).fetchall()
    return [dict(id=r[0],title=r[1],token=r[2],order=r[3]) for r in rows]


def day_colors():
    rows=store.conn.execute(
        "SELECT id,title,payload_json,revision FROM entities WHERE profile_id=? AND entity_type='calendar_day_color' AND status='ACTIVE' ORDER BY title",
        (PROFILE_ID,)
    ).fetchall()
    result={}
    for r in rows:
        payload=json.loads(r[2]); result[payload.get('day',r[1])]={'id':r[0],'color_id':payload.get('color_id'),'revision':r[3]}
    return result

def privacy_safe_path(path):
    try:
        p=Path(path)
        return f".../{p.name}"
    except Exception:
        return "[Pfad verborgen]"

def diagnostic_preview():
    return {
        'tool':'OI - PROVOWARE - IO',
        'version':APP_VERSION,
        'timestamp':datetime.datetime.now().astimezone().isoformat(timespec='seconds'),
        'profile':PROFILE_NAME,
        'platform':sys.platform,
        'python':sys.version.split()[0],
        'project_path':privacy_safe_path(PROJECT),
        'database':privacy_safe_path(DB),
        'integrity':store.integrity_check(),
        'asset_quota':asset_manager.quota_status(),
        'audio_capture':audio_recorder.capability(),
        'counts':api_state()['counts'],
        'privacy':{
            'memo_contents':'NICHT ENTHALTEN',
            'pin':'NICHT ENTHALTEN',
            'tokens':'NICHT ENTHALTEN',
            'full_home_path':'VERKÜRZT'
        },
        'solution_hints':[
            'Bei Startfehler STARTEN_LINUX.sh verwenden und nicht index.html direkt öffnen.',
            'Bei Datenfehler zuerst Diagnose und Backup-Integrität prüfen.',
            'Bei Revisionskonflikt Inhalt neu laden statt blind überschreiben.'
        ]
    }

def create_diagnostic_report():
    preview=diagnostic_preview()
    outdir=PROJECT/'export'/'diagnose'
    outdir.mkdir(parents=True,exist_ok=True)
    stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    path=outdir/f'OI_PROVOWARE_IO_DIAGNOSE_{stamp}.txt'
    lines=[
        'OI - PROVOWARE - IO – DIAGNOSEBERICHT',
        '='*64,
        f"Version: {preview['version']}",
        f"Zeit: {preview['timestamp']}",
        f"Profil: {preview['profile']}",
        f"Plattform: {preview['platform']}",
        f"Python: {preview['python']}",
        f"Projekt: {preview['project_path']}",
        f"Datenbank: {preview['database']}",
        f"Integrität: {preview['integrity']}",
        f"Inhalte: {json.dumps(preview['counts'],ensure_ascii=False)}",
        '',
        'DATENSCHUTZFILTER',
        json.dumps(preview['privacy'],ensure_ascii=False,indent=2),
        '',
        'LÖSUNGSHINWEISE',
    ]+[f"- {x}" for x in preview['solution_hints']]
    path.write_text('\\n'.join(lines)+'\\n',encoding='utf-8')
    return path

def safe_note_filename(title):
    cleaned=''.join(c if c.isalnum() or c in ' _-' else '_' for c in (title or 'Notizen')).strip() or 'Notizen'
    return cleaned[:80]+'.txt'

def append_quick_note(title,text):
    if not text.strip(): raise ValueError('NOTE_TEXT_REQUIRED')
    p=PROJECT/'notizen'/safe_note_filename(title)
    stamp=datetime.datetime.now().astimezone().isoformat(timespec='seconds')
    with QUICK_NOTE_LOCK:
        with p.open('a',encoding='utf-8') as f:
            f.write(f'[{stamp}] {text.strip()}\n')
            f.flush(); os.fsync(f.fileno())
    return p

def open_path(path):
    path=str(path)
    cmd = ['xdg-open',path] if shutil.which('xdg-open') else None
    if not cmd: return False, 'Kein Standard-Öffner erkannt.'
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return True, 'Standardprogramm wurde angefordert.'

def notify(title,body):
    if shutil.which('notify-send'):
        subprocess.Popen(['notify-send',title,body], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    return False

def share_note(path):
    # xdg-email can attach a local file on Linux; still requires explicit user action in the mail client.
    if shutil.which('xdg-email'):
        subprocess.Popen(['xdg-email','--subject','OI - PROVOWARE - IO Diagnose/Notiz','--body','Datei aus OI - PROVOWARE - IO. Versand erst nach Ihrer Bestätigung im Mailprogramm.','--attach',str(path),'provoware.157@gmail.com'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True,'Mailprogramm wurde mit vorbereiteter Nachricht geöffnet.'
    return False,'Kein xdg-email erkannt; Datei bleibt lokal.'


def backup_status():
    """Truthful runtime backup status; never claims protection without evidence."""
    roots=[PROJECT/'backups', PROJECT/'daten'/'backups']
    generations=set()
    for root in roots:
        if not root.exists():
            continue
        for p in root.rglob('*'):
            if not p.is_file():
                continue
            name=p.name.lower()
            if ('manifest' in name and p.suffix.lower()=='.json') or name=='core.sqlite3':
                generations.add(str(p.parent.resolve()))
    count=len(generations)
    return {
        'generations':count,
        'state':'READY' if count else 'EMPTY',
        'label':f'{count} Gen.' if count else 'Noch keine'
    }

def api_state():
    return {
        'version':APP_VERSION,'profile':{'id':PROFILE_ID,'name':PROFILE_NAME},
        'settings':settings_service.get_all(PROFILE_ID),
        'counts':{
            'memos':len(entity_list('memo')),
            'todos':len(entity_list('todo')),
            'events':len(entity_list('calendar_event')),
            'trash':store.conn.execute("SELECT COUNT(*) FROM entities WHERE profile_id=? AND status='TRASHED'",(PROFILE_ID,)).fetchone()[0]
        },
        'next':calendar_service.next_items(PROFILE_ID,10),
        'colors':colors(),
        'day_colors':day_colors(),
        'integrity':store.integrity_check(),
        'asset_quota':asset_manager.quota_status(),
        'audio_capture':audio_recorder.capability(),
        'backup':backup_status(),
    }

class Handler(SimpleHTTPRequestHandler):
    server_version='Provoware/0.12'
    def translate_path(self,path):
        clean=urlparse(path).path.lstrip('/')
        return str(UI / clean)
    def log_message(self,fmt,*args):
        pass
    def _json(self,obj,status=200):
        data=json.dumps(obj,ensure_ascii=False).encode('utf-8')
        self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data)
    def _body(self):
        n=int(self.headers.get('Content-Length','0')); raw=self.rfile.read(n) if n else b'{}'
        return json.loads(raw.decode('utf-8') or '{}')
    def _asset_upload(self):
        parsed=urlparse(self.path); q=parse_qs(parsed.query)
        kind=str((q.get('kind') or [''])[0])
        title=str((q.get('title') or [''])[0])
        filename=Path(str((q.get('filename') or [''])[0])).name
        if not filename: raise ValueError('UPLOAD_FILENAME_REQUIRED')
        length=int(self.headers.get('Content-Length','0') or '0')
        max_bytes=int(os.environ.get('PROVOWARE_UPLOAD_MAX_BYTES',str(512*1024*1024)))
        if length<=0: raise ValueError('UPLOAD_EMPTY')
        if length>max_bytes: raise ValueError('UPLOAD_TOO_LARGE')
        upload_root=PROJECT/'temp'/'browser-uploads'
        upload_root.mkdir(parents=True,exist_ok=True)
        session=Path(tempfile.mkdtemp(prefix='upload_',dir=str(upload_root)))
        tmp=session/filename
        try:
            remaining=length
            with open(tmp,'wb') as f:
                while remaining:
                    chunk=self.rfile.read(min(1024*1024,remaining))
                    if not chunk: break
                    f.write(chunk); remaining-=len(chunk)
                f.flush(); os.fsync(f.fileno())
            if remaining: raise ValueError('UPLOAD_TRUNCATED')
            manifest=asset_manager.import_asset(tmp,kind,title or Path(filename).stem)
            return self._ok(manifest,'Datei sicher importiert.')
        finally:
            shutil.rmtree(session,ignore_errors=True)
    def _ok(self,data=None,message='OK'): self._json({'ok':True,'message':message,'data':data})
    def _fail(self,e,status=400):
        code=str(e.args[0] if getattr(e,'args',None) else e)
        self._json({'ok':False,'code':code,'message':ERROR_TEXT.get(code,code)},status)
    def do_GET(self):
        path=urlparse(self.path).path
        try:
            if path.startswith('/asset-file/'):
                aid=path.split('/')[2]
                manifest=asset_manager.validate_asset(aid)
                fpath=asset_manager.path_for(aid)
                ctype=mimetypes.guess_type(fpath.name)[0] or 'application/octet-stream'
                data=fpath.read_bytes()
                self.send_response(200); self.send_header('Content-Type',ctype); self.send_header('Content-Length',str(len(data))); self.send_header('Content-Disposition',f"inline; filename*=UTF-8''{manifest['original_name']}"); self.send_header('X-Content-Type-Options','nosniff'); self.end_headers(); self.wfile.write(data); return
            if path=='/api/state': return self._ok(api_state())
            if path=='/api/memos': return self._ok(entity_list('memo'))
            if path=='/api/todos': return self._ok(entity_list('todo'))
            if path=='/api/events': return self._ok(entity_list('calendar_event'))
            if path=='/api/calendar/day-colors': return self._ok(day_colors())
            if path=='/api/diagnostics/preview': return self._ok(diagnostic_preview())
            if path=='/api/assets/quota': return self._ok(asset_manager.quota_status())
            if path=='/api/playlists': return self._ok(entity_list('playlist'))
            if path=='/api/reminders/pending': return self._ok(reminder_engine.pending_for_platform(PROFILE_ID,'linux'))
            if path=='/api/assets/list': return self._ok(asset_manager.list_assets())
            if path.startswith('/api/assets/') and path.endswith('/text'):
                aid=path.split('/')[3]; return self._ok(asset_manager.read_text_asset(aid))
            if path=='/api/audio/capability': return self._ok(audio_recorder.capability())
            if path=='/api/platform/capabilities':
                linux=linux_capability_probe(); linux['filesystem_write_test']=write_probe(PROJECT)
                return self._ok({'linux':linux,'android':android_contract(),'ios':ios_contract()})
            if path=='/api/trash':
                rows=store.conn.execute("SELECT id,entity_type,title,payload_json,revision,status,updated_at FROM entities WHERE profile_id=? AND status='TRASHED' ORDER BY updated_at DESC",(PROFILE_ID,)).fetchall()
                return self._ok([dict(id=r[0],entity_type=r[1],title=r[2],payload=json.loads(r[3]),revision=r[4],status=r[5],updated_at=r[6]) for r in rows])
            if path=='/api/health': return self._ok({'version':APP_VERSION,'integrity':store.integrity_check(),
        'asset_quota':asset_manager.quota_status(),
        'audio_capture':audio_recorder.capability(),'queue':'running','project':str(PROJECT),'db':str(DB)})
            return super().do_GET()
        except Exception as e: return self._fail(e,500)
    def do_POST(self):
        path=urlparse(self.path).path
        try:
            if path=='/api/assets/upload':
                return self._asset_upload()
            b=self._body()
            if path=='/api/memos':
                eid,rev=memo_service.create(PROFILE_ID,b.get('title',''),b.get('body',''),b.get('tags') or [])
                return self._ok(store.get_entity(eid),'Memo gespeichert.')
            if path.startswith('/api/memos/') and path.endswith('/edit'):
                eid=path.split('/')[3]; memo_service.edit(eid,PROFILE_ID,int(b.get('revision')),b.get('title',''),b.get('body',''),b.get('tags') or []); return self._ok(store.get_entity(eid),'Memo aktualisiert.')
            if path.startswith('/api/memos/') and path.endswith('/trash'):
                eid=path.split('/')[3]; rev=int(b.get('revision')); memo_service.trash(eid,PROFILE_ID,rev); return self._ok(None,'Memo liegt im Papierkorb.')
            if path=='/api/todos':
                eid,rev=todo_service.create(PROFILE_ID,b.get('title',''),b.get('description',''),b.get('due_at') or None,b.get('reminder_at') or None,b.get('priority','NORMAL'))
                if b.get('reminder_at'): notify('OI - PROVOWARE - IO',f"Erinnerung vorbereitet: {b.get('title','Todo')}")
                return self._ok(store.get_entity(eid),'Todo gespeichert.')
            if path.startswith('/api/todos/') and path.endswith('/edit'):
                eid=path.split('/')[3]; todo_service.edit(eid,PROFILE_ID,int(b.get('revision')),b.get('title',''),b.get('description',''),b.get('due_at') or None,b.get('reminder_at') or None,b.get('priority','NORMAL')); return self._ok(store.get_entity(eid),'Todo aktualisiert.')
            if path.startswith('/api/todos/') and path.endswith('/complete'):
                eid=path.split('/')[3]; todo_service.complete(eid,PROFILE_ID,int(b.get('revision'))); return self._ok(store.get_entity(eid),'Todo erledigt.')
            if path.startswith('/api/todos/') and path.endswith('/trash'):
                eid=path.split('/')[3]; todo_service.trash(eid,PROFILE_ID,int(b.get('revision'))); return self._ok(None,'Todo liegt im Papierkorb.')
            if path=='/api/events':
                eid,rev=calendar_service.create_event(PROFILE_ID,b.get('title',''),b.get('start_at',''),b.get('end_at') or None,bool(b.get('all_day')),b.get('color_id') or None,b.get('reminder_at') or None)
                if b.get('reminder_at'): notify('OI - PROVOWARE - IO',f"Termin-Erinnerung vorbereitet: {b.get('title','Termin')}")
                return self._ok(store.get_entity(eid),'Termin gespeichert.')
            if path.startswith('/api/events/') and path.endswith('/edit'):
                eid=path.split('/')[3]; calendar_service.edit_event(eid,PROFILE_ID,int(b.get('revision')),b.get('title',''),b.get('start_at',''),b.get('end_at') or None,bool(b.get('all_day')),b.get('color_id') or None,b.get('reminder_at') or None); return self._ok(store.get_entity(eid),'Termin aktualisiert.')
            if path.startswith('/api/events/') and path.endswith('/trash'):
                eid=path.split('/')[3]; calendar_service.trash_event(eid,PROFILE_ID,int(b.get('revision'))); return self._ok(None,'Termin liegt im Papierkorb.')
            if path=='/api/calendar/day-color':
                day=str(b.get('day','')); cid=str(b.get('color_id',''))
                if not day or not cid: raise ValueError('CALENDAR_DAY_COLOR_REQUIRED')
                existing=day_colors().get(day)
                if existing:
                    payload={'day':day,'color_id':cid}
                    queue.wait(queue.submit('calendar.update_day_color',lambda:store.upsert_entity(profile_id=PROFILE_ID,entity_type='calendar_day_color',title=day,payload=payload,entity_id=existing['id'],expected_revision=existing['revision'])))
                else:
                    calendar_service.set_day_color(PROFILE_ID,day,cid)
                return self._ok(day_colors().get(day),'Tagfarbe gespeichert.')
            if path=='/api/calendar/colors':
                entries=b.get('entries') or []
                if len(entries)!=5: raise ValueError('CALENDAR_REQUIRES_EXACTLY_FIVE_COLORS')
                pairs=[(str(x.get('title','')),str(x.get('token',''))) for x in entries]
                queue.wait(queue.submit('calendar.colors',lambda:calendar_service.set_color_legend(PROFILE_ID,pairs)))
                return self._ok(colors(),'Kalenderlegende gespeichert.')
            if path.startswith('/api/trash/') and path.endswith('/restore'):
                eid=path.split('/')[3]; rev=int(b.get('revision'))
                queue.wait(queue.submit('trash.restore',lambda:store.restore_entity(eid,rev)))
                return self._ok(store.get_entity(eid),'Inhalt wiederhergestellt.')
            if path=='/api/diagnostics/create':
                if b.get('confirmed') is not True: raise ValueError('DIAG_CONFIRM_REQUIRED')
                p=create_diagnostic_report()
                return self._ok({'path':str(p),'name':p.name},'Diagnosebericht lokal erstellt.')
            if path=='/api/reminders/mark-delivered':
                eid=str(b.get('entity_id','')); reminder_at=str(b.get('reminder_at','')); platform=str(b.get('platform','linux'))
                reminder_engine.mark_delivered(PROFILE_ID,eid,reminder_at,platform,str(b.get('result','DELIVERED')))
                return self._ok(None,'Reminder als zugestellt protokolliert.')
            if path=='/api/assets/import':
                src=Path(str(b.get('source_path','')))
                kind=str(b.get('kind',''))
                title=str(b.get('title',''))
                m=asset_manager.import_asset(src,kind,title)
                return self._ok(m,'Asset sicher importiert.')
            if path=='/api/assets/validate':
                aid=str(b.get('asset_id',''))
                return self._ok(asset_manager.validate_or_quarantine(aid),'Asset geprüft.')
            if path=='/api/assets/edit-text':
                aid=str(b.get('asset_id','')); text=str(b.get('text','')); rev=int(b.get('revision'))
                return self._ok(asset_manager.edit_text_asset(aid,text,rev),'Dokument revisionsgesichert gespeichert.')
            if path=='/api/audio/start':
                return self._ok(audio_recorder.start(str(b.get('backend','pulse')),str(b.get('device','default'))),'Aufnahme gestartet.')
            if path=='/api/audio/stop':
                return self._ok(audio_recorder.stop_and_commit(str(b.get('title','Sprachmemo'))),'Aufnahme sicher gespeichert.')
            if path=='/api/playlists':
                eid,rev=playlist_service.create(PROFILE_ID,str(b.get('title','Playlist')))
                return self._ok(store.get_entity(eid),'Playlist erstellt.')
            if path.startswith('/api/playlists/') and path.endswith('/add'):
                eid=path.split('/')[3]
                playlist_service.add_asset(eid,PROFILE_ID,int(b.get('revision')),str(b.get('asset_id')))
                return self._ok(store.get_entity(eid),'Asset zur Playlist hinzugefügt.')
            if path=='/api/quick-note':
                p=append_quick_note(b.get('title','Notizen'),b.get('text','')); return self._ok({'path':str(p),'name':p.name},'Textdatei ergänzt.')
            if path=='/api/quick-note/open':
                p=PROJECT/'notizen'/safe_note_filename(b.get('title','Notizen')); ok,msg=open_path(p); return self._ok({'opened':ok,'path':str(p)},msg)
            if path=='/api/quick-note/share':
                p=PROJECT/'notizen'/safe_note_filename(b.get('title','Notizen'))
                if not p.exists(): raise FileNotFoundError('NOTE_FILE_NOT_FOUND')
                ok,msg=share_note(p); return self._ok({'opened':ok,'path':str(p)},msg)
            if path=='/api/undo': queue.wait(queue.submit('ui.undo', lambda: store.undo_last(PROFILE_ID))); return self._ok(api_state(),'Letzte Änderung rückgängig.')
            if path=='/api/redo': queue.wait(queue.submit('ui.redo', lambda: store.redo_last(PROFILE_ID))); return self._ok(api_state(),'Änderung wiederholt.')
            if path=='/api/settings':
                for k,v in b.items(): queue.wait(queue.submit('settings.set', lambda k=k,v=v: settings_service.set(PROFILE_ID,k,v)))
                return self._ok(settings_service.get_all(PROFILE_ID),'Einstellungen gespeichert.')
            return self._json({'ok':False,'message':'Nicht gefunden'},404)
        except Exception as e:
            return self._fail(e,409 if str(e)=='REVISION_CONFLICT' else 400)

def run(port=8765,open_browser=True):
    os.chdir(UI)
    try:
        server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
    except OSError as e:
        queue.stop(); store.close()
        if getattr(e,'errno',None)==98:
            print(f'PORT_BELEGT: 127.0.0.1:{port}. Bitte STARTEN_LINUX.sh verwenden; der Launcher wählt sicher einen freien Port und beendet keine fremden Prozesse.',file=sys.stderr,flush=True)
        raise
    url=f'http://127.0.0.1:{port}/index.html'
    print(f'OI - PROVOWARE - IO {APP_VERSION} läuft: {url}',flush=True)
    if open_browser: threading.Timer(.4,lambda:webbrowser.open(url)).start()
    try: server.serve_forever()
    finally:
        queue.stop(); store.close(); server.server_close()

if __name__=='__main__':
    port=int(os.environ.get('PROVOWARE_PORT','8765'))
    run(port, '--no-browser' not in sys.argv)
