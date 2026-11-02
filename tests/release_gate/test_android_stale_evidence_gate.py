"""Android device gate must invalidate stale PASS before any ADB interaction."""
import contextlib
import io
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[2] / 'tools/release_gate/gate_06_android_device.py'


class AndroidEvidenceInvalidationTests(unittest.TestCase):
    def exercise(self, failure):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = root / 'tools/release_gate/gate_06_android_device.py'
            script.parent.mkdir(parents=True)
            shutil.copyfile(SOURCE, script)
            evidence = root / 'registry/evidence/v0.12.2/gates/GATE_06_ANDROID_DEVICE.json'
            evidence.parent.mkdir(parents=True)
            evidence.write_text('{"gate":"GATE_06_ANDROID_DEVICE","status":"PASS","stale":true}', encoding='utf-8')

            acceptance_apk = root / 'acceptance.apk'
            release_apk = root / 'release.apk'
            acceptance_apk.touch()
            release_apk.touch()

            def fake_adb(args, **kwargs):
                if failure == 'interrupt':
                    raise KeyboardInterrupt('simulated interrupted device listing')
                if failure == 'timeout':
                    raise subprocess.TimeoutExpired(args, 8)
                return subprocess.CompletedProcess(args, 1, '', 'ADB device listing failed')

            with patch.dict(os.environ, {'PROVOWARE_ANDROID_ACCEPTANCE_APK': str(acceptance_apk), 'PROVOWARE_ANDROID_RELEASE_APK': str(release_apk)}), \
                 patch('shutil.which', return_value='/usr/bin/adb'), \
                 patch('subprocess.run', side_effect=fake_adb), \
                 contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises((KeyboardInterrupt, SystemExit)) as caught:
                    runpy.run_path(str(script), run_name='__main__')
            data = json.loads(evidence.read_text(encoding='utf-8'))
            self.assertEqual(data['gate'], 'GATE_06_ANDROID_DEVICE')
            self.assertEqual(data['status'], 'BLOCKED')
            self.assertNotIn('stale', data)
            if failure == 'interrupt':
                self.assertIsInstance(caught.exception, KeyboardInterrupt)
            else:
                self.assertIsInstance(caught.exception, SystemExit)
                self.assertEqual(caught.exception.code, 2)
                self.assertIn('device listing failed', data['reason'])

    def test_interrupted_adb_listing_invalidates_old_pass(self):
        self.exercise('interrupt')

    def test_adb_timeout_is_blocked_and_invalidates_old_pass(self):
        self.exercise('timeout')

    def test_adb_error_exit_is_blocked_and_invalidates_old_pass(self):
        self.exercise('nonzero')



class AndroidResetPreconditionTests(unittest.TestCase):
    """A failed isolation step must not turn old app data or logs into a real PASS."""

    def exercise(self, failed_step):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = root / 'tools/release_gate/gate_06_android_device.py'
            script.parent.mkdir(parents=True)
            shutil.copyfile(SOURCE, script)
            acceptance_apk = root / 'acceptance.apk'
            release_apk = root / 'release.apk'
            acceptance_apk.touch()
            release_apk.touch()
            calls = []
            cleared_logs = 0
            read_logs = 0
            package_queries = 0

            def fake_adb(args, **kwargs):
                nonlocal cleared_logs, read_logs, package_queries
                calls.append(args)
                if args == ['/usr/bin/adb', 'devices']:
                    return subprocess.CompletedProcess(args, 0, 'List of devices attached\nserial-1\tdevice\n', '')
                command = args[3:]
                if command == ['shell', 'getprop', 'ro.product.model'] and failed_step == 'getprop_oserror':
                    raise OSError('simulated disconnected device')
                if command[:1] == ['install'] and failed_step == 'install_timeout':
                    raise subprocess.TimeoutExpired(args, kwargs.get('timeout', 30))
                if command == ['shell', 'getprop', 'ro.product.model']:
                    return subprocess.CompletedProcess(args, 0, 'Pixel 8\n', '')
                if command == ['shell', 'getprop', 'ro.build.version.sdk']:
                    if failed_step == 'sdk_non_numeric':
                        return subprocess.CompletedProcess(args, 0, 'unknown\n', '')
                    if failed_step == 'sdk_empty':
                        return subprocess.CompletedProcess(args, 0, '\n', '')
                    if failed_step == 'sdk_command_error':
                        return subprocess.CompletedProcess(args, 1, '34\n', 'Device error')
                    return subprocess.CompletedProcess(args, 0, '34\n', '')
                if command[:1] == ['install'] and failed_step in ('acceptance_install_false_success', 'release_install_false_success'):
                    target = 'release.apk' if failed_step.startswith('release_') else 'acceptance.apk'
                    if command[-1].endswith(target):
                        # Some wrappers report exit 0 while ADB output says installation failed.
                        return subprocess.CompletedProcess(args, 0, 'Performing Streamed Install\nFailure [INSTALL_FAILED_TEST]\n', '')
                if command[:1] == ['uninstall'] and failed_step.startswith('uninstall_'):
                    return subprocess.CompletedProcess(
                        args, 1 if failed_step == 'uninstall_nonzero' else 0,
                        'Failure [DELETE_FAILED_INTERNAL_ERROR]\n', ''
                    )
                if command[:3] == ['shell', 'pm', 'clear']:
                    if failed_step == 'app_data':
                        return subprocess.CompletedProcess(args, 1, 'Failed\n', '')
                    return subprocess.CompletedProcess(args, 0, 'Success\n', '')
                if command[:3] == ['shell', 'am', 'force-stop'] and failed_step == 'force_stop':
                    return subprocess.CompletedProcess(args, 1, '', 'Device disconnected')
                if command == ['logcat', '-c']:
                    cleared_logs += 1
                    if failed_step == 'verify_logs_timeout' and cleared_logs == 2:
                        raise subprocess.TimeoutExpired(args, kwargs.get('timeout', 30))
                    if (failed_step == 'run_logs' and cleared_logs == 1) or (
                        failed_step == 'verify_logs' and cleared_logs == 2
                    ):
                        return subprocess.CompletedProcess(args, 1, '', 'Log clear failed')
                if command[:3] == ['shell', 'dumpsys', 'package']:
                    package_queries += 1
                    if failed_step == 'acceptance_dumpsys_error' and package_queries == 1:
                        # ADB may emit a plausible version despite failing the query.
                        return subprocess.CompletedProcess(args, 1, 'versionName=0.12.2\n', 'device disconnected')
                    if failed_step == 'release_dumpsys_error' and package_queries == 2:
                        # A failed ADB query may still print plausible version data.
                        return subprocess.CompletedProcess(args, 1, 'versionName=0.12.2\n', 'device disconnected')
                    return subprocess.CompletedProcess(args, 0, 'versionName=0.12.2\n', '')
                if command[:2] == ['logcat', '-d']:
                    read_logs += 1
                    mode = 'run' if read_logs == 1 else 'verify'
                    logs = 'I/ProvowareAcceptance: {"mode":"' + mode + '","status":"PASS"}\nREMINDER_FIRED:1\n'
                    if failed_step == mode + '_read_error':
                        return subprocess.CompletedProcess(args, 1, logs, 'logcat read failed')
                    return subprocess.CompletedProcess(args, 0, logs, '')
                if command[:2] == ['shell', 'pidof']:
                    if failed_step == 'release_pidof_error':
                        return subprocess.CompletedProcess(args, 1, '1234\n', 'device disconnected')
                    return subprocess.CompletedProcess(args, 0, '1234\n', '')
                return subprocess.CompletedProcess(args, 0, 'Success\n', '')

            with patch.dict(os.environ, {
                'PROVOWARE_ANDROID_ACCEPTANCE_APK': str(acceptance_apk),
                'PROVOWARE_ANDROID_RELEASE_APK': str(release_apk),
            }), patch('shutil.which', return_value='/usr/bin/adb'), \
                 patch('subprocess.run', side_effect=fake_adb), \
                 patch('time.sleep', return_value=None), \
                 contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(SystemExit) as caught:
                    runpy.run_path(str(script), run_name='__main__')

            evidence = root / 'registry/evidence/v0.12.2/gates/GATE_06_ANDROID_DEVICE.json'
            data = json.loads(evidence.read_text(encoding='utf-8'))
            self.assertEqual(caught.exception.code, 2)
            self.assertEqual(data['status'], 'BLOCKED')
            self.assertNotIn('release_pid', data)
            if failed_step.endswith('_timeout'):
                self.assertEqual(data['failure_class'], 'TIMEOUT')
            if failed_step.endswith('_oserror'):
                self.assertEqual(data['failure_class'], 'COMMAND_ERROR')
            if failed_step == 'acceptance_dumpsys_error':
                self.assertEqual(data['failure_class'], 'ACCEPTANCE_METADATA_QUERY_FAILED')
                self.assertEqual(data['failed_step'], 'shell dumpsys package')
                self.assertFalse(any(call[3:5] == ['logcat', '-c'] for call in calls))
            if failed_step.startswith('release_'):
                self.assertTrue(any('release.apk' in str(call) for call in calls))
                self.assertEqual(data['failure_class'], {
                    'release_dumpsys_error': 'RELEASE_METADATA_QUERY_FAILED',
                    'release_pidof_error': 'RELEASE_PROCESS_QUERY_FAILED',
                    'release_install_false_success': 'RELEASE_APK_INSTALL_FAILED',
                }[failed_step])
                self.assertNotIn('release_pid', data)
            else:
                self.assertFalse(any('release.apk' in str(call) for call in calls))
            if failed_step in ('acceptance_install_false_success', 'release_install_false_success'):
                self.assertEqual(data['failed_step'], 'install -r')
                self.assertEqual(data['failure_class'], (
                    'RELEASE_APK_INSTALL_FAILED' if failed_step.startswith('release_')
                    else 'ACCEPTANCE_APK_INSTALL_FAILED'
                ))
                # Neither a debug-install failure nor a release-install failure can reach its package query.
                package_checks = [call for call in calls if call[3:6] == ['shell', 'dumpsys', 'package']]
                self.assertEqual(len(package_checks), 1 if failed_step.startswith('release_') else 0)
            if failed_step.startswith('uninstall_'):
                self.assertEqual(data['failure_class'], 'DEBUG_APK_UNINSTALL_FAILED')
                self.assertEqual(data['failed_step'], 'uninstall')
                self.assertTrue(any(call[3:4] == ['uninstall'] for call in calls))
            if failed_step.endswith('_read_error'):
                self.assertEqual(data['failure_class'], 'LOGCAT_READ_FAILED')
                self.assertEqual(data['failed_step'], 'logcat -d ' + failed_step.split('_')[0])
            if failed_step.startswith('sdk_'):
                self.assertEqual(data['failure_class'], 'INVALID_DEVICE_METADATA')
                self.assertEqual(data['failed_step'], 'shell getprop ro.build.version.sdk')
                self.assertFalse(any(call[3:4] == ['install'] for call in calls))
            return data['reason']

    def test_debug_install_false_success_blocks_before_package_query(self):
        self.assertIn('Debug acceptance APK installation was not confirmed', self.exercise('acceptance_install_false_success'))

    def test_release_install_false_success_blocks_before_package_query(self):
        self.assertIn('Signed release APK installation was not confirmed', self.exercise('release_install_false_success'))

    def test_failed_acceptance_metadata_query_blocks_forged_version(self):
        self.assertIn('Debug acceptance package metadata could not be verified', self.exercise('acceptance_dumpsys_error'))

    def test_failed_release_metadata_query_blocks_forged_version(self):
        self.assertIn('release package metadata could not be verified', self.exercise('release_dumpsys_error'))

    def test_failed_release_pid_query_blocks_forged_process(self):
        self.assertIn('release process could not be verified', self.exercise('release_pidof_error'))

    def test_unknown_sdk_blocks_before_installation(self):
        for case in ('sdk_non_numeric', 'sdk_empty', 'sdk_command_error'):
            with self.subTest(case=case):
                self.assertIn('SDK version could not be verified', self.exercise(case))

    def test_adb_install_timeout_is_blocked_with_evidence(self):
        self.assertIn('ADB install failed (TimeoutExpired)', self.exercise('install_timeout'))

    def test_adb_getprop_oserror_is_blocked_with_evidence(self):
        self.assertIn('ADB shell failed (OSError)', self.exercise('getprop_oserror'))

    def test_adb_verify_logcat_timeout_is_blocked_with_evidence(self):
        self.assertIn('ADB logcat failed (TimeoutExpired)', self.exercise('verify_logs_timeout'))

    def test_failed_initial_logcat_read_blocks_forged_pass(self):
        self.assertIn('logcat read failed during initial acceptance', self.exercise('run_read_error'))

    def test_failed_verify_logcat_read_blocks_forged_pass(self):
        self.assertIn('logcat read failed during persistence verification', self.exercise('verify_read_error'))

    def test_debug_uninstall_failure_blocks_release_install(self):
        for case in ('uninstall_nonzero', 'uninstall_false_success'):
            with self.subTest(case=case):
                self.assertIn('Debug acceptance APK could not be removed', self.exercise(case))

    def test_app_data_clear_failure_blocks_gate(self):
        self.assertIn('app data', self.exercise('app_data'))

    def test_run_log_clear_failure_blocks_gate(self):
        self.assertIn('logcat', self.exercise('run_logs'))

    def test_force_stop_failure_blocks_gate(self):
        self.assertIn('force-stopped', self.exercise('force_stop'))

    def test_verify_log_clear_failure_blocks_gate(self):
        self.assertIn('logcat', self.exercise('verify_logs'))


if __name__ == '__main__':
    unittest.main()
