from pathlib import Path
import json, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'app'))

from error_contract import classify_public_error

MESSAGES = {
    'MEMO_TITLE_REQUIRED': 'Bitte einen Titel für das Memo eingeben.',
    'REVISION_CONFLICT': 'Der Inhalt wurde inzwischen geändert. Bitte neu laden.',
    'REQUEST_JSON_INVALID': 'Die Anfrage enthält ungültige JSON-Daten.',
    'MUTATION_DEGRADED_MODE': 'Schreibzugriffe sind nach einem internen Fehler vorsorglich gesperrt.',
}


def main():
    known = classify_public_error(ValueError('MEMO_TITLE_REQUIRED'), MESSAGES)
    assert known.code == 'MEMO_TITLE_REQUIRED' and known.status == 400
    assert known.degraded_mode is False and known.activate_mutation_barrier is False
    assert 'Titel' in known.message and known.recovery_hint

    revision = classify_public_error(RuntimeError('REVISION_CONFLICT'), MESSAGES)
    assert revision.status == 409 and revision.code == 'REVISION_CONFLICT'

    try:
        json.loads('{kaputt')
    except json.JSONDecodeError as exc:
        invalid_json = classify_public_error(exc, MESSAGES)
    assert invalid_json.code == 'REQUEST_JSON_INVALID' and invalid_json.status == 400
    assert 'kaputt' not in json.dumps(invalid_json.payload(), ensure_ascii=False)

    secret = '/home/private/projekt/core.sqlite3: database is locked'
    unknown_write = classify_public_error(RuntimeError(secret), MESSAGES, mutation_context=True)
    payload = unknown_write.payload()
    assert unknown_write.status == 500 and payload['code'] == 'INTERNAL_ERROR'
    assert secret not in json.dumps(payload, ensure_ascii=False)
    assert payload['degraded_mode'] is True and unknown_write.activate_mutation_barrier is True
    assert 'Nicht erneut speichern' in payload['recovery_hint']

    unknown_read = classify_public_error(RuntimeError(secret), MESSAGES)
    assert unknown_read.status == 500 and unknown_read.degraded_mode is False
    assert unknown_read.activate_mutation_barrier is False
    assert secret not in json.dumps(unknown_read.payload(), ensure_ascii=False)

    degraded = classify_public_error(RuntimeError('MUTATION_DEGRADED_MODE'), MESSAGES)
    assert degraded.status == 503 and degraded.degraded_mode is True
    assert degraded.activate_mutation_barrier is False
    assert 'Schreibzugriffe' in degraded.recovery_hint

    server = (ROOT / 'app' / 'server.py').read_text(encoding='utf-8')
    assert 'from error_contract import classify_public_error' in server
    assert 'MUTATION_DEGRADED = threading.Event()' in server
    assert 'if MUTATION_DEGRADED.is_set():' in server
    assert "ValueError('MUTATION_DEGRADED_MODE')" in server
    assert 'public = classify_public_error(e, ERROR_TEXT, status, mutation_context=mutation_context)' in server
    assert 'if public.activate_mutation_barrier:' in server
    assert 'MUTATION_DEGRADED.set()' in server
    assert 'return self._fail(e, mutation_context=True)' in server
    assert "'mutation_mode':'DEGRADED' if MUTATION_DEGRADED.is_set() else 'READY'" in server

    print('PASS ERROR-UX-001 safe mutation error boundary')


if __name__ == '__main__':
    main()
