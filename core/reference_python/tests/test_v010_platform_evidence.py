from pathlib import Path
import tempfile, sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/"core/reference_python"))
from provoware_core.platform import linux_capability_probe, write_probe, android_contract, ios_contract

def test_linux_probe_native():
    with tempfile.TemporaryDirectory() as td:
        p=linux_capability_probe(); p["filesystem_write_test"]=write_probe(Path(td))
        assert p["evidence_type"]=="NATIVE_RUNTIME_PROBE"
        assert p["filesystem_write_test"] is True

def test_mobile_contracts_not_falsely_native():
    a=android_contract(); i=ios_contract()
    assert a["native_device_tested"] is False and a["evidence_type"]=="CONTRACT_ONLY"
    assert i["native_device_tested"] is False and i["evidence_type"]=="CONTRACT_ONLY"

if __name__=="__main__":
    tests=[v for k,v in sorted(globals().items()) if k.startswith("test_")]
    bad=[]
    for t in tests:
        try:t();print("PASS",t.__name__)
        except Exception as e:bad.append((t.__name__,repr(e)));print("FAIL",t.__name__,repr(e))
    print(f"SUMMARY total={len(tests)} passed={len(tests)-len(bad)} failed={len(bad)}")
    if bad:raise SystemExit(1)
