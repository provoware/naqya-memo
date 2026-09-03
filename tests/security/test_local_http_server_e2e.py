from pathlib import Path
import http.client, json, os, socket, subprocess, sys, tempfile, time

ROOT=Path(__file__).resolve().parents[2]
SERVER=ROOT/"app/server.py"


def free_port():
    s=socket.socket();s.bind(("127.0.0.1",0));p=s.getsockname()[1];s.close();return p


def request(port,method,path,body=None,headers=None):
    conn=http.client.HTTPConnection("127.0.0.1",port,timeout=3)
    hdrs={"Host":f"127.0.0.1:{port}"}
    if headers: hdrs.update(headers)
    conn.request(method,path,body=body,headers=hdrs)
    resp=conn.getresponse(); data=resp.read(); status=resp.status
    out_headers={k.lower():v for k,v in resp.getheaders()}
    conn.close()
    return status,data,out_headers


def oversized_headers_only_request(port,path,declared_length):
    """Prove rejection occurs from headers alone, before a large body is accepted."""
    conn=http.client.HTTPConnection("127.0.0.1",port,timeout=3)
    conn.putrequest("POST",path,skip_host=True)
    conn.putheader("Host",f"127.0.0.1:{port}")
    conn.putheader("Content-Type","application/json")
    conn.putheader("Content-Length",str(declared_length))
    conn.putheader("Origin",f"http://127.0.0.1:{port}")
    conn.endheaders()
    resp=conn.getresponse(); data=resp.read(); status=resp.status
    conn.close()
    return status,data


def wait_ready(port,proc):
    deadline=time.time()+12
    while time.time()<deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"server exited early rc={proc.returncode}")
        try:
            status,data,_=request(port,"GET","/api/health")
            if status==200 and json.loads(data).get("ok"):
                return
        except Exception:
            pass
        time.sleep(.15)
    raise TimeoutError("server health did not become ready")


def main():
    port=free_port()
    with tempfile.TemporaryDirectory(prefix="naqya-http-security-") as td:
        env=os.environ.copy()
        env["PROVOWARE_PROJECT_PATH"]=str(Path(td)/"projekt")
        env["PROVOWARE_PORT"]=str(port)
        proc=subprocess.Popen(
            [sys.executable,"-S",str(SERVER),"--no-browser"],
            cwd=str(ROOT),env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,
        )
        try:
            wait_ready(port,proc)

            status,data,headers=request(port,"GET","/api/health")
            payload=json.loads(data)["data"]
            assert status==200
            assert payload["service"]=="oi-provoware-io"
            assert len(payload["project_fingerprint"])==64
            assert "project" not in payload and "db" not in payload
            assert headers.get("x-frame-options")=="DENY"
            assert headers.get("x-content-type-options")=="nosniff"

            status,_,_=request(port,"GET","/api/health",headers={"Host":f"attacker.example:{port}"})
            assert status==403

            status,_,_=request(port,"GET","/%2e%2e/%2e%2e/registry/VERSION.json")
            assert status==404

            body=b'{}'
            status,_,_=request(port,"POST","/api/settings",body,{
                "Content-Type":"application/json",
                "Content-Length":str(len(body)),
                "Origin":"https://evil.example",
            })
            assert status==403

            status,_,_=request(port,"POST","/api/settings",body,{
                "Content-Type":"text/plain",
                "Content-Length":str(len(body)),
                "Origin":f"http://127.0.0.1:{port}",
            })
            assert status==415

            status,_=oversized_headers_only_request(port,"/api/settings",2*1024*1024+2)
            assert status==413

            print("PASS local HTTP server E2E boundary")
        finally:
            proc.terminate()
            try: proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill();proc.wait(timeout=5)

if __name__=="__main__":
    main()
