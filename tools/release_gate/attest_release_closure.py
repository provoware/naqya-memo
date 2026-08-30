from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
CLOSURE = ROOT / 'registry/evidence/v0.12.2/RELEASE_GATE_CLOSURE.json'
REQUIRED_PLATFORMS = ('android', 'ios')


def _is_hex(value, length):
    return isinstance(value, str) and len(value.strip()) == length and all(
        ch in '0123456789abcdef' for ch in value.strip().lower()
    )


def build_provenance_payload(closure):
    """Build the minimal deterministic identity payload for one release closure."""
    source_sha = closure.get('evaluated_source_sha')
    source_tree_sha = closure.get('evaluated_source_tree_sha')
    manifest_sha256 = closure.get('evaluated_release_manifest_sha256')
    if not _is_hex(source_sha, 40):
        return None, 'PROVENANCE_SOURCE_SHA_INVALID'
    if not _is_hex(source_tree_sha, 40):
        return None, 'PROVENANCE_SOURCE_TREE_SHA_INVALID'
    if not _is_hex(manifest_sha256, 64):
        return None, 'PROVENANCE_MANIFEST_SHA256_INVALID'

    artifact_items = closure.get('release_artifact_integrity')
    if not isinstance(artifact_items, list):
        return None, 'PROVENANCE_ARTIFACT_LIST_INVALID'

    artifacts = {}
    for item in artifact_items:
        if not isinstance(item, dict):
            return None, 'PROVENANCE_ARTIFACT_ITEM_INVALID'
        platform = item.get('platform')
        if platform not in REQUIRED_PLATFORMS or platform in artifacts:
            return None, 'PROVENANCE_ARTIFACT_PLATFORM_INVALID'
        sha256 = item.get('actual_sha256')
        actual_bytes = item.get('actual_bytes')
        if item.get('status') != 'PASS' or not _is_hex(sha256, 64):
            return None, 'PROVENANCE_ARTIFACT_INTEGRITY_INVALID'
        if not isinstance(actual_bytes, int) or isinstance(actual_bytes, bool) or actual_bytes < 0:
            return None, 'PROVENANCE_ARTIFACT_SIZE_INVALID'
        artifacts[platform] = {
            'sha256': sha256.strip().lower(),
            'bytes': actual_bytes,
        }

    if set(artifacts) != set(REQUIRED_PLATFORMS):
        return None, 'PROVENANCE_REQUIRED_ARTIFACT_MISSING'

    payload = {
        'schema': 'provoware.release-provenance.v1',
        'source_sha': source_sha.strip().lower(),
        'source_tree_sha': source_tree_sha.strip().lower(),
        'release_manifest_sha256': manifest_sha256.strip().lower(),
        'artifacts': {platform: artifacts[platform] for platform in REQUIRED_PLATFORMS},
    }
    return payload, 'PROVENANCE_PAYLOAD_VALID'


def provenance_sha256(payload):
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(',', ':'),
    ).encode('utf-8')
    return hashlib.sha256(canonical).hexdigest()


def attest_release_closure(path=CLOSURE):
    path = Path(path)
    try:
        closure = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError, TypeError) as exc:
        return False, 'RELEASE_CLOSURE_MISSING_OR_INVALID', {'error': repr(exc)}

    payload, reason = build_provenance_payload(closure)
    if payload is None:
        closure['release_provenance'] = {
            'status': 'FAIL',
            'reason': reason,
            'schema': 'provoware.release-provenance.v1',
        }
        try:
            path.write_text(json.dumps(closure, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        except OSError as exc:
            return False, 'RELEASE_CLOSURE_PROVENANCE_WRITE_FAILED', {'error': repr(exc)}
        return False, reason, closure['release_provenance']

    digest = provenance_sha256(payload)
    closure['release_provenance'] = {
        'status': 'PASS',
        'reason': 'RELEASE_PROVENANCE_BOUND',
        'schema': payload['schema'],
        'sha256': digest,
        'payload': payload,
    }
    try:
        path.write_text(json.dumps(closure, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    except OSError as exc:
        return False, 'RELEASE_CLOSURE_PROVENANCE_WRITE_FAILED', {'error': repr(exc)}
    return True, 'RELEASE_PROVENANCE_BOUND', closure['release_provenance']


def main():
    passed, reason, evidence = attest_release_closure()
    print(json.dumps({'status': 'PASS' if passed else 'FAIL', 'reason': reason, 'release_provenance': evidence}, indent=2, ensure_ascii=False))
    raise SystemExit(0 if passed else 2)


if __name__ == '__main__':
    main()
