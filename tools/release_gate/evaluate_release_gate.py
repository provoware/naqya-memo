from pathlib import Path
import datetime
import json
import os

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


def evaluate_release_gate(run_started_at=None):
    if run_started_at is None:
        run_started_at = os.environ.get(FRESHNESS_ENV)

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

    out = {
        'version': '0.12.2-MOBILE-RUNTIME-COMPLETION',
        'generated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'feature_freeze': True,
        'freeze_exception': 'platform parity completion only',
        'evidence_freshness_required': True,
        'freshness_context_status': 'PASS' if freshness_context_valid else 'FAIL',
        'gate_run_started_at': run_started_at,
        'mobile_runtime_source_status': mobile_source.get('status'),
        'required_real_gates': len(GATES),
        'passed_real_gates': pass_count,
        'all_required_real_gates_pass': all_pass,
        'release_status': 'GO' if all_pass and source_pass else 'NO-GO',
        'v1_rc_allowed': bool(all_pass and source_pass),
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
