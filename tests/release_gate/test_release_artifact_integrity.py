from pathlib import Path
import hashlib
import importlib.util
import json
import tempfile

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / 'tools/release_gate/evaluate_release_gate.py'
SPEC = importlib.util.spec_from_file_location('evaluate_release_gate', MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
release_artifact_integrity = MODULE.release_artifact_integrity


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fixture(root):
    artifact_root = root / 'dist'
    artifact_root.mkdir()
    android = artifact_root / 'android-source.zip'
    ios = artifact_root / 'ios-source.zip'
    android.write_bytes(b'android-runtime-source\n')
    ios.write_bytes(b'ios-runtime-source\n')
    manifest = {
        'android': {
            'source_artifact': android.name,
            'sha256': _sha256(android),
            'bytes': android.stat().st_size,
        },
        'ios': {
            'source_artifact': ios.name,
            'sha256': _sha256(ios),
            'bytes': ios.stat().st_size,
        },
    }
    manifest_path = root / 'manifest.json'
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
    return manifest_path, artifact_root, manifest, android, ios


def _write_manifest(path, manifest):
    path.write_text(json.dumps(manifest), encoding='utf-8')


def test_matching_manifest_hashes_and_sizes_pass():
    with tempfile.TemporaryDirectory() as temp:
        manifest_path, artifact_root, _, _, _ = _fixture(Path(temp))
        passed, reason, items = release_artifact_integrity(manifest_path, artifact_root)
        assert passed is True
        assert reason == 'RELEASE_ARTIFACT_INTEGRITY_MATCH'
        assert [item['status'] for item in items] == ['PASS', 'PASS']


def test_tampered_artifact_hash_fails_closed():
    with tempfile.TemporaryDirectory() as temp:
        manifest_path, artifact_root, _, android, _ = _fixture(Path(temp))
        android.write_bytes(b'tampered-but-same-length!!\n')
        passed, reason, _ = release_artifact_integrity(manifest_path, artifact_root)
        assert passed is False
        assert reason in {'RELEASE_ARTIFACT_SIZE_MISMATCH', 'RELEASE_ARTIFACT_SHA256_MISMATCH'}


def test_declared_size_mismatch_fails_closed():
    with tempfile.TemporaryDirectory() as temp:
        manifest_path, artifact_root, manifest, _, _ = _fixture(Path(temp))
        manifest['android']['bytes'] += 1
        _write_manifest(manifest_path, manifest)
        passed, reason, _ = release_artifact_integrity(manifest_path, artifact_root)
        assert passed is False
        assert reason == 'RELEASE_ARTIFACT_SIZE_MISMATCH'


def test_missing_artifact_fails_closed():
    with tempfile.TemporaryDirectory() as temp:
        manifest_path, artifact_root, _, _, ios = _fixture(Path(temp))
        ios.unlink()
        passed, reason, _ = release_artifact_integrity(manifest_path, artifact_root)
        assert passed is False
        assert reason == 'RELEASE_ARTIFACT_MISSING_OR_UNSAFE'


def test_path_traversal_is_rejected():
    with tempfile.TemporaryDirectory() as temp:
        manifest_path, artifact_root, manifest, _, _ = _fixture(Path(temp))
        manifest['android']['source_artifact'] = '../outside.zip'
        _write_manifest(manifest_path, manifest)
        passed, reason, _ = release_artifact_integrity(manifest_path, artifact_root)
        assert passed is False
        assert reason == 'RELEASE_ARTIFACT_PATH_UNSAFE'


def test_invalid_declared_sha256_is_rejected():
    with tempfile.TemporaryDirectory() as temp:
        manifest_path, artifact_root, manifest, _, _ = _fixture(Path(temp))
        manifest['android']['sha256'] = 'not-a-sha256'
        _write_manifest(manifest_path, manifest)
        passed, reason, _ = release_artifact_integrity(manifest_path, artifact_root)
        assert passed is False
        assert reason == 'RELEASE_ARTIFACT_METADATA_MISSING_OR_INVALID'


def test_symlink_artifact_is_rejected():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        manifest_path, artifact_root, manifest, android, _ = _fixture(root)
        external = root / 'external.zip'
        external.write_bytes(android.read_bytes())
        android.unlink()
        android.symlink_to(external)
        manifest['android']['sha256'] = _sha256(external)
        manifest['android']['bytes'] = external.stat().st_size
        _write_manifest(manifest_path, manifest)
        passed, reason, _ = release_artifact_integrity(manifest_path, artifact_root)
        assert passed is False
        assert reason == 'RELEASE_ARTIFACT_MISSING_OR_UNSAFE'


def main():
    tests = [
        test_matching_manifest_hashes_and_sizes_pass,
        test_tampered_artifact_hash_fails_closed,
        test_declared_size_mismatch_fails_closed,
        test_missing_artifact_fails_closed,
        test_path_traversal_is_rejected,
        test_invalid_declared_sha256_is_rejected,
        test_symlink_artifact_is_rejected,
    ]
    for test in tests:
        test()
    print(f'release artifact integrity contracts: {len(tests)}/{len(tests)} PASS')


if __name__ == '__main__':
    main()
