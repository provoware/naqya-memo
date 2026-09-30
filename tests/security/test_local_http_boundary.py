from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"app"))

from http_security import host_is_loopback, origin_is_same_loopback, project_fingerprint, resolve_static_path


def test_static_path_stays_inside_ui_root():
    ui=ROOT/"ui"/"reference_web"
    assert resolve_static_path(ui,"/index.html")== (ui/"index.html").resolve()
    assert resolve_static_path(ui,"/assets/../app.js")== (ui/"app.js").resolve()


def test_static_path_traversal_is_rejected():
    ui=ROOT/"ui"/"reference_web"
    assert resolve_static_path(ui,"/../../registry/PROJECT_STATUS.json") is None
    assert resolve_static_path(ui,"/%2e%2e/%2e%2e/registry/VERSION.json") is None


def test_host_boundary_accepts_only_expected_loopback_host():
    assert host_is_loopback("127.0.0.1:8765",8765)
    assert host_is_loopback("LOCALHOST:8765",8765)
    assert not host_is_loopback("attacker.example:8765",8765)
    assert not host_is_loopback("127.0.0.1:9999",8765)
    assert not host_is_loopback(None,8765)


def test_origin_boundary_rejects_foreign_websites():
    assert origin_is_same_loopback(None,8765)
    assert origin_is_same_loopback("http://127.0.0.1:8765",8765)
    assert origin_is_same_loopback("http://localhost:8765",8765)
    assert not origin_is_same_loopback("https://evil.example",8765)
    assert not origin_is_same_loopback("http://localhost:9999",8765)
    assert not origin_is_same_loopback("file://",8765)


def test_project_identity_is_non_path_fingerprint():
    p=(ROOT/"runtime"/"projektordner").resolve()
    value=project_fingerprint(p)
    assert len(value)==64
    int(value,16)
    assert str(p) not in value


if __name__=="__main__":
    tests=[v for k,v in sorted(globals().items()) if k.startswith("test_")]
    bad=[]
    for t in tests:
        try:t();print("PASS",t.__name__)
        except Exception as e:bad.append((t.__name__,repr(e)));print("FAIL",t.__name__,repr(e))
    print(f"SUMMARY total={len(tests)} passed={len(tests)-len(bad)} failed={len(bad)}")
    raise SystemExit(1 if bad else 0)
