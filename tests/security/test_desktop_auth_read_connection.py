#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import os
import sqlite3
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'app'))


def main() -> None:
    with tempfile.TemporaryDirectory(prefix='provoware-auth-read-connection-') as td:
        project = Path(td) / 'project'
        os.environ['PROVOWARE_PROJECT_PATH'] = str(project)
        os.environ['PYTHONPATH'] = str(ROOT / 'core' / 'reference_python')
        sys.path.insert(0, str(ROOT / 'core' / 'reference_python'))

        import secure_response_server as hardened

        revision = hardened._profile_revision_from_readonly_db()
        assert isinstance(revision, int) and revision >= 1, revision
        print('PASS auth security state is readable from the committed profile database')

        original_conn = hardened.secure.base.store.conn

        class PoisonSharedConnection:
            def execute(self, *args, **kwargs):
                raise AssertionError('shared product SQLite connection was used by auth state read')

        hardened.secure.base.store.conn = PoisonSharedConnection()
        try:
            isolated_revision = hardened._profile_revision_from_readonly_db()
        finally:
            hardened.secure.base.store.conn = original_conn
        assert isolated_revision == revision, (isolated_revision, revision)
        print('PASS auth state read is independent from the shared product SQLite connection')

        con = sqlite3.connect(hardened.secure.DB, timeout=3)
        try:
            with con:
                con.execute(
                    "UPDATE profiles SET status='INACTIVE' WHERE id=?",
                    (hardened.secure.base.PROFILE_ID,),
                )
            assert hardened._profile_revision_from_readonly_db() is None
            print('PASS inactive profile fails closed on the independent auth read path')

            with con:
                con.execute(
                    "UPDATE profiles SET status='ACTIVE' WHERE id=?",
                    (hardened.secure.base.PROFILE_ID,),
                )
            assert hardened._profile_revision_from_readonly_db() == revision
            print('PASS committed profile state becomes visible immediately after reactivation')
        finally:
            con.close()

        original_db = hardened.secure.DB
        hardened.secure.DB = project / 'daten' / 'missing-security-state.sqlite3'
        try:
            assert hardened._profile_revision_from_readonly_db() is None
        finally:
            hardened.secure.DB = original_db
        print('PASS missing/unreadable auth database fails closed instead of trusting cache state')

        print('SUMMARY total=5 passed=5 failed=0')


if __name__ == '__main__':
    main()
