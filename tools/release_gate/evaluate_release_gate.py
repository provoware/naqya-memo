from pathlib import Path
import datetime
import hashlib
import json
import os
import subprocess

ROOT = Path(__file__).resolve().parents[2]
GD = ROOT / 'registry/evidence/v0.12.2/gates'
OUT = ROOT / 'registry/evidence/v0.12.2/RELEASE_GATE_CLOSURE.json'
ARTIFACT_MANIFEST = ROOT / 'docs/release/MOBILE_RUNTIME_RELEASE_MANIFEST.json'
ARTIFACT_ROOT = ROOT / 'dist/v0.12.2'
REQUIRED_SOURCE_ARTIFACTS = ('android', 'ios')
GATES = [
    ('01', '8H_SOAK'),
    ('02', 'CHROMIUM'),
    ('03', 'FIREFOX'),
    ('04', 'LINUX_MICROPHONE'),
    ('05', 'STORAGE_FAILURE'),
    ('06', 'ANDROID_DEVICE'),
    ('07', 'IOS_IPHONE_X'),
]
FRESHNESS_ENV = 'PROVOWARE_RELEASE_GATE_STARTED_AT'
SOURCE_SHA_ENV = 'PROVOWARE_RELEASE_GATE_SOURCE_SHA'
SOURCE_TREE_SHA_ENV = 'PROVOWARE_RELEASE_GATE_SOURCE_TREE_SHA'
MANIFEST_SHA256_ENV = 'PROVOWARE_RELEASE_GATE_MANIFEST_SHA256'


def _parse_utc(value):
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(datetime.timezone.utc)


def _is_git_object_id(value):
    if not isinstance(value, str):
        return False
    value = value.strip().lower()
    return len(value) == 40 and all(ch in '0123456789abcdef' for ch in value)


def _is_sha256(value):
    if not isinstance(value, str):
        return False
    value = value.strip().lower()
    return len(value) == 64 and all(ch in '0123456789abcdef' for ch in value)


def _sha256_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _current_release_manifest_sha256(manifest_path=ARTIFACT_MANIFEST):
    path = Path(manifest_path)
    if path.is_symlink() or not path.is_file():
        return None
    try:
        return _sha256_file(path)
    except OSError:
        return None


def release_manifest_identity(expected_sha256, current_sha256):
    """Fail closed unless the exact release manifest stays unchanged for the gate run."""
    if not _is_sha256(expected_sha256):
        return False, 'RELEASE_MANIFEST_IDENTITY_CONTEXT_MISSING_OR_INVALID'
    if not _is_sha256(current_sha256):
        return False, 'CURRENT_RELEASE_MANIFEST_IDENTITY_UNAVAILABLE'
    if expected_sha256.strip().lower() != current_sha256.strip().lower():
        return False, 'RELEASE_MANIFEST_CHANGED_DURING_GATE_RUN'
    return True, 'RELEASE_MANIFEST_IDENTITY_MATCH'


def release_artifact_integrity(manifest_path=ARTIFACT_MANIFEST, artifact_root=ARTIFACT_ROOT):
    """Verify the exact mobile source artifacts declared by the release manifest.

    This is deliberately manifest-driven: the release gate does not invent new
    package names and cannot turn unavailable APK/IPA builds into release evidence.
    Existing source ZIPs must be regular, local files whose byte length and SHA-256
    exactly match the committed release manifest before GO can be considered.
    """
    try:
        manifest = json.loads(Path(manifest_path).read_text(encoding='utf-8'))
    except (OSError, ValueError, TypeError) as exc:
        return False, 'RELEASE_ARTIFACT_MANIFEST_MISSING_OR_INVALID', [{'error': repr(exc)}]

    root = Path(artifact_root)
    items = []
    for platform in REQUIRED_SOURCE_ARTIFACTS:
        entry = manifest.get(platform)
        if not isinstance(entry, dict):
            return False, 'RELEASE_ARTIFACT_METADATA_MISSING_OR_INVALID', items + [{'platform': platform}]

        artifact_name = entry.get('source_artifact')
        declared_sha256 = entry.get('sha256')
        declared_bytes = entry.get('bytes')
        if (
            not isinstance(artifact_name, str)
            or not artifact_name
            or artifact_name in {'.', '..'}
            or '/' in artifact_name
            or '\\' in artifact_name
            or Path(artifact_name).name != artifact_name
        ):
            return False, 'RELEASE_ARTIFACT_PATH_UNSAFE', items + [{'platform': platform, 'artifact': artifact_name}]
        if not _is_sha256(declared_sha256) or not isinstance(declared_bytes, int) or isinstance(declared_bytes, bool) or declared_bytes < 0:
            return False, 'RELEASE_ARTIFACT_METADATA_MISSING_OR_INVALID', items + [{'platform': platform, 'artifact': artifact_name}]

        artifact = root / artifact_name
        if artifact.is_symlink() or not artifact.is_file():
            return False, 'RELEASE_ARTIFACT_MISSING_OR_UNSAFE', items + [{'platform': platform, 'artifact': artifact_name}]

        try:
            actual_bytes = artifact.stat().st_size
            actual_sha256 = _sha256_file(artifact)
        except OSError as exc:
            return False, 'RELEASE_ARTIFACT_UNREADABLE', items + [{'platform': platform, 'artifact': artifact_name, 'error': repr(exc)}]

        item = {
            'platform': platform,
            'artifact': str(artifact.relative_to(ROOT)) if artifact.is_relative_to(ROOT) else artifact_name,
            'declared_bytes': declared_bytes,
            'actual_bytes': actual_bytes,
            'declared_sha256': declared_sha256.lower(),
            'actual_sha256': actual_sha256,
        }
        if actual_bytes != declared_bytes:
            item['status'] = 'FAIL'
            items.append(item)
            return False, 'RELEASE_ARTIFACT_SIZE_MISMATCH', items
        if actual_sha256 != declared_sha256.lower():
            item['status'] = 'FAIL'
            items.append(item)
            return False, 'RELEASE_ARTIFACT_SHA256_MISMATCH', items
        item['status'] = 'PASS'
        items.append(item)

    return True, 'RELEASE_ARTIFACT_INTEGRITY_MATCH', items


def evidence_freshness(evidence, run_started_at):
    """Return (is_fresh, reason) for one real release-gate evidence object."""
    started = _parse_utc(run_started_at)
    if started is None:
        return False, 'FRESHNESS_CONTEXT_MISSING_OR_INVALID'
    evidence_time = _parse_utc(evidence.get('timestamp') or evidence.get('timestamp_utc'))
    if evidence_time is None:
        return False, 'EVIDENCE_TIMESTAMP_MISSING_OR_INVALID'
    if evidence_time < started:
        return False, 'EVIDENCE_PREDATES_CURRENT_GATE_RUN'
    return True, 'CURRENT_GATE_RUN'


def source_identity(expected_sha, current_sha):
    """Fail closed unless closure start and evaluation use the exact same Git commit."""
    if not _is_git_object_id(expected_sha):
        return False, 'SOURCE_IDENTITY_CONTEXT_MISSING_OR_INVALID'
    if not _is_git_object_id(current_sha):
        return False, 'CURRENT_SOURCE_IDENTITY_UNAVAILABLE'
    if expected_sha.strip().lower() != current_sha.strip().lower():
        return False, 'SOURCE_IDENTITY_CHANGED_DURING_GATE_RUN'
    return True, 'SOURCE_IDENTITY_MATCH'


def source_tree_identity(expected_tree_sha, current_tree_sha):
    """Fail closed unless closure start and evaluation use the exact same Git tree object."""
    if not _is_git_object_id(expected_tree_sha):
        return False, 'SOURCE_TREE_IDENTITY_CONTEXT_MISSING_OR_INVALID'
    if not _is_git_object_id(current_tree_sha):
        return False, 'CURRENT_SOURCE_TREE_IDENTITY_UNAVAILABLE'
    if expected_tree_sha.strip().lower() != current_tree_sha.strip().lower():
        return False, 'SOURCE_TREE_IDENTITY_CHANGED_DURING_GATE_RUN'
    return True, 'SOURCE_TREE_IDENTITY_MATCH'


def select_gate_evidence(directory, no, name):
    """Bind one release gate to exactly one canonical evidence filename.

    A similarly numbered file must never substitute for or shadow the canonical
    gate evidence. Extra same-number JSON files are treated as ambiguity and fail
    closed so operators cannot accidentally qualify the wrong artifact.
    """
    canonical = directory / f'GATE_{no}_{name}.json'
    if not canonical.is_file():
        return None, 'CANONICAL_GATE_EVIDENCE_MISSING'
    extras = sorted(
        path for path in directory.glob(f'GATE_{no}_*.json')
        if path != canonical
    )
    if extras:
        return None, 'AMBIGUOUS_GATE_EVIDENCE_FILES'
    return canonical, 'CANONICAL_GATE_EVIDENCE_BOUND'


def _git_rev_parse(expression):
    try:
        result = subprocess.run(
            ['git', '-C', str(ROOT), 'rev-parse', '--verify', expression],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    value = result.stdout.strip()
    return value if _is_git_object_id(value) else None


def _current_source_sha():
    return _git_rev_parse('HEAD')


def _current_source_tree_sha():
    return _git_rev_parse('HEAD^{tree}')


def _load_gate(path, fallback_gate, run_started_at):
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:
        return {'gate': fallback_gate, 'status': 'INVALID_EVIDENCE', 'error': repr(exc)}

    fresh, reason = evidence_freshness(data, run_started_at)
    data['freshness'] = {'status': 'PASS' if fresh else 'FAIL', 'reason': reason}
    if not fresh:
        reported_status = data.get('status')
        data['reported_status'] = reported_status
        data['status'] = 'STALE_EVIDENCE'
    return data


def evaluate_release_gate(
    run_started_at=None,
    expected_source_sha=None,
    current_source_sha=None,
    expected_source_tree_sha=None,
    current_source_tree_sha=None,
    expected_manifest_sha256=None,
    current_manifest_sha256=None,
):
    if run_started_at is None:
        run_started_at = os.environ.get(FRESHNESS_ENV)
    if expected_source_sha is None:
        expected_source_sha = os.environ.get(SOURCE_SHA_ENV)
    if current_source_sha is None:
        current_source_sha = _current_source_sha()
    if expected_source_tree_sha is None:
        expected_source_tree_sha = os.environ.get(SOURCE_TREE_SHA_ENV)
    if current_source_tree_sha is None:
        current_source_tree_sha = _current_source_tree_sha()
    if expected_manifest_sha256 is None:
        expected_manifest_sha256 = os.environ.get(MANIFEST_SHA256_ENV)
    if current_manifest_sha256 is None:
        current_manifest_sha256 = _current_release_manifest_sha256()

    items = []
    for no, name in GATES:
        fallback_gate = f'GATE_{no}_{name}'
        path, binding_reason = select_gate_evidence(GD, no, name)
        if path is None:
            items.append({
                'gate': fallback_gate,
                'status': 'INVALID_EVIDENCE_BINDING',
                'evidence_binding': {'status': 'FAIL', 'reason': binding_reason},
            })
            continue
        item = _load_gate(path, fallback_gate, run_started_at)
        item['evidence_binding'] = {
            'status': 'PASS',
            'reason': binding_reason,
            'path': str(path.relative_to(ROOT)),
        }
        items.append(item)

    pass_count = sum(item.get('status') == 'PASS' for item in items)
    all_pass = pass_count == len(GATES)

    source_evidence = ROOT / 'registry/evidence/v0.12.2/MOBILE_RUNTIME_SOURCE_ACCEPTANCE.json'
    mobile_source = (
        json.loads(source_evidence.read_text(encoding='utf-8'))
        if source_evidence.exists()
        else {'status': 'NOT_RUN'}
    )
    source_pass = mobile_source.get('status') == 'PASS'
    freshness_context_valid = _parse_utc(run_started_at) is not None
    identity_pass, identity_reason = source_identity(expected_source_sha, current_source_sha)
    tree_identity_pass, tree_identity_reason = source_tree_identity(
        expected_source_tree_sha,
        current_source_tree_sha,
    )
    manifest_identity_pass, manifest_identity_reason = release_manifest_identity(
        expected_manifest_sha256,
        current_manifest_sha256,
    )
    artifact_integrity_pass, artifact_integrity_reason, artifact_integrity_items = release_artifact_integrity()
    release_allowed = bool(
        all_pass
        and source_pass
        and identity_pass
        and tree_identity_pass
        and manifest_identity_pass
        and artifact_integrity_pass
    )

    out = {
        'version': '0.12.2-MOBILE-RUNTIME-COMPLETION',
        'generated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'feature_freeze': True,
        'freeze_exception': 'platform parity completion only',
        'canonical_gate_evidence_required': True,
        'evidence_freshness_required': True,
        'freshness_context_status': 'PASS' if freshness_context_valid else 'FAIL',
        'gate_run_started_at': run_started_at,
        'source_identity_required': True,
        'source_identity_status': 'PASS' if identity_pass else 'FAIL',
        'source_identity_reason': identity_reason,
        'gate_run_source_sha': expected_source_sha,
        'evaluated_source_sha': current_source_sha,
        'source_tree_identity_required': True,
        'source_tree_identity_status': 'PASS' if tree_identity_pass else 'FAIL',
        'source_tree_identity_reason': tree_identity_reason,
        'gate_run_source_tree_sha': expected_source_tree_sha,
        'evaluated_source_tree_sha': current_source_tree_sha,
        'release_manifest_identity_required': True,
        'release_manifest_identity_status': 'PASS' if manifest_identity_pass else 'FAIL',
        'release_manifest_identity_reason': manifest_identity_reason,
        'gate_run_release_manifest_sha256': expected_manifest_sha256,
        'evaluated_release_manifest_sha256': current_manifest_sha256,
        'release_artifact_integrity_required': True,
        'release_artifact_integrity_status': 'PASS' if artifact_integrity_pass else 'FAIL',
        'release_artifact_integrity_reason': artifact_integrity_reason,
        'release_artifact_integrity': artifact_integrity_items,
        'mobile_runtime_source_status': mobile_source.get('status'),
        'required_real_gates': len(GATES),
        'passed_real_gates': pass_count,
        'all_required_real_gates_pass': all_pass,
        'release_status': 'GO' if release_allowed else 'NO-GO',
        'v1_rc_allowed': release_allowed,
        'gates': items,
    }
    return out


def main():
    out = evaluate_release_gate()
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(out, indent=2, ensure_ascii=False))
    raise SystemExit(0 if out['v1_rc_allowed'] else 2)


if __name__ == '__main__':
    main()
