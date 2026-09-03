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

# Select the profile chosen by the desktop start helper. Headless/development starts keep
# the historical first-active-profile fallback. An invalid requested ID fails closed.
REQUESTED_PROFILE_ID = os.environ.get('PROVOWARE_PROFILE_ID','').strip()
if REQUESTED_PROFILE_ID:
    row = store.conn.execute("SELECT id,display_name FROM profiles WHERE id=? AND status='ACTIVE'", (REQUESTED_PROFILE_ID,)).fetchone()
    if row is None:
        raise RuntimeError('START_PROFILE_NOT_FOUND')
else:
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
    'MEMO_TITLE_REQUIRED':'Bitte einen Titel f√ºr das Memo eingeben.',
    'TODO_TITLE_REQUIRED':'Bitte einen Titel f√ºr die Aufgabe eingeben.',
    'EVENT_TITLE_REQUIRED':'Bitte einen Titel f√ºr den Termin eingeben.',
    'REMINDER_REQUIRES_DUE_DATE':'Eine Erinnerung ben√∂tigt zuerst einen Termin.',
    'EVENT_END_BEFORE_START':'Das Terminende darf nicht vor dem Start liegen.',
    'REVISION_CONFLICT':'Der Inhalt wurde inzwischen ge√§ndert. Bitte neu laden.',
    'UNDO_EMPTY':'Es gibt nichts mehr r√ºckg√§ngig zu machen.',
    'REDO_EMPTY':'Es gibt nichts zu wiederholen.',
    'ENTITY_NOT_TRASHED':'Dieser Inhalt liegt nicht im Papierkorb.',
    'DIAG_CONFIRM_REQUIRED':'Diagnosepaket wird erst nach sichtbarer Best√§tigung erzeugt.',
    'CALENDAR_REQUIRES_EXACTLY_FIVE_COLORS':'Es m√ºssen genau f√ºnf Kalenderfarben vorhanden sein.',
    'ASSET_TEXT_EDIT_UNSUPPORTED':'Nur TXT- und Markdown-Dateien werden im internen Editor ver√§ndert.',
    'ASSET_REVISION_CONFLICT':'Das Dokument wurde inzwischen ge√§ndert. Bitte neu laden.',
    'RECORDING_NOT_ACTIVE':'Es l√§uft aktuell keine Aufnahme.',
    'MICROPHONE_CAPTURE_START_FAILED':'Die Mikrofonaufnahme konnte nicht gestartet werden. Bitte Eingabeger√§t und Berechtigung pr√ºfen.',
    'UPLOAD_TOO_LARGE':'Die ausgew√§hlte Datei ist f√ºr den Browserimport zu gro√ü.',
    'UPLOAD_EMPTY':'Die ausgew√§hlte Datei ist leer oder wurde nicht √ºbertragen.',
    'UPLOAD_TRUNCATED':'Die Datei√ºbertragung wurde unvollst√§ndig beendet.',
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
            'full_home_path':'VERK√úRZT'
        },
        'solution_hints':[
            'Bei Startfehler STARTEN_LINUX.sh verwenden und nicht index.html direkt √∂ffnen.',
            'Bei Datenfehler zuerst Diagnose und Backup-Integrit√§t pr√ºfen.',
            'Bei Revisionskonflikt Inhalt neu laden statt blind √ºberschreiben.'
        ]
    }

def create_diagnostic_report():
    preview=diagnostic_preview()
    outdir=PROJECT/'export'/'d≤»="25…îπùï—}ïπ—•—‰°ï•ê§∞ùQΩëºÅï…±ïë•ù–∏ú§(ÄÄÄÄÄÄÄÄÄÄÄÅ•òÅ¡Ö—†πÕ—Ö…—Õ›•—††úΩÖ¡§Ω—ΩëΩÃºú§ÅÖπêÅ¡Ö—†πïπëÕ›•—††úΩ—…ÖÕ†ú§Ë(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅï•êı¡Ö—†πÕ¡±•–†úºú•lÕtÏÅ—ΩëΩ}Õï…Ÿ•çîπ—…ÖÕ†°ï•ê±AI=%1}%±•π–°àπùï–†ù…ïŸ•Õ•Ω∏ú§§§ÏÅ…ï—’…∏ÅÕï±òπ}Ω¨°9Ωπî∞ùQΩëºÅ±•ïù–Å•¥ÅAÖ¡•ï…≠Ω…à∏ú§(ÄÄÄÄÄÄÄÄÄÄÄÅ•òÅ¡Ö—†ÙÙúΩÖ¡§ΩïŸïπ—ÃúË(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅï•ê±…ïÿıçÖ±ïπëÖ…}Õï…Ÿ•çîπç…ïÖ—ï}ïŸïπ–°AI=%1}%±àπùï–†ù—•—±îú∞úú§±àπùï–†ùÕ—Ö…—}Ö–ú∞úú§±àπùï–†ùïπë}Ö–ú§ÅΩ»Å9Ωπî±âΩΩ∞°àπùï–†ùÖ±±}ëÖ‰ú§§±àπùï–†ùçΩ±Ω…}•êú§ÅΩ»Å9Ωπî±àπùï–†ù…ïµ•πëï…}Ö–ú§ÅΩ»Å9Ωπî§(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ•òÅàπùï–†ù…ïµ•πëï…}Ö–ú§ËÅπΩ—•ô‰†ù=$Ä¥ÅAI=Y=]IÄ¥Å%<ú±òâQï…µ•∏µ…•ππï…’πúÅŸΩ…âï…ï•—ï–ËÅÌàπùï–†ù—•—±îú∞ùQï…µ•∏ú•Ùà§(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ…ï—’…∏ÅÕï±òπ}Ω¨°Õ—Ω…îπùï—}ïπ—•—‰°ï•ê§∞ùQï…µ•∏ÅùïÕ¡ï•ç°ï…–∏ú§(ÄÄÄÄÄÄÄÄÄÄÄÅ•òÅ¡Ö—†πÕ—Ö…—Õ›•—††úΩÖ¡§ΩïŸïπ—Ãºú§ÅÖπêÅ¡Ö—†πïπëÕ›•—††úΩïë•–ú§Ë(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅï•êı¡Ö—†πÕ¡±•–†úºú•lÕtÏÅçÖ±ïπëÖ…}Õï…Ÿ•çîπïë•—}ïŸïπ–°ï•ê±AI=%1}%±•π–°àπùï–†ù…ïŸ•Õ•Ω∏ú§§±àπùï–†ù—•—±îú∞úú§±àπùï–†ùÕ—Ö…—}Ö–ú∞úú§±àπùï–†ùïπë}Ö–ú§ÅΩ»Å9Ωπî±âΩΩ∞°àπùï–†ùÖ±±}ëÖ‰ú§§±àπùï–†ùçΩ±Ω…}•êú§ÅΩ»Å9Ωπî±àπùï–†ù…ïµ•πëï…}Ö–ú§ÅΩ»Å9Ωπî§ÏÅ…ï—’…∏ÅÕï±òπ}Ω¨°Õ—Ω…îπùï—}ïπ—•—‰°ï•ê§∞ùQï…µ•∏ÅÖ≠—’Ö±•Õ•ï…–∏ú§(ÄÄÄÄÄÄÄÄÄÄÄÅ•òÅ¡Ö—†πÕ—Ö…—Õ›•—††úΩÖ¡§ΩïŸïπ—Ãºú§ÅÖπêÅ¡Ö—†πïπëÕ›•—††úΩ—…ÖÕ†ú§Ë(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅï•êı¡Ö—†πÕ¡±•–†úºú•lÕtÏÅçÖ±ïπëÖ…}Õï…Ÿ•çîπ—…ÖÕ°}ïŸïπ–°ï•ê±AI=%1}%±•π–°àπùï–†ù…ïŸ•Õ•Ω∏ú§§§ÏÅ…ï—’…∏ÅÕï±òπ}Ω¨°9Ωπî∞ùQï…µ•∏Å±•ïù–Å•¥ÅAÖ¡•ï…≠Ω…à∏ú§(ÄÄÄÄÄÄÄÄÄÄÄÅ•òÅ¡Ö—†ÙÙúΩÖ¡§ΩçÖ±ïπëÖ»ΩëÖ‰µçΩ±Ω»úË(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅëÖ‰ıÕ—»°àπùï–†ùëÖ‰ú∞úú§§ÏÅç•êıÕ—»°àπùï–†ùçΩ±Ω…}•êú∞úú§§(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ•òÅπΩ–ÅëÖ‰ÅΩ»ÅπΩ–Åç•êËÅ…Ö•ÕîÅYÖ±’ï……Ω»†ù19I}e}=1=I}IEU%Iú§(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅï·•Õ—•πúıëÖÂ}çΩ±Ω…Ã†§πùï–°ëÖ‰§(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ•òÅï·•Õ—•πúË(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ¡ÖÂ±ΩÖêıÏùëÖ‰úÈëÖ‰∞ùçΩ±Ω…}•êúÈç•ëÙ(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ≈’ï’îπ›Ö•–°≈’ï’îπÕ’âµ•–†ùçÖ±ïπëÖ»π’¡ëÖ—ï}ëÖÂ}çΩ±Ω»ú±±ÖµâëÑÈÕ—Ω…îπ’¡Õï…—}ïπ—•—‰°¡…Ωô•±ï}•êıAI=%1}%±ïπ—•—Â}—Â¡îÙùçÖ±ïπëÖ…}ëÖÂ}çΩ±Ω»ú±—•—±îıëÖ‰±¡ÖÂ±ΩÖêı¡ÖÂ±ΩÖê±ïπ—•—Â}•êıï·•Õ—•πùlù•êùt±ï·¡ïç—ïë}…ïŸ•Õ•Ω∏ıï·•Õ—•πùlù…ïŸ•Õ•Ω∏ùt§§§(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅï±ÕîË(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅçÖ±ïπëÖ…}Õï…Ÿ•çîπÕï—}ëÖÂ}çΩ±Ω»°AI=%1}%±ëÖ‰±ç•ê§(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ…ï—’…∏ÅÕï±òπ}Ω¨°ëÖÂ}çΩ±Ω…Ã†§πùï–°ëÖ‰§∞ùQÖùôÖ…âîÅùïÕ¡ï•ç°ï…–∏ú§(ÄÄÄÄÄÄÄÄÄÄÄÅ•òÅ¡Ö—†ÙÙúΩÖ¡§ΩçÖ±ïπëÖ»ΩçΩ±Ω…ÃúË(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅïπ—…•ïÃıàπùï–†ùïπ—…•ïÃú§ÅΩ»Åmt(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ•òÅ±ï∏°ïπ—…•ïÃ§ÑÙ‘ËÅ…Ö•ÕîÅYÖ±’ï……Ω»†ù19I}IEU%IM}aQ1e}%Y}=1=ILú§(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ¡Ö•…Ãıl°Õ—»°‡πùï–†ù—•—±îú∞úú§§±Õ—»°‡πùï–†ù—Ω≠ï∏ú∞úú§§§ÅôΩ»Å‡Å•∏Åïπ—…•ïÕt(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ≈’ï’îπ›Ö•–°≈’ï’îπÕ’âµ•–†ùçÖ±ïπëÖ»πçΩ±Ω…Ãú±±ÖµâëÑÈçÖ±ïπëÖ…}Õï…Ÿ•çîπÕï—}çΩ±Ω…}±ïùïπê°AI=%1}%±¡Ö•…Ã§§§(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ…ï—’…∏ÅÕï±òπ}Ω¨°çΩ±Ω…Ã†§∞ù-Ö±ïπëï…±ïùïπëîÅùïÕ¡ï•ç°ï…–∏ú§(ÄÄÄÄÄÄÄÄÄÄÄÅ•òÅ¡Ö—†πÕ—Ö…—Õ›•—††úΩÖ¡§Ω—…ÖÕ†ºú§ÅÖπêÅ¡Ö—†πïπëÕ›•—††úΩ…ïÕ—Ω…îú§Ë(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅï•êı¡Ö—†πÕ¡±•–†úºú•lÕtÏÅ…ïÿı•π–°àπùï–†ù…ïŸ•Õ•Ω∏ú§§(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ≈’ï’îπ›Ö•–°≈’ï’îπÕ’âµ•–†ù—…ÖÕ†π…ïÕ—Ω…îú±±ÖµâëÑÈÕ—Ω…îπ…ïÕ—Ω…ï}ïπ—•—‰°ï•ê±…ïÿ§§§(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ…ï—’…∏ÅÕï±òπ}Ω¨°Õ—Ω…îπùï—}ïπ—•—‰°ï•ê§∞ù%π°Ö±–Å›•ïëï…°ï…ùïÕ—ï±±–∏ú§(ÄÄÄÄÄÄÄÄÄÄÄÅ•òÅ¡Ö—†ÙÙúΩÖ¡§Ωë•ÖùπΩÕ—•çÃΩç…ïÖ—îúË(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ•òÅàπùï–†ùçΩπô•…µïêú§Å•ÃÅπΩ–ÅQ…’îËÅ…Ö•ÕîÅYÖ±’ï……Ω»†ù%}=9%I5}IEU%Iú§(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ¿ıç…ïÖ—ï}ë•ÖùπΩÕ—•ç}…ï¡Ω…–†§(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ…ï—’…∏ÅÕï±òπ}Ω¨°Ïù¡Ö—†úÈÕ—»°¿§∞ùπÖµîúÈ¿ππÖµïÙ∞ù•ÖùπΩÕïâï…•ç°–Å±Ω≠Ö∞Åï…Õ—ï±±–∏ú§(ÄÄÄÄÄÄÄÄÄÄÄÅ•òÅ¡Ö—†ÙÙúΩÖ¡§Ω…ïµ•πëï…ÃΩµÖ…¨µëï±•Ÿï…ïêúË(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅï•êıÕ—»°àπùï–†ùïπ—•—Â}•êú∞úú§§ÏÅ…ïµ•πëï…}Ö–ıÕ—»°àπùï–†ù…ïµ•πëï…}Ö–ú∞úú§§ÏÅ¡±Ö—ôΩ…¥ıÕ—»°àπùï–†ù¡±Ö—ôΩ…¥ú∞ù±•π’‡ú§§(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ…ïµ•πëï…}ïπù•πîπµÖ…≠}ëï±•Ÿï…ïê°AI=%1}%±ï•ê±…ïµ•πëï…}Ö–±¡±Ö—ôΩ…¥±Õ—»°àπùï–†ù…ïÕ’±–ú∞ù1%YIú§§§(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ…ï—’…∏ÅÕï±òπ}Ω¨°9Ωπî∞ùIïµ•πëï»ÅÖ±ÃÅÈ’ùïÕ—ï±±–Å¡…Ω—Ω≠Ω±±•ï…–∏ú§(ÄÄÄÄÄÄÄÄÄÄÄÅ•òÅ¡Ö—†ÙÙúΩÖ¡§ΩÖÕÕï—ÃΩ•µ¡Ω…–úË(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅÕ…åıAÖ—†°Õ—»°àπùï–†ùÕΩ’…çï}¡Ö—†ú∞úú§§§(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ≠•πêıÕ—»°àπùï–†ù≠•πêú∞úú§§(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ—•—±îıÕ—»°àπùï–†ù—•—±îú∞úú§§(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ¥ıÖÕÕï—}µÖπÖùï»π•µ¡Ω…—}ÖÕÕï–°Õ…å±≠•πê±—•—±î§(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ…ï—’…∏ÅÕï±òπ}Ω¨°¥∞ùÕÕï–ÅÕ•ç°ï»Å•µ¡Ω…—•ï…–∏ú§(ÄÄÄÄÄÄÄÄÄÄÄÅ•òÅ¡Ö—†ÙÙúΩÖ¡§ΩÖÕÕï—ÃΩŸÖ±•ëÖ—îúË(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅÖ•êıÕ—»°àπùï–†ùÖÕÕï—}•êú∞úú§§(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ…ï—’…∏ÅÕï±òπ}Ω¨°ÖÕÕï—}µÖπÖùï»πŸÖ±•ëÖ—ï}Ω…}≈’Ö…Öπ—•πî°Ö•ê§∞ùÕÕï–Åùï¡ÀÒô–∏ú§(ÄÄÄÄÄÄÄÄÄÄÄÅ•òÅ¡Ö—†ÙÙúΩÖ¡§ΩÖÕÕï—ÃΩïë•–µ—ï·–úË(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅÖ•êıÕ—»°àπùï–†ùÖÕÕï—}•êú∞úú§§ÏÅ—ï·–ıÕ—»°àπùï–†ù—ï·–ú∞úú§§ÏÅ…ïÿı•π–°àπùï–†ù…ïŸ•Õ•Ω∏ú§§(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ…ï—’…∏ÅÕï±òπ}Ω¨°ÖÕÕï—}µÖπÖùï»πïë•—}—ï·—}ÖÕÕï–°Ö•ê±—ï·–±…ïÿ§∞ùΩ≠’µïπ–Å…ïŸ•Õ•ΩπÕùïÕ•ç°ï…–ÅùïÕ¡ï•ç°ï…–∏ú§(ÄÄÄÄÄÄÄÄÄÄÄÅ•òÅ¡Ö—†ÙÙúΩÖ¡§ΩÖ’ë•ºΩÕ—Ö…–úË(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ…ï—’…∏ÅÕï±òπ}Ω¨°Ö’ë•Ω}…ïçΩ…ëï»πÕ—Ö…–°Õ—»°àπùï–†ùâÖç≠ïπêú∞ù¡’±Õîú§§±Õ—»°àπùï–†ùëïŸ•çîú∞ùëïôÖ’±–ú§§§∞ù’ôπÖ°µîÅùïÕ—Ö…—ï–∏ú§(ÄÄÄÄÄÄÄÄÄÄÄÅ•òÅ¡Ö—†ÙÙúΩÖ¡§ΩÖ’ë•ºΩÕ—Ω¿úË(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ…ï—’…∏ÅÕï±òπ}Ω¨°Ö’ë•Ω}…ïçΩ…ëï»πÕ—Ω¡}Öπë}çΩµµ•–°Õ—»°àπùï–†ù—•—±îú∞ùM¡…Öç°µïµºú§§§∞ù’ôπÖ°µîÅÕ•ç°ï»ÅùïÕ¡ï•ç°ï…–∏ú§(ÄÄÄÄÄÄÄÄÄÄÄÅ•òÅ¡Ö—†ÙÙúΩÖ¡§Ω¡±ÖÂ±•Õ—ÃúË(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅï•ê±…ïÿı¡±ÖÂ±•Õ—}Õï…Ÿ•çîπç…ïÖ—î°AI=%1}%±Õ—»°àπùï–†ù—•—±îú∞ùA±ÖÂ±•Õ–ú§§§(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ…ï—’…∏ÅÕï±òπ}Ω¨°Õ—Ω…îπùï—}ïπ—•—‰°ï•ê§∞ùA±ÖÂ±•Õ–Åï…Õ—ï±±–∏ú§(ÄÄÄÄÄÄÄÄÄÄÄÅ•òÅ¡Ö—†πÕ—Ö…—Õ›•—††úΩÖ¡§Ω¡±ÖÂ±•Õ—Ãºú§ÅÖπêÅ¡Ö—†πïπëÕ›•—††úΩÖëêú§Ë(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅï•êı¡Ö—†πÕ¡±•–†úºú•lÕt(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ¡±ÖÂ±•Õ—}Õï…Ÿ•çîπÖëë}ÖÕÕï–°ï•ê±AI=%1}%±•π–°àπùï–†ù…ïŸ•Õ•Ω∏ú§§±Õ—»°àπùï–†ùÖÕÕï—}•êú§§§(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ…ï—’…∏ÅÕï±òπ}Ω¨°Õ—Ω…îπùï—}ïπ—•—‰°ï•ê§∞ùÕÕï–ÅÈ’»ÅA±ÖÂ±•Õ–Å°•πÈ’ùïõÒù–∏ú§(ÄÄÄÄÄÄÄÄÄÄÄÅ•òÅ¡Ö—†ÙÙúΩÖ¡§Ω≈’•ç¨µπΩ—îúË(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ¿ıÖ¡¡ïπë}≈’•ç≠}πΩ—î°àπùï–†ù—•—±îú∞ù9Ω—•Èï∏ú§±àπùï–†ù—ï·–ú∞úú§§ÏÅ…ï—’…∏ÅÕï±òπ}Ω¨°Ïù¡Ö—†úÈÕ—»°¿§∞ùπÖµîúÈ¿ππÖµïÙ∞ùQï·—ëÖ—ï§Åï…üëπÈ–∏ú§(ÄÄÄÄÄÄÄÄÄÄÄÅ•òÅ¡Ö—†ÙÙúΩÖ¡§Ω≈’•ç¨µπΩ—îΩΩ¡ï∏úË(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ¿ıAI=)PºùπΩ—•Èï∏úΩÕÖôï}πΩ—ï}ô•±ïπÖµî°àπùï–†ù—•—±îú∞ù9Ω—•Èï∏ú§§ÏÅΩ¨±µÕúıΩ¡ïπ}¡Ö—†°¿§ÏÅ…ï—’…∏ÅÕï±òπ}Ω¨°ÏùΩ¡ïπïêúÈΩ¨∞ù¡Ö—†úÈÕ—»°¿•Ù±µÕú§(ÄÄÄÄÄÄÄÄÄÄÄÅ•òÅ¡Ö—†ÙÙúΩÖ¡§Ω≈’•ç¨µπΩ—îΩÕ°Ö…îúË(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ¿ıAI=)PºùπΩ—•Èï∏úΩÕÖôï}πΩ—ï}ô•±ïπÖµî°àπùï–†ù—•—±îú∞ù9Ω—•Èï∏ú§§(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ•òÅπΩ–Å¿πï·•Õ—Ã†§ËÅ…Ö•ÕîÅ•±ï9Ω—Ω’πë……Ω»†ù9=Q}%1}9=Q}=U9ú§(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅΩ¨±µÕúıÕ°Ö…ï}πΩ—î°¿§ÏÅ…ï—’…∏ÅÕï±òπ}Ω¨°ÏùΩ¡ïπïêúÈΩ¨∞ù¡Ö—†úÈÕ—»°¿•Ù±µÕú§(ÄÄÄÄÄÄÄÄÄÄÄÅ•òÅ¡Ö—†ÙÙúΩÖ¡§Ω’πëºúËÅ≈’ï’îπ›Ö•–°≈’ï’îπÕ’âµ•–†ù’§π’πëºú∞Å±ÖµâëÑËÅÕ—Ω…îπ’πëΩ}±ÖÕ–°AI=%1}%§§§ÏÅ…ï—’…∏ÅÕï±òπ}Ω¨°Ö¡•}Õ—Ö—î†§∞ù1ï—È—îÉπëï…’πúÅÀÒç≠üëπù•ú∏ú§(ÄÄÄÄÄÄÄÄÄÄÄÅ•òÅ¡Ö—†ÙÙúΩÖ¡§Ω…ïëºúËÅ≈’ï’îπ›Ö•–°≈’ï’îπÕ’âµ•–†ù’§π…ïëºú∞Å±ÖµâëÑËÅÕ—Ω…îπ…ïëΩ}±ÖÕ–°AI=%1}%§§§ÏÅ…ï—’…∏ÅÕï±òπ}Ω¨°Ö¡•}Õ—Ö—î†§∞üπëï…’πúÅ›•ïëï…°Ω±–∏ú§(ÄÄÄÄÄÄÄÄÄÄÄÅ•òÅ¡Ö—†ÙÙúΩÖ¡§ΩÕï——•πùÃúË(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅôΩ»Å¨±ÿÅ•∏Åàπ•—ïµÃ†§ËÅ≈’ï’îπ›Ö•–°≈’ï’îπÕ’âµ•–†ùÕï——•πùÃπÕï–ú∞Å±ÖµâëÑÅ¨ı¨±ÿıÿËÅÕï——•πùÕ}Õï…Ÿ•çîπÕï–°AI=%1}%±¨±ÿ§§§(ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ…ï—’…∏ÅÕï±òπ}Ω¨°Õï——•πùÕ}Õï…Ÿ•çîπùï—}Ö±∞°AI=%1}%§∞ù•πÕ—ï±±’πùï∏ÅùïÕ¡ï•ç°ï…–∏ú§(ÄÄÄÄÄÄÄÄÄÄÄÅ…ï—’…∏ÅÕï±òπ}©ÕΩ∏°ÏùΩ¨úÈÖ±Õî∞ùµïÕÕÖùîúËù9•ç°–Åùïô’πëï∏ùÙ∞–¿–§(ÄÄÄÄÄÄÄÅï·çï¡–Å·çï¡—•Ω∏ÅÖÃÅîË(ÄÄÄÄÄÄÄÄÄÄÄÅ…ï—’…∏ÅÕï±òπ}ôÖ•∞°î∞–¿‰Å•òÅÕ—»°î§ÙÙùIY%M%=9}=91%PúÅï±ÕîÄ–¿¿§()ëïòÅ…’∏°¡Ω…–Ù‡‹ÿ‘±Ω¡ïπ}â…Ω›Õï»ıQ…’î§Ë(ÄÄÄÅΩÃπç°ë•»°U$§(ÄÄÄÅ—…‰Ë(ÄÄÄÄÄÄÄÅÕï…Ÿï»ıQ°…ïÖë•πù!QQAMï…Ÿï»††úƒ»‹∏¿∏¿∏ƒú±¡Ω…–§±!Öπë±ï»§(ÄÄÄÅï·çï¡–Å=M……Ω»ÅÖÃÅîË(ÄÄÄÄÄÄÄÅ≈’ï’îπÕ—Ω¿†§ÏÅÕ—Ω…îπç±ΩÕî†§(ÄÄÄÄÄÄÄÅ•òÅùï—Ö——»°î∞ùï……πºú±9Ωπî§ÙÙ‰‡Ë(ÄÄÄÄÄÄÄÄÄÄÄÅ¡…•π–°òùA=IQ}	1PËÄƒ»‹∏¿∏¿∏ƒÈÌ¡Ω…—Ù∏Å	•——îÅMQIQ9}1%9U`πÕ†ÅŸï…›ïπëï∏ÏÅëï»Å1Ö’πç°ï»Åﬂë°±–ÅÕ•ç°ï»Åï•πï∏Åô…ï•ï∏ÅAΩ…–Å’πêÅâïïπëï–Å≠ï•πîÅô…ïµëï∏ÅA…ΩÈïÕÕî∏ú±ô•±îıÕÂÃπÕ—ëï…»±ô±’Õ†ıQ…’î§(ÄÄÄÄÄÄÄÅ…Ö•Õî(ÄÄÄÅ’…∞ıòù°——¿Ëººƒ»‹∏¿∏¿∏ƒÈÌ¡Ω…—ÙΩ•πëï‡π°—µ∞ú(ÄÄÄÅ¡…•π–°òù=$Ä¥ÅAI=Y=]IÄ¥Å%<ÅÌAA}YIM%=9ÙÅ≥ë’ô–ËÅÌ’…±Ùú±ô±’Õ†ıQ…’î§(ÄÄÄÅ•òÅΩ¡ïπ}â…Ω›Õï»ËÅ—°…ïÖë•πúπQ•µï»†∏–±±ÖµâëÑÈ›ïââ…Ω›Õï»πΩ¡ï∏°’…∞§§πÕ—Ö…–†§(ÄÄÄÅ—…‰ËÅÕï…Ÿï»πÕï…Ÿï}ôΩ…ïŸï»†§(ÄÄÄÅô•πÖ±±‰Ë(ÄÄÄÄÄÄÄÅ≈’ï’îπÕ—Ω¿†§ÏÅÕ—Ω…îπç±ΩÕî†§ÏÅÕï…Ÿï»πÕï…Ÿï…}ç±ΩÕî†§()•òÅ}}πÖµï}|ÙÙù}}µÖ•π}|úË(ÄÄÄÅ¡Ω…–ı•π–°ΩÃπïπŸ•…Ω∏πùï–†ùAI=Y=]I}A=IPú∞ú‡‹ÿ‘ú§§(ÄÄÄÅ…’∏°¡Ω…–∞Äú¥µπºµâ…Ω›Õï»úÅπΩ–Å•∏ÅÕÂÃπÖ…ùÿ§