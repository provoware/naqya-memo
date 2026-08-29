#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import base64
import http.client
import os
import socket
import stat
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[2]
SERVER=ROOT/'app'/'secure_server.py'


def free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1',0))
        return s.getsockname()[1]


def auth(pin):
    token=base64.b64encode(f'provoware:{pin}'.encode()).decode()
    return {'Authorization':f'Basic {token}'}


def request(port,path='/',headers=None):
    c=http.client.HTTPConnection('127.0.0.1',port,timeout=4)
    c.request('GET',path,headers=headers or {})
    r=c.getresponse(); body=r.read(); out=(r.status,dict(r.getheaders()),body); c.close(); return out


def assert_no_store(headers):
    cache=headers.get('Cache-Control','')
    assert 'no-store' in cache and 'no-cache' in cache and 'max-age=0' in cache,headers
    assert headers.get('Pragma')=='no-cache',headers
    assert headers.get('Expires')=='0',headers
    assert 'Authorization' in headers.get('Vary',''),headers


def wait(port,proc):
    deadline=time.time()+12
    while time.time()<deadline:
        if proc.poll() is not None:
            raise AssertionError(f'server exited rc={proc.returncode}: {proc.stdout.read()}')
        try:
            status,_,_=request(port,'/index.html')
            if status==401:
                return
        except OSError:
            pass
        time.sleep(.1)
    raise AssertionError('secure server did not become ready')


def read_first_pin(project):
    path=project/'nutzer-einstellungen'/'ERSTSTART_PIN_EINMAL.txt'
    deadline=time.time()+5
    while time.time()<deadline and not path.is_file():
        time.sleep(.05)
    assert path.is_file(), 'one-time first PIN file missing'
    lines=path.read_text(encoding='utf-8').splitlines()
    pin=next((line.split(':',1)[1].strip() for line in lines if line.startswith('PIN:')),None)
    assert pin and len(pin)==4 and pin.isdigit() and pin!='0000',pin
    mode=stat.S_IMODE(path.stat().st_mode)
    assert mode==0o600,oct(mode)
    return path,pin


def distinct_wrong_pins(first_pin):
    out=[]
    for pin in ('1111','2222','3333','4444'):
        if pin not in (first_pin,'0000'):
            out.append(pin)
        if len(out)==2:
            return out
    raise AssertionError('could not choose distinct wrong PINs')


def main():
    port=free_port()
    with tempfile.TemporaryDirectory(prefix='provoware-pin-gate-') as td:
        project=Path(td)/'project'
        env=os.environ.copy()
        env['PROVOWARE_PROJECT_PATH']=str(project)
        env['PROVOWARE_PORT']=str(port)
        env['PYTHONPATH']=str(ROOT/'core'/'reference_python')
        env['PROVOWARE_AUTH_MAX_FAILURES']='3'
        env['PROVOWARE_AUTH_FAILURE_WINDOW']='30'
        env['PROVOWARE_AUTH_LOCKOUT_SECONDS']='1'
        p=subprocess.Popen([sys.executable,'-S',str(SERVER),'--no-browser'],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        try:
            wait(port,p)
            first_pin_file,first_pin=read_first_pin(project)
            print('PASS first profile receives a random four-digit PIN other than 0000')
            print('PASS one-time PIN file is mode 0600')

            status,h,_=request(port,'/index.html')
            assert status==401,status
            assert 'Basic realm="PROVOWARE Desktop PIN"' in h.get('WWW-Authenticate','')
            assert_no_store(h)
            print('PASS unauthenticated UI is blocked without consuming failure budget')
            print('PASS authentication challenges are explicitly non-cacheable')

            for _ in range(4):
                status,_,_=request(port,'/index.html',auth('0000'))
                assert status==401,status
            print('PASS repeated requests with the same wrong PIN count only once')

            wrong1,wrong2=distinct_wrong_pins(first_pin)
            status,_,_=request(port,'/index.html',auth(wrong1))
            assert status==401,status
            print('PASS second distinct wrong PIN is rejected without premature lockout')

            status,h,_=request(port,'/index.html',auth(wrong2))
            assert status==429,status
            assert int(h.get('Retry-After','0'))>=1,h
            assert_no_store(h)
            print('PASS third distinct wrong PIN triggers temporary HTTP 429 lockout')

            status,h,_=request(port,'/index.html',auth(first_pin))
            assert status==429,status
            assert int(h.get('Retry-After','0'))>=1,h
            print('PASS correct PIN cannot bypass an active temporary lockout')

            time.sleep(1.15)
            status,h,body=request(port,'/index.html',auth(first_pin))
            assert status==200,(status,body[:120])
            assert_no_store(h)
            print('PASS correct PIN works again automatically after lockout expiry')
            print('PASS authenticated UI responses are explicitly non-cacheable')

            deadline=time.time()+2
            while time.time()<deadline and first_pin_file.exists():
                time.sleep(.05)
            assert not first_pin_file.exists(),'one-time PIN file survived successful login'
            print('PASS one-time PIN file is removed after first successful login')

            status,h,body=request(port,'/api/state',auth(first_pin))
            assert status==200,(status,body[:160])
            assert b'"ok": true' in body
            assert_no_store(h)
            print('PASS authenticated API access works after rate-limit recovery')
            print('PASS authenticated API responses are explicitly non-cacheable')

            linux=(ROOT/'STARTEN_LINUX.sh').read_text(encoding='utf-8')
            headless=(ROOT/'STARTEN_OHNE_BROWSER.sh').read_text(encoding='utf-8')
            assert 'app/secure_server.py' in linux and 'app/server.py' not in linux
            assert 'app/secure_server.py' in headless and 'app/server.py' not in headless
            print('PASS official Linux launchers enforce secure server')
            print('SUMMARY total=14 passed=14 failed=0')
        finally:
            p.terminate()
            try:p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill();p.wait(timeout=5)


if __name__=='__main__':
    main()
