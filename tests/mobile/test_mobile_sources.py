from pathlib import Path
import re, sys, json
ROOT=Path(__file__).resolve().parents[2]

def must(path, tokens):
    s=(ROOT/path).read_text(encoding='utf-8')
    for t in tokens:
        assert t in s, f'{t!r} missing in {path}'

def test_android_runtime_source():
    must('platform/android/app/src/main/java/de/provoware/naqya/MainActivity.kt', ['WebView','addJavascriptInterface','onShowFileChooser','file:///android_asset/www/index.html','FLAG_DEBUGGABLE','provoware_acceptance'])
    must('platform/android/app/src/main/java/de/provoware/naqya/NativeBridge.kt', ['MediaRecorder','scheduleReminderWithPermission','POST_NOTIFICATIONS','RECORD_AUDIO','shareText','audioStart','audioStop','acceptanceResult','cancelReminder'])
    must('platform/android/app/src/main/java/de/provoware/naqya/ReminderReceiver.kt', ['NotificationChannel','NotificationManager'])
    must('platform/android/app/src/main/AndroidManifest.xml', ['android.permission.RECORD_AUDIO','android.permission.POST_NOTIFICATIONS','ReminderReceiver'])
    read=(ROOT/'platform/android/README.md').read_text()
    assert 'RUNTIME_SOURCE_COMPLETE' in read

def test_ios_runtime_source():
    must('platform/ios/OIProvowareIO/AppDelegate.swift',['WKWebView','loadFileURL','NativeBridge'])
    must('platform/ios/OIProvowareIO/NativeBridge.swift',['AVAudioRecorder','UNUserNotificationCenter','UIActivityViewController','requestRecordPermission','scheduleReminder','acceptanceResult','cancelReminder'])
    must('platform/ios/Info.plist',['0.12.2','NSMicrophoneUsageDescription'])
    must('platform/ios/OIProvowareIO.xcodeproj/project.pbxproj',['com.apple.product-type.application','IPHONEOS_DEPLOYMENT_TARGET = 16.0','WebAssets in Resources'])
    read=(ROOT/'platform/ios/README.md').read_text()
    assert 'XCODE_RUNTIME_SOURCE_COMPLETE' in read

def test_mobile_api_parity_surface():
    s=(ROOT/'ui/reference_web/mobile/mobile_core.js').read_text()
    routes=['/api/state','/api/memos','/api/todos','/api/events','/api/trash','/api/undo','/api/redo','/api/calendar/day-color','/api/calendar/colors','/api/reminders/pending','/api/platform/capabilities','/api/assets/quota','/api/assets/list','/api/assets/edit-text','/api/audio/capability','/api/audio/start','/api/audio/stop','/api/playlists','/api/diagnostics/preview']
    for r in routes: assert r in s, r
    assert 'IndexedDbStore' in s and 'createStructuredBackup' in s and 'validateStructuredBackup' in s and 'restoreStructuredBackup' in s and 'backupAssets' in s and 'FULL_COPY_PER_GENERATION' in s and 'sha256' in s
    for token in ['PBKDF2','pinHash','createProfile','verifyProfile','this.profile']:
        assert token in s, token

def test_ui_uses_mobile_adapter():
    idx=(ROOT/'ui/reference_web/index.html').read_text()
    app=(ROOT/'ui/reference_web/app.js').read_text()
    assert 'mobile/mobile_core.js' in idx and 'mobile/mobile_bootstrap.js' in idx and 'mobile/mobile_acceptance.js' in idx
    assert 'ProvowareMobileApi?.active' in app
    assert 'importFile(file' in app and 'assetUrl(id)' in app
    boot=(ROOT/'ui/reference_web/mobile/mobile_bootstrap.js').read_text()
    assert 'mobile-auth-overlay' in boot and 'verifyProfile' in boot and 'createProfile' in boot

if __name__=='__main__':
    tests=[v for k,v in sorted(globals().items()) if k.startswith('test_') and callable(v)]
    bad=[]
    for t in tests:
        try:t();print('PASS',t.__name__)
        except Exception as e:bad.append((t.__name__,repr(e)));print('FAIL',t.__name__,repr(e))
    print(f'SUMMARY total={len(tests)} passed={len(tests)-len(bad)} failed={len(bad)}')
    if bad: raise SystemExit(1)
