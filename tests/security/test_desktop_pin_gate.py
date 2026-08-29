#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import base64
import http.client
import os
import socket
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


def main():
    port=free_port()
    with tempfile.TemporaryDirectory(prefix='provoware-pin-gate-') as td:
        env=os.environ.copy()
        env['PROVOWARE_PROJECT_PATH']=str(Path(td)/'project')
        env['PROVOWARE_PORT']=str(port)
        env['PYTHONPATH']=str(ROOT/'core'/'reference_python')
        p=subprocess.Popen([sys.executable,'-S',str(SERVER),'--no-browser'],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        try:
            wait(port,p)
            status,h,_=request(port,'/index.html')
            assert status==401,status
            assert 'Basic realm="PROVOWARE Desktop PIN"' in h.get('WWW-Authenticate','')
            print('PASS unauthenticated UI is blocked')

            status,_,_=request(port,'/index.html',auth('9999'))
            assert status==401,status
            print('PASS wrong PIN is rejected')

            status,_,body=request(port,'/index.html',auth('0000'))
            assert status==200,(status,body[:120])
            print('PASS correct profile PIN unlocks UI')

            status,_,body=request(port,'/api/state',auth('0000'))
            assert status==200,(status,body[:160])
            assert b'"ok": true' in body
            print('PASS authenticated API access works')

            linux=(ROOT/'STARTEN_LINUX.sh').read_text(encoding='utf-8')
            headless=(ROOT/'STARTEN_OHNE_BROWSER.sh').read_text(encoding='utf-8')
            assert 'app/secure_server.py' in linux and 'app/server.py' not in linux
            assert 'app/secure_server.py' in headless and 'app/server.py' not in headless
            print('PASS official Linux launchers enforce secure server')
            print('SUMMARY total=5 passed=5 failed=0')
        finally:
            p.terminate()
            try:p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill();p.wait(timeout=5)


if __name__=='__main__':
    main()
