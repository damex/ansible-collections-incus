# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_image_import module."""

from __future__ import annotations

import hashlib
import lzma
import os
import tarfile
import tempfile
import zipfile
from unittest.mock import MagicMock, patch

import pytest

from ansible_collections.damex.incus.plugins.module_utils.incus_client import IncusNotFoundException
from ansible_collections.damex.incus.plugins.modules.incus_image_import import (
    _incus_image_import_build_metadata,
    _incus_image_import_build_tarball,
    _incus_image_import_create_aliases,
    _incus_image_import_download_source,
    _incus_image_import_extract_xz,
    _incus_image_import_extract_zip,
    _incus_image_import_is_xz,
    _incus_image_import_verify_checksum,
    main,
)
from ansible_collections.damex.incus.tests.unit.conftest import (
    CONNECTION_PARAMS,
    assert_exit_changed,
    assert_write_check_mode,
    assert_write_delete_missing,
    mock_incus_client,
    assert_write_fail_create,
    run_module_main,
)

__all__ = [
    'test_is_xz_true',
    'test_is_xz_false',
    'test_extract_xz',
    'test_extract_xz_invalid',
    'test_download_source_local_file',
    'test_download_source_missing_local_file',
    'test_download_source_url',
    'test_verify_checksum_match',
    'test_verify_checksum_mismatch',
    'test_extract_zip_single_file',
    'test_extract_zip_invalid',
    'test_extract_zip_rejects_traversal_entry',
    'test_extract_zip_rejects_absolute_path_entry',
    'test_build_metadata_with_properties',
    'test_build_metadata_without_properties',
    'test_build_tarball_contents',
    'test_create_aliases_single',
    'test_create_aliases_multiple',
    'test_present_alias_exists_no_change',
    'test_present_import_image',
    'test_present_import_with_aliases',
    'test_present_missing_source',
    'test_present_check_mode',
    'test_present_force_reimport',
    'test_present_force_missing_source',
    'test_present_force_deletes_after_upload',
    'test_present_force_check_mode',
    'test_absent_delete_by_fingerprint',
    'test_absent_alias_not_found',
    'test_absent_check_mode',
]

MODULE = 'ansible_collections.damex.incus.plugins.modules.incus_image_import'


def test_is_xz_true() -> None:
    """Detect xz compressed file."""
    with tempfile.NamedTemporaryFile(suffix='.xz') as tmp:
        tmp.write(lzma.compress(b'test data'))
        tmp.flush()
        assert _incus_image_import_is_xz(tmp.name) is True


def test_is_xz_false() -> None:
    """Reject non-xz file."""
    with tempfile.NamedTemporaryFile(suffix='.qcow2') as tmp:
        tmp.write(b'not compressed')
        tmp.flush()
        assert _incus_image_import_is_xz(tmp.name) is False


def test_extract_xz() -> None:
    """Decompress xz file."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        xz_path = os.path.join(tmp_dir, 'test.qcow2.xz')
        with open(xz_path, 'wb') as fh:
            fh.write(lzma.compress(b'qcow2 image data'))
        module = MagicMock()
        result = _incus_image_import_extract_xz(module, xz_path, tmp_dir)
        assert result.endswith('test.qcow2')
        with open(result, 'rb') as fh:
            assert fh.read() == b'qcow2 image data'


def test_extract_xz_invalid() -> None:
    """Fail on invalid xz file."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        bad_path = os.path.join(tmp_dir, 'bad.xz')
        with open(bad_path, 'wb') as fh:
            fh.write(b'not xz data')
        module = MagicMock()
        module.fail_json.side_effect = SystemExit(1)
        try:
            _incus_image_import_extract_xz(module, bad_path, tmp_dir)
        except SystemExit:
            pass
        module.fail_json.assert_called_once()


def test_download_source_local_file() -> None:
    """Return local path unchanged."""
    with tempfile.NamedTemporaryFile() as tmp:
        module = MagicMock()
        result = _incus_image_import_download_source(module, tmp.name, '/tmp', 30)
        assert result == tmp.name


def test_download_source_missing_local_file() -> None:
    """Fail on missing local file."""
    module = MagicMock()
    _incus_image_import_download_source(module, '/nonexistent/path.img', '/tmp', 30)
    module.fail_json.assert_called_once()


def test_download_source_url() -> None:
    """Download URL to temporary directory."""
    module = MagicMock()
    mock_response = MagicMock()
    mock_response.read.return_value = b''
    with tempfile.TemporaryDirectory() as tmp_dir:
        with patch(
            f'{MODULE}.open_url',
            return_value=MagicMock(
                __enter__=MagicMock(return_value=mock_response),
                __exit__=MagicMock(return_value=False),
            ),
        ):
            result = _incus_image_import_download_source(
                module,
                'https://example.com/image.qcow2',
                tmp_dir,
                30,
            )
            assert result == os.path.join(tmp_dir, 'image.qcow2')


def test_verify_checksum_match() -> None:
    """Pass silently on matching checksum."""
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(b'test content')
        tmp.flush()
        expected = hashlib.sha256(b'test content').hexdigest()
        module = MagicMock()
        _incus_image_import_verify_checksum(module, tmp.name, expected, 'sha256')
        module.fail_json.assert_not_called()


def test_verify_checksum_mismatch() -> None:
    """Fail on mismatched checksum."""
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(b'test content')
        tmp.flush()
        module = MagicMock()
        _incus_image_import_verify_checksum(module, tmp.name, 'wrong', 'sha256')
        module.fail_json.assert_called_once()


def test_extract_zip_single_file() -> None:
    """Extract first file from ZIP."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        zip_path = os.path.join(tmp_dir, 'test.zip')
        inner_name = 'image.qcow2'
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr(inner_name, 'fake image')
        module = MagicMock()
        result = _incus_image_import_extract_zip(module, zip_path, tmp_dir)
        assert result == os.path.join(tmp_dir, inner_name)
        with open(result, encoding='utf-8') as file_handle:
            assert file_handle.read() == 'fake image'


def test_extract_zip_invalid() -> None:
    """Fail on invalid ZIP."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        bad_path = os.path.join(tmp_dir, 'bad.zip')
        with open(bad_path, 'wb') as file_handle:
            file_handle.write(b'not a zip')
        module = MagicMock()
        _incus_image_import_extract_zip(module, bad_path, tmp_dir)
        module.fail_json.assert_called_once()


def test_extract_zip_rejects_traversal_entry() -> None:
    """Reject ZIP entries that escape the target via path traversal."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        zip_path = os.path.join(tmp_dir, 'malicious.zip')
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr('../../escape.qcow2', 'malicious content')
        module = MagicMock()
        module.fail_json.side_effect = SystemExit(1)
        with pytest.raises(SystemExit):
            _incus_image_import_extract_zip(module, zip_path, tmp_dir)
        module.fail_json.assert_called_once()
        fail_message = module.fail_json.call_args.kwargs['msg']
        assert 'escapes target directory' in fail_message


def test_extract_zip_rejects_absolute_path_entry() -> None:
    """Reject ZIP entries with absolute paths."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        zip_path = os.path.join(tmp_dir, 'absolute.zip')
        with zipfile.ZipFile(zip_path, 'w') as zf:
            info = zipfile.ZipInfo(filename='/tmp/evil.qcow2')
            zf.writestr(info, 'malicious content')
        module = MagicMock()
        module.fail_json.side_effect = SystemExit(1)
        with pytest.raises(SystemExit):
            _incus_image_import_extract_zip(module, zip_path, tmp_dir)
        module.fail_json.assert_called_once()
        fail_message = module.fail_json.call_args.kwargs['msg']
        assert 'absolute path' in fail_message


def test_build_metadata_with_properties() -> None:
    """Include properties in metadata YAML."""
    result = _incus_image_import_build_metadata(
        'x86_64',
        {'os': 'debian', 'release': 'bookworm'},
    )
    assert 'architecture: x86_64' in result
    assert 'os: debian' in result
    assert 'release: bookworm' in result
    assert 'creation_date:' in result


def test_build_metadata_without_properties() -> None:
    """Omit properties section when None."""
    result = _incus_image_import_build_metadata('aarch64', None)
    assert 'architecture: aarch64' in result
    assert 'properties' not in result


def test_build_tarball_contents() -> None:
    """Verify tarball contains metadata.yaml and rootfs.img."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        image_path = os.path.join(tmp_dir, 'disk.qcow2')
        with open(image_path, 'wb') as file_handle:
            file_handle.write(b'fake image')
        module = MagicMock()
        result = _incus_image_import_build_tarball(
            module,
            image_path,
            'x86_64',
            None,
            tmp_dir,
        )
        assert result.endswith('image.tar.gz')
        with tarfile.open(result, 'r:gz') as tar:
            names = tar.getnames()
            assert 'metadata.yaml' in names
            assert 'rootfs.img' in names


def test_create_aliases_single() -> None:
    """Create single alias."""
    client = MagicMock()
    client.post.return_value = {'type': 'sync'}
    _incus_image_import_create_aliases(client, 'abc123', 'myimage', None, '?project=default')
    client.post.assert_called_once()
    _post_path, alias_data = client.post.call_args.args
    assert alias_data['name'] == 'myimage'
    assert alias_data['target'] == 'abc123'


def test_create_aliases_multiple() -> None:
    """Create primary alias plus additional aliases."""
    client = MagicMock()
    client.post.return_value = {'type': 'sync'}
    _incus_image_import_create_aliases(
        client,
        'abc123',
        'primary',
        ['secondary', 'tertiary'],
        '?project=default',
    )
    assert client.post.call_count == 3
    alias_names = []
    for call in client.post.call_args_list:
        _post_path, alias_payload = call.args
        alias_names.append(alias_payload['name'])
    assert alias_names == ['primary', 'secondary', 'tertiary']


def _mock_module(state: str = 'present', check_mode: bool = False,
                 source: str | None = '/tmp/test.qcow2',
                 force: bool = False) -> MagicMock:
    """Build mock module."""
    module = MagicMock()
    module.params = CONNECTION_PARAMS.copy()
    module.params['alias'] = 'chr/7.22'
    module.params['aliases'] = None
    module.params['state'] = state
    module.params['project'] = 'default'
    module.params['source'] = source
    module.params['checksum'] = None
    module.params['checksum_algorithm'] = 'sha256'
    module.params['architecture'] = 'x86_64'
    module.params['properties'] = {
        'os': 'RouterOS',
        'release': '7.22',
        'description': 'MikroTik CHR 7.22',
    }
    module.params['public'] = False
    module.params['force'] = force
    module.params['timeout'] = 300
    module.check_mode = check_mode
    return module


def test_present_alias_exists_no_change() -> None:
    """Skip existing image."""
    module = _mock_module()
    client = mock_incus_client()
    client.get.return_value = {'metadata': {'name': 'chr/7.22', 'target': 'abc123'}}
    run_module_main(MODULE, module, client, main)
    assert_exit_changed(module, False)
    client.post_file.assert_not_called()


@patch(f'{MODULE}._incus_image_import_prepare', return_value='/tmp/image.tar.gz')
@patch(f'{MODULE}.tempfile')
@patch(f'{MODULE}.shutil')
def test_present_import_image(mock_shutil: MagicMock, mock_tempfile: MagicMock,
                              mock_prepare: MagicMock) -> None:
    """Import new image."""
    mock_tempfile.mkdtemp.return_value = '/tmp/test-dir'
    module = _mock_module()
    client = mock_incus_client()
    client.get.side_effect = IncusNotFoundException('not found')
    client.post_file.return_value = {'type': 'async', 'metadata': {'id': 'op-123'}}
    client.wait.return_value = {'metadata': {'fingerprint': 'abc123'}}
    client.post.return_value = {'type': 'sync'}
    run_module_main(MODULE, module, client, main)
    assert_exit_changed(module, True)
    client.post_file.assert_called_once()
    client.post.assert_called_once()
    _post_path, alias_data = client.post.call_args.args
    assert alias_data['name'] == 'chr/7.22'
    assert alias_data['target'] == 'abc123'
    mock_shutil.rmtree.assert_called_once_with('/tmp/test-dir', ignore_errors=True)
    mock_prepare.assert_called_once()


@patch(f'{MODULE}._incus_image_import_prepare', return_value='/tmp/image.tar.gz')
@patch(f'{MODULE}.tempfile')
@patch(f'{MODULE}.shutil')
def test_present_import_with_aliases(mock_shutil: MagicMock, mock_tempfile: MagicMock,
                                     mock_prepare: MagicMock) -> None:
    """Import image with additional aliases."""
    mock_tempfile.mkdtemp.return_value = '/tmp/test-dir'
    module = _mock_module()
    module.params['alias'] = 'chr'
    module.params['aliases'] = ['chr/7.22']
    client = mock_incus_client()
    client.get.side_effect = IncusNotFoundException('not found')
    client.post_file.return_value = {'type': 'async', 'metadata': {'id': 'op-123'}}
    client.wait.return_value = {'metadata': {'fingerprint': 'abc123'}}
    client.post.return_value = {'type': 'sync'}
    run_module_main(MODULE, module, client, main)
    assert_exit_changed(module, True)
    assert client.post.call_count == 2
    first_call, second_call = client.post.call_args_list
    _first_path, first_alias = first_call.args
    _second_path, second_alias = second_call.args
    assert first_alias['name'] == 'chr'
    assert second_alias['name'] == 'chr/7.22'
    mock_shutil.rmtree.assert_called_once()
    mock_prepare.assert_called_once()


def test_present_missing_source() -> None:
    """Fail when source missing on create."""
    assert_write_fail_create(main, MODULE, _mock_module(source=None))


def test_present_check_mode() -> None:
    """Skip all operations in check mode."""
    assert_write_check_mode(main, MODULE, _mock_module(check_mode=True))


@patch(f'{MODULE}._incus_image_import_prepare', return_value='/tmp/image.tar.gz')
@patch(f'{MODULE}.tempfile')
@patch(f'{MODULE}.shutil')
def test_present_force_reimport(mock_shutil: MagicMock, mock_tempfile: MagicMock,
                                mock_prepare: MagicMock) -> None:
    """Delete and re-import when force is true."""
    mock_tempfile.mkdtemp.return_value = '/tmp/test-dir'
    module = _mock_module(force=True)
    client = mock_incus_client()
    client.get.return_value = {'metadata': {'name': 'chr/7.22', 'target': 'abc123'}}
    client.delete.return_value = {'type': 'sync'}
    client.post_file.return_value = {'type': 'async', 'metadata': {'id': 'op-123'}}
    client.wait.return_value = {'metadata': {'fingerprint': 'def456'}}
    client.post.return_value = {'type': 'sync'}
    run_module_main(MODULE, module, client, main)
    assert_exit_changed(module, True)
    client.delete.assert_called_once()
    delete_path = next(iter(client.delete.call_args.args))
    assert 'abc123' in delete_path
    client.post_file.assert_called_once()
    _post_path, alias_data = client.post.call_args.args
    assert alias_data['name'] == 'chr/7.22'
    assert alias_data['target'] == 'def456'
    mock_shutil.rmtree.assert_called_once_with('/tmp/test-dir', ignore_errors=True)
    mock_prepare.assert_called_once()


def test_present_force_missing_source() -> None:
    """Fail before delete when source missing on force re-import."""
    module = _mock_module(source=None, force=True)
    module.fail_json.side_effect = SystemExit(1)
    client = mock_incus_client()
    client.get.return_value = {'metadata': {'name': 'chr/7.22', 'target': 'abc123'}}
    with pytest.raises(SystemExit):
        run_module_main(MODULE, module, client, main)
    module.fail_json.assert_called_once()
    client.delete.assert_not_called()


@patch(f'{MODULE}._incus_image_import_prepare', return_value='/tmp/image.tar.gz')
@patch(f'{MODULE}.tempfile')
@patch(f'{MODULE}.shutil')
def test_present_force_deletes_after_upload(_mock_shutil: MagicMock, mock_tempfile: MagicMock,
                                            _mock_prepare: MagicMock) -> None:
    """Delete old image only after successful upload."""
    mock_tempfile.mkdtemp.return_value = '/tmp/test-dir'
    module = _mock_module(force=True)
    client = mock_incus_client()
    client.get.return_value = {'metadata': {'name': 'chr/7.22', 'target': 'abc123'}}
    client.delete.return_value = {'type': 'sync'}
    client.post_file.return_value = {'type': 'async', 'metadata': {'id': 'op-123'}}
    client.wait.return_value = {'metadata': {'fingerprint': 'def456'}}
    client.post.return_value = {'type': 'sync'}
    run_module_main(MODULE, module, client, main)
    assert_exit_changed(module, True)
    mutation_order = [
        method_name
        for method_name, call_args, call_kwargs in client.mock_calls
        if method_name in ('post_file', 'delete')
    ]
    assert mutation_order == ['post_file', 'delete']


def test_present_force_check_mode() -> None:
    """Skip force re-import in check mode."""
    module = _mock_module(force=True, check_mode=True)
    client = mock_incus_client()
    client.get.return_value = {'metadata': {'name': 'chr/7.22', 'target': 'abc123'}}
    run_module_main(MODULE, module, client, main)
    assert_exit_changed(module, True)
    client.delete.assert_not_called()
    client.post_file.assert_not_called()


def test_absent_delete_by_fingerprint() -> None:
    """Delete image by fingerprint."""
    module = _mock_module(state='absent')
    client = mock_incus_client()
    client.get.return_value = {'metadata': {'name': 'chr/7.22', 'target': 'abc123'}}
    client.delete.return_value = {'type': 'sync'}
    run_module_main(MODULE, module, client, main)
    assert_exit_changed(module, True)
    client.delete.assert_called_once()
    delete_path = next(iter(client.delete.call_args.args))
    assert 'abc123' in delete_path


def test_absent_alias_not_found() -> None:
    """Skip delete for missing alias."""
    assert_write_delete_missing(main, MODULE, _mock_module(state='absent'))


def test_absent_check_mode() -> None:
    """Skip delete in check mode."""
    module = _mock_module(state='absent', check_mode=True)
    client = mock_incus_client()
    client.get.return_value = {'metadata': {'name': 'chr/7.22', 'target': 'abc123'}}
    run_module_main(MODULE, module, client, main)
    assert_exit_changed(module, True)
    client.delete.assert_not_called()
