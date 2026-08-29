from pathlib import Path
import tarfile, sys, tempfile, shutil, socket, subprocess, os, time, urllib.request, json
ROOT=Path(__file__).resolve().parents[3]

def test_linux_portable_archive_contains_launcher():
    tar=ROOT/'dist/OI_PROVOWARE_IO_V0.11_LINUX_PORTABLE.tar.gz'; assert tar.exists()
    with tarfile.open(tar) as t:
        names=t.getnames(); assert any(x.endswith('/START_OI_PROVOWARE_IO.sh') for x in names); assert any(x.endswith('/app/server.py') for x in names)

def test_android_structure_has_runtime_permissions():
    m=(ROOT/'platform/android/app/src/main/AndroidManifest.xml').read_text(); assert 'RECORD_AUDIO' in m and 'POST_NOTIFICATIONS' in m
    read=(ROOT/'platform/android/README.md').read_text(); assert 'BUILD_STRUCTURE_ONLY' in read

def test_ios_contract_has_microphone_usage_text():
    p=(ROOT/'platform/ios/Info.plist').read_text(); assert 'NSMicrophoneUsageDescription' in p
    read=(ROOT/'platform/ios/README.md').read_text(); assert 'BUILD_CONCEPT_ONLY' in read

if __name__=='__main__':
    tests=[v for k,v in sorted(globals().items()) if k.startswith('test_')]
    bad=[]
    for t in tests:
        try:t();print('PASS',t.__name__)
        except Exception as e:bad.append((t.__name__,repr(e)));print('FAIL',t.__name__,repr(e))
    print(f'SUMMARY total={len(tests)} passed={len(tests)-len(bad)} failed={len(bad)}')
    if bad:raise SystemExit(1)
