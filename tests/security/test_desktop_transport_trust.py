#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
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


def request(port,headers=None):
    c=http.client.HTTPConnection('127.0.0.1',port,timeout=4)
    c.request('GET','/index.html',headers=headers or {})
    r=c.getresponse(); body=r.read(); out=(r.status,dict(r.getheaders()),body); c.close(); return out


def assert_no_store(headers):
    assert 'no-store' in headers.get('Cache-Control',''),headers


def wait(port,proc):
    deadline=time.time()+12
    while time.time()<deadline:
        if proc.poll() is not None:
            raise AssertionError(f'server exited rc={proc.returncode}: {proc.stdout.read()}')
        try:
            if request(port)[0]==401:
                return
        except OSError:
            pass
        time.sleep(.1)
    raise AssertionError('secure server did not become ready')


def main():
    port=free_port()
    authority=f'127.0.0.1:{port}'
    local_authority=f'localhost:{port}'
    with tempfile.TemporaryDirectory(prefix='provoware-transport-trust-') as td:
        env=os.environ.copy()
        env['PROVOWARE_PROJECT_PATH']=str(Path(td)/'project')
        env['PROVOWARE_PORT']=str(port)
        env['PYTHONPATH']=str(ROOT/'core'/'reference_python')
        proc=subprocess.Popen([sys.executable,'-S',str(SERVER),'--no-browser'],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        try:
            wait(port,proc)

            status,h,body=request(port,{'Host':'rebind.example'})
            assert status==421,(status,body)
            assert b'LOCAL_HOST_BLOCKED' in body
            assert_no_store(h)
            print('PASS foreign Host is rejected before authentication')

            status,h,body=request(port,{'Host':authority,'Origin':'https://evil.example'})
            assert status==403,(status,body)
            assert b'CROSS_SITE_ORIGIN_BLOCKED' in body
            assert_no_store(h)
            print('PASS foreign Origin is rejected before authentication')

            status,h,body=request(port,{'Host':authority,'Sec-Fetch-Site':'cross-site'})
            assert status==403,(status,body)
            assert b'CROSS_SITE_REQUEST_BLOCKED' in body
            assert_no_store(h)
            print('PASS browser cross-site request metadata is rejected')

            status,_,_=request(port,{'Host':local_authority})
            assert status==401,status
            print('PASS localhost authority remains compatible with normal PIN challenge')

            status,_,_=request(port,{'Host':authority,'Origin':f'http://{authority}','Sec-Fetch-Site':'same-origin'})
            assert status==401,status
            print('PASS same-origin loopback request remains compatible with normal PIN challenge')
            print('SUMMARY total=5 passed=5 failed=0')
        finally:
            proc.terminate()
            try: proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill(); proc.wait(timeout=5)


if __name__=='__main__':
    main()
