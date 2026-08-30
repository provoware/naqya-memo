from pathlib import Path
import datetime
import json
import os
import subprocess

ROOT = Path(__file__).resolve().parents[2]
GD = ROOT / 'registry/evidence/v0.12.2/gates'
OUT = ROOT / 'registry/evidence/v0.12.2/RELEASE_GATE_CLOSURE.json'
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
    if not isinstance(expected_sha, str) or len(expected_sha.strip()) != 40:
        return False, 'SOURCE_IDENTITY_CONTEXT_MISSING_OR_INVALID'
    if not isinstance(current_sha, str) or len(current_sha.strip()) != 40:
        return False, 'CURRENT_SOURCE_IDENTITY_UNAVAILABLE'
    if expected_sha.strip().lower() != current_sha.strip().lower():
        return False, 'SOURCE_IDENTITY_CHANGED_DURING_GATE_RUN'
    return True, 'SOURCE_IDENTITY_MATCH'


def _current_source_sha():
    try:
        result = subprocess.run(
            ['git', '-C', str(ROOT), 'rev-parse', '--verify', 'HEAD'],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    value = result.stdout.strip()
    return value if len(value) == 40 else None


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


def evaluate_release_gate(run_started_at=None, expected_source_sha=None, current_source_sha=None):
    if run_started_at is None:
        run_started_at = os.environ.get(FRESHNESS_ENV)
    if expected_source_sha is None:
        expected_source_sha = os.environ.get(SOURCE_SHA_ENV)
    if current_source_sha is None:
        current_source_sha = _current_source_sha()

    items = []
    for no, name in GATES:
        matches = sorted(GD.glob(f'GATE_{no}_*.json'))
        fallback_gate = f'GATE_{no}_{name}'
        if not matches:
            items.append({'gate': fallback_gate, 'status': 'NOT_RUN'})
            continue
        items.append(_load_gate(matches[-1], fallback_gate, run_started_at))

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
    release_allowed = bool(all_pass and source_pass and identity_pass)

    out = {
        'version': '0.12.2-MOBILE-RUNTIME-COMPLETION',
        'generated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'feature_freeze': True,
        'freeze_exception': 'platform parity completion only',
        'evidence_freshness_required': True,
        'freshness_context_status': 'PASS' if freshness_context_valid else 'FAIL',
        'gate_run_started_at': run_started_at,
        'source_identity_required': True,
        'source_identity_status': 'PASS' if identity_pass else 'FAIL',
        'source_identity_reason': identity_reason,
        'gate_run_source_sha': expected_source_sha,
        'evaluated_source_sha': current_source_sha,
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
