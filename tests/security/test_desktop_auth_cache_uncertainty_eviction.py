#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import os
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'app'))
sys.path.insert(0, str(ROOT / 'core' / 'reference_python'))


def main() -> None:
    with tempfile.TemporaryDirectory(prefix='provoware-auth-cache-uncertainty-') as td:
        os.environ['PROVOWARE_PROJECT_PATH'] = str(Path(td) / 'project')

        import secure_response_server as hardened

        secure = hardened.secure
        first = 'Basic first-credential'
        second = 'Basic second-credential'
        epoch = hardened._profile_cache_epoch_from_readonly_db()
        assert isinstance(epoch, int) and epoch > 0, epoch

        original_revision = secure._profile_revision
        try:
            secure._profile_revision = lambda: epoch
            secure._remember(first, epoch)
            secure._remember(second, epoch)
            assert secure._cached(first) is True
            assert secure._cached(second) is True
            print('PASS multiple credentials may be cached while security state is proven')

            first_key = secure._authorization_digest(first)
            second_key = secure._authorization_digest(second)
            assert first_key in secure._AUTH_CACHE and second_key in secure._AUTH_CACHE
            print('PASS baseline cache contains both credential digests')

            secure._profile_revision = lambda: None
            assert secure._cached(first) is False
            print('PASS unknown security state fails closed for the triggering credential')

            assert secure._AUTH_CACHE == {}, secure._AUTH_CACHE
            print('PASS security-state uncertainty evicts the complete auth cache')

            secure._profile_revision = lambda: epoch
            assert secure._cached(first) is False
            assert secure._cached(second) is False
            print('PASS cached credentials do not resurrect when the same security epoch returns')

            secure._remember(first, epoch)
            assert secure._cached(first) is True
            print('PASS credential can be cached again only after an explicit new remember step')

            print('SUMMARY total=6 passed=6 failed=0')
        finally:
            secure._profile_revision = original_revision
            secure._AUTH_CACHE.clear()


if __name__ == '__main__':
    main()
