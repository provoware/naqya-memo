from pathlib import Path
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[2]
CLOSURE = ROOT / 'registry/evidence/v0.12.2/RELEASE_GATE_CLOSURE.json'
ATTESTER_PATH = ROOT / 'tools/release_gate/attest_release_closure.py'

_SPEC = importlib.util.spec_from_file_location('attest_release_closure', ATTESTER_PATH)
_ATTESTER = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_ATTESTER)
build_provenance_payload = _ATTESTER.build_provenance_payload
provenance_sha256 = _ATTESTER.provenance_sha256


def verify_release_closure_provenance(path=CLOSURE):
    """Read-only verification of the persisted release provenance against closure facts."""
    path = Path(path)
    try:
        closure = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError, TypeError) as exc:
        return False, 'RELEASE_CLOSURE_MISSING_OR_INVALID', {'error': repr(exc)}

    stored = closure.get('release_provenance')
    if not isinstance(stored, dict):
        return False, 'RELEASE_PROVENANCE_MISSING', {}
    if stored.get('status') != 'PASS':
        return False, 'RELEASE_PROVENANCE_NOT_PASS', stored
    if stored.get('schema') != 'provoware.release-provenance.v1':
        return False, 'RELEASE_PROVENANCE_SCHEMA_INVALID', stored

    expected_payload, reason = build_provenance_payload(closure)
    if expected_payload is None:
        return False, reason, stored

    stored_payload = stored.get('payload')
    if stored_payload != expected_payload:
        return False, 'RELEASE_PROVENANCE_PAYLOAD_MISMATCH', stored

    expected_sha256 = provenance_sha256(expected_payload)
    stored_sha256 = stored.get('sha256')
    if stored_sha256 != expected_sha256:
        return False, 'RELEASE_PROVENANCE_SHA256_MISMATCH', stored

    return True, 'RELEASE_PROVENANCE_VERIFIED', {
        'status': 'PASS',
        'schema': stored['schema'],
        'sha256': expected_sha256,
    }


def main():
    passed, reason, evidence = verify_release_closure_provenance()
    print(json.dumps({
        'status': 'PASS' if passed else 'FAIL',
        'reason': reason,
        'verification': evidence,
    }, indent=2, ensure_ascii=False))
    raise SystemExit(0 if passed else 2)


if __name__ == '__main__':
    main()
