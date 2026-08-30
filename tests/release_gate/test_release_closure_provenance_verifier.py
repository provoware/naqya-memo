from pathlib import Path
import importlib.util
import json
import tempfile

ROOT = Path(__file__).resolve().parents[2]
ATTEST_PATH = ROOT / 'tools/release_gate/attest_release_closure.py'
VERIFY_PATH = ROOT / 'tools/release_gate/verify_release_closure_provenance.py'


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ATTEST = _load('attest_release_closure_for_test', ATTEST_PATH)
VERIFY = _load('verify_release_closure_provenance_for_test', VERIFY_PATH)


def _closure():
    return {
        'evaluated_source_sha': 'a' * 40,
        'evaluated_source_tree_sha': 'b' * 40,
        'evaluated_release_manifest_sha256': 'c' * 64,
        'release_artifact_integrity': [
            {'platform': 'android', 'status': 'PASS', 'actual_sha256': 'd' * 64, 'actual_bytes': 11},
            {'platform': 'ios', 'status': 'PASS', 'actual_sha256': 'e' * 64, 'actual_bytes': 22},
        ],
        'release_status': 'NO-GO',
    }


def _attested_file(temp):
    path = Path(temp) / 'closure.json'
    path.write_text(json.dumps(_closure()), encoding='utf-8')
    passed, _, _ = ATTEST.attest_release_closure(path)
    assert passed is True
    return path


def test_valid_attestation_verifies():
    with tempfile.TemporaryDirectory() as temp:
        path = _attested_file(temp)
        passed, reason, evidence = VERIFY.verify_release_closure_provenance(path)
        assert passed is True
        assert reason == 'RELEASE_PROVENANCE_VERIFIED'
        assert evidence['status'] == 'PASS'


def test_modified_bound_closure_fact_is_detected():
    with tempfile.TemporaryDirectory() as temp:
        path = _attested_file(temp)
        closure = json.loads(path.read_text(encoding='utf-8'))
        closure['release_artifact_integrity'][0]['actual_bytes'] = 12
        path.write_text(json.dumps(closure), encoding='utf-8')
        passed, reason, _ = VERIFY.verify_release_closure_provenance(path)
        assert passed is False
        assert reason == 'RELEASE_PROVENANCE_PAYLOAD_MISMATCH'


def test_modified_stored_payload_even_with_old_hash_is_detected():
    with tempfile.TemporaryDirectory() as temp:
        path = _attested_file(temp)
        closure = json.loads(path.read_text(encoding='utf-8'))
        closure['release_provenance']['payload']['artifacts']['android']['bytes'] = 99
        path.write_text(json.dumps(closure), encoding='utf-8')
        passed, reason, _ = VERIFY.verify_release_closure_provenance(path)
        assert passed is False
        assert reason == 'RELEASE_PROVENANCE_PAYLOAD_MISMATCH'


def test_modified_hash_is_detected():
    with tempfile.TemporaryDirectory() as temp:
        path = _attested_file(temp)
        closure = json.loads(path.read_text(encoding='utf-8'))
        closure['release_provenance']['sha256'] = 'f' * 64
        path.write_text(json.dumps(closure), encoding='utf-8')
        passed, reason, _ = VERIFY.verify_release_closure_provenance(path)
        assert passed is False
        assert reason == 'RELEASE_PROVENANCE_SHA256_MISMATCH'


def test_missing_provenance_fails_closed():
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp) / 'closure.json'
        path.write_text(json.dumps(_closure()), encoding='utf-8')
        passed, reason, _ = VERIFY.verify_release_closure_provenance(path)
        assert passed is False
        assert reason == 'RELEASE_PROVENANCE_MISSING'


def test_verifier_is_read_only():
    with tempfile.TemporaryDirectory() as temp:
        path = _attested_file(temp)
        before = path.read_bytes()
        passed, _, _ = VERIFY.verify_release_closure_provenance(path)
        after = path.read_bytes()
        assert passed is True
        assert after == before


def main():
    tests = [
        test_valid_attestation_verifies,
        test_modified_bound_closure_fact_is_detected,
        test_modified_stored_payload_even_with_old_hash_is_detected,
        test_modified_hash_is_detected,
        test_missing_provenance_fails_closed,
        test_verifier_is_read_only,
    ]
    for test in tests:
        test()
        print(f'PASS {test.__name__}')
    print(f'PASS {len(tests)}/{len(tests)} release closure provenance verifier contracts')


if __name__ == '__main__':
    main()
