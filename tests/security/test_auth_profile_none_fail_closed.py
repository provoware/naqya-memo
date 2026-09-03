#!/usr/bin/env python3
from __future__ import annotations

import base64
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]


def _load_secure_server():
    td = tempfile.TemporaryDirectory(prefix='provoware-auth-none-')
    project = Path(td.name) / 'project'
    os.environ['PROVOWARE_PROJECT_PATH'] = str(project)
    sys.path.insert(0, str(ROOT / 'core' / 'reference_python'))
    sys.path.insert(0, str(ROOT / 'app'))
    import secure_server as secure
    return td, secure


_TEMP, secure = _load_secure_server()


class _ForbiddenStore:
    @property
    def conn(self):
        raise AssertionError('profile database must not be touched without an auth profile')


class _ForbiddenProfileService:
    def verify_access(self, *args, **kwargs):
        raise AssertionError('PIN verification must not run without an auth profile')

    def change_pin(self, *args, **kwargs):
        raise AssertionError('PIN mutation must not run without an auth profile')


class _DummyRequest:
    def __init__(self, header: str):
        self.headers = {'Authorization': header}
        self.client_address = ('127.0.0.1', 12345)
        self._auth_operational_error = None


def _auth_header(pin: str = '1234') -> str:
    token = base64.b64encode(f'provoware:{pin}'.encode('utf-8')).decode('ascii')
    return f'Basic {token}'


def test_auth_profile_resolver_rejects_missing_blank_and_invalid_values() -> None:
    original = secure.base.PROFILE_ID
    try:
        for value in (None, '', '   ', 1234):
            secure.base.PROFILE_ID = value
            assert secure._auth_profile_id() is None, value
    finally:
        secure.base.PROFILE_ID = original


def test_profile_revision_does_not_touch_database_without_profile() -> None:
    original_id = secure.base.PROFILE_ID
    original_store = secure.base.store
    try:
        secure.base.PROFILE_ID = None
        secure.base.store = _ForbiddenStore()
        assert secure._profile_revision() is None
    finally:
        secure.base.store = original_store
        secure.base.PROFILE_ID = original_id


def test_cached_authorization_is_evicted_without_profile() -> None:
    original_id = secure.base.PROFILE_ID
    try:
        secure.base.PROFILE_ID = None
        secure._AUTH_CACHE.clear()
        secure._AUTH_CACHE['synthetic'] = (10**12, 1)
        assert secure._cached(_auth_header()) is False
        assert secure._AUTH_CACHE == {}
    finally:
        secure._AUTH_CACHE.clear()
        secure.base.PROFILE_ID = original_id


def test_request_auth_never_verifies_pin_without_profile() -> None:
    original_id = secure.base.PROFILE_ID
    original_service = secure.base.profile_service
    try:
        secure.base.PROFILE_ID = None
        secure.base.profile_service = _ForbiddenProfileService()
        secure._AUTH_CACHE.clear()
        secure._AUTH_FAILURES.clear()
        secure._AUTH_LOCKED_UNTIL.clear()
        request = _DummyRequest(_auth_header())
        assert secure.SecureHandler._authorized(request) == (False, 0)
        assert request._auth_operational_error is None
    finally:
        secure._AUTH_CACHE.clear()
        secure._AUTH_FAILURES.clear()
        secure._AUTH_LOCKED_UNTIL.clear()
        secure.base.profile_service = original_service
        secure.base.PROFILE_ID = original_id


def test_first_profile_hardening_stops_before_profile_access_without_profile() -> None:
    original_id = secure.base.PROFILE_ID
    original_service = secure.base.profile_service
    try:
        secure.base.PROFILE_ID = None
        secure.base.profile_service = _ForbiddenProfileService()
        try:
            secure._harden_first_profile_if_needed()
            raise AssertionError('expected AUTH_PROFILE_ID_UNAVAILABLE')
        except RuntimeError as exc:
            assert str(exc) == 'AUTH_PROFILE_ID_UNAVAILABLE', exc
    finally:
        secure.base.profile_service = original_service
        secure.base.PROFILE_ID = original_id


def main() -> None:
    tests = [
        test_auth_profile_resolver_rejects_missing_blank_and_invalid_values,
        test_profile_revision_does_not_touch_database_without_profile,
        test_cached_authorization_is_evicted_without_profile,
        test_request_auth_never_verifies_pin_without_profile,
        test_first_profile_hardening_stops_before_profile_access_without_profile,
    ]
    failed = []
    try:
        for test in tests:
            try:
                test()
                print('PASS', test.__name__)
            except Exception as exc:
                failed.append((test.__name__, repr(exc)))
                print('FAIL', test.__name__, repr(exc))
        print(f'SUMMARY total={len(tests)} passed={len(tests)-len(failed)} failed={len(failed)}')
        if failed:
            raise SystemExit(1)
    finally:
        _TEMP.cleanup()


if __name__ == '__main__':
    main()
