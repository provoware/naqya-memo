#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import argparse, json, os, socket, subprocess, urllib.request

def is_free(port: int) -> bool:
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        s.bind(("127.0.0.1",port))
        return True
    except OSError:
        return False
    finally:
        s.close()

def health(port: int):
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health",timeout=0.8) as r:
            payload=json.loads(r.read())
        if not payload.get("ok"): return None
        return payload.get("data") or {}
    except Exception:
        return None

def listener_info(port: int) -> str:
    for cmd in (
        ["ss","-ltnp",f"sport = :{port}"],
        ["lsof","-nP",f"-iTCP:{port}","-sTCP:LISTEN"],
    ):
        try:
            p=subprocess.run(cmd,text=True,capture_output=True,timeout=1.5)
            out=(p.stdout or p.stderr or "").strip()
            if p.returncode==0 and out:
                return " | ".join(line.strip() for line in out.splitlines()[-3:])
        except Exception:
            pass
    return "Listener konnte nicht näher bestimmt werden."

def load_version(root: Path) -> str:
    try:
        return json.loads((root/"registry/VERSION.json").read_text(encoding="utf-8")).get("version","UNKNOWN")
    except Exception:
        return "UNKNOWN"

def expected_project(root: Path) -> Path:
    return Path(os.environ.get("PROVOWARE_PROJECT_PATH", str(root/"runtime"/"projektordner"))).expanduser().resolve()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",required=True)
    ap.add_argument("--requested",type=int,default=int(os.environ.get("PROVOWARE_PORT","8765")))
    ap.add_argument("--max",type=int,default=int(os.environ.get("PROVOWARE_PORT_MAX","8795")))
    ap.add_argument("--strict",action="store_true",default=os.environ.get("PROVOWARE_PORT_STRICT")=="1")
    ap.add_argument("--evidence",action="store_true")
    args=ap.parse_args()

    root=Path(args.root).resolve()
    requested=args.requested
    current_version=load_version(root)
    wanted_project=expected_project(root)
    result={
        "requested_port":requested,
        "selected_port":None,
        "action":None,
        "reason":None,
        "version":current_version,
        "project":str(wanted_project),
    }

    if is_free(requested):
        result.update(action="START",selected_port=requested,reason="REQUESTED_PORT_FREE")
    else:
        h=health(requested)
        same_project=bool(h and Path(h.get("project","")).resolve()==wanted_project)
        same_version=bool(h and h.get("version")==current_version)
        if same_project and same_version:
            result.update(action="REUSE",selected_port=requested,reason="SAME_APP_ALREADY_RUNNING")
        elif args.strict:
            result.update(action="ERROR",selected_port=requested,
                          reason="REQUESTED_PORT_OCCUPIED_STRICT",
                          listener=listener_info(requested))
        else:
            free=None
            for port in range(requested+1,args.max+1):
                if is_free(port):
                    free=port; break
            if free is None:
                result.update(action="ERROR",reason="NO_FREE_PORT_IN_RANGE",
                              listener=listener_info(requested))
            else:
                result.update(action="START",selected_port=free,
                              reason="FALLBACK_PORT_SELECTED",
                              occupied_port=requested,
                              listener=listener_info(requested),
                              occupied_health=h)

    if args.evidence:
        out=root/"runtime"/"startup"
        out.mkdir(parents=True,exist_ok=True)
        (out/"LAST_START_PORT.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

    # machine-readable single-line output for shell launcher
    print(json.dumps(result,separators=(",",":"),ensure_ascii=False))
    return 0 if result["action"] in ("START","REUSE") else 98

if __name__=="__main__":
    raise SystemExit(main())
