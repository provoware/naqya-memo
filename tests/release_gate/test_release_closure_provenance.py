from pathlib import Path
import importlib.util
import json
import tempfile

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / 'tools/release_gate/attest_release_closure.py'
SPEC = importlib.util.spec_from_file_location('attest_release_closure', MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
build_provenance_payload = MODULE.build_provenance_payload
provenance_sha256 = MODULE.provenance_sha256
attest_release_closure = MODULE.attest_release_closure


def _closure():
    return {
        'evaluated_source_sha': 'a' * 40,
        'evaluated_source_tree_sha': 'b' * 40,
        'evaluated_release_manifest_sha256': 'c' * 64,
        'release_artifact_integrity': [
            {'platform': 'ios', 'status': 'PASS', 'actual_sha256': 'e' * 64, 'actual_bytes': 22},
            {'platform': 'android', 'status': 'PASS', 'actual_sha256': 'd' * 64, 'actual_bytes': 11},
        ],
        'release_status': 'NO-GO',
    }


def test_provenance_is_deterministic_across_artifact_input_order():
    first = _closure()
    second = _closure()
    second['release_artifact_integrity'] = list(reversed(second['release_artifact_integrity']))
    payload_a, reason_a = build_provenance_payload(first)
    payload_b, reason_b = build_provenance_payload(second)
    assert reason_a == reason_b == 'PROVENANCE_PAYLOAD_VALID'
    assert payload_a == payload_b
    assert provenance_sha256(payload_a) == provenance_sha256(payload_b)


def test_provenance_changes_when_bound_artifact_changes():
    first = _closure()
    second = _closure()
    second['release_artifact_integrity'][0]['actual_sha256'] = 'f' * 64
    payload_a, _ = build_provenance_payload(first)
    payload_b, _ = build_provenance_payload(second)
    assert provenance_sha256(payload_a) != provenance_sha256(payload_b)


def test_invalid_source_identity_fails_closed():
    closure = _closure()
    closure['evaluated_source_sha'] = 'not-a-git-sha'
    payload, reason = build_provenance_payload(closure)
    assert payload is None
    assert reason == 'PROVENANCE_SOURCE_SHA_INVALID'


def test_missing_required_artifact_fails_closed():
    closure = _closure()
    closure['release_artifact_integrity'] = closure['release_artifact_integrity'][:1]
    payload, reason = build_provenance_payload(closure)
    assert payload is None
    assert reason == 'PROVENANCE_REQUIRED_ARTIFACT_MISSING'


def test_attestation_is_written_into_closure_evidence():
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp) / 'closure.json'
        path.write_text(json.dumps(_closure()), encoding='utf-8')
        passed, reason, evidence = attest_release_closure(path)
        stored = json.loads(path.read_text(encoding='utf-8'))
        assert passed is True
        assert reason == 'RELEASE_PROVENANCE_BOUND'
        assert evidence['status'] == 'PASS'
        assert len(evidence['sha256']) == 64
        assert stored['release_provenance'] == evidence


def test_failed_artifact_integrity_cannot_receive_pass_provenance():
    closure = _closure()
    closure['release_artifact_integrity'][0]['status'] = 'FAIL'
    payload, reason = build_provenance_payload(closure)
    assert payload is None
    assert reason == 'PROVENANCE_ARTIFACT_INTEGRITY_INVALID'


def main():
    tests = [
        test_provenance_is_deterministic_across_artifact_input_order,
        test_provenance_changes_when_bound_artifact_changes,
        test_invalid_source_identity_fails_closed,
        test_missing_required_artifact_fails_closed,
        test_attestation_is_written_into_closure_evidence,
        test_failed_artifact_integrity_cannot_receive_pass_provenance,
    ]
    for test in tests:
        test()
    print(f'release closure provenance contracts: {len(tests)}/{len(tests)} PASS')


if __name__ == '__main__':
    main()
