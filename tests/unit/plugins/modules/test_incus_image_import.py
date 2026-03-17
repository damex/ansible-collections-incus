# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_image_import module."""

from __future__ import annotations

import lzma
import os
import tempfile
from unittest.mock import MagicMock, patch

from ansible_collections.damex.incus.plugins.module_utils.incus import IncusNotFoundException
from ansible_collections.damex.incus.plugins.modules.incus_image_import import (
    _incus_image_import_extract_xz,
    _incus_image_import_is_xz,
    main,
)
from ansible_collections.damex.incus.tests.unit.conftest import (
    CONNECTION_PARAMS,
    assert_write_check_mode,
    assert_write_delete_missing,
    assert_write_fail_create,
    run_module_main,
)

__all__ = [
    'test_is_xz_true',
    'test_is_xz_false',
    'test_extract_xz',
    'test_extract_xz_invalid',
    'test_present_alias_exists_no_change',
    'test_present_import_image',
    'test_present_import_with_aliases',
    'test_present_missing_source',
    'test_present_check_mode',
    'test_present_force_reimport',
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


def _mock_module(state: str = 'present', check_mode: bool = False,
                 source: str | None = '/tmp/test.qcow2',
                 force: bool = False) -> MagicMock:
    """Build mock module."""
    module = MagicMock()
    module.params = {
        **CONNECTION_PARAMS,
        'alias': 'chr/7.22',
        'aliases': None,
        'state': state,
        'project': 'default',
        'source': source,
        'checksum': None,
        'checksum_algorithm': 'sha256',
        'architecture': 'x86_64',
        'properties': {
            'os': 'RouterOS',
            'release': '7.22',
            'description': 'MikroTik CHR 7.22',
        },
        'public': False,
        'force': force,
        'timeout': 300,
    }
    module.check_mode = check_mode
    return module


def test_present_alias_exists_no_change() -> None:
    """Skip existing image."""
    module = _mock_module()
    client = MagicMock()
    client.get.return_value = {'metadata': {'name': 'chr/7.22', 'target': 'abc123'}}
    run_module_main(MODULE, module, client, main)
    module.exit_json.assert_called_once_with(changed=False)
    client.post_file.assert_not_called()


@patch(f'{MODULE}._incus_image_import_prepare', return_value='/tmp/image.tar.gz')
@patch(f'{MODULE}.tempfile')
@patch(f'{MODULE}.shutil')
def test_present_import_image(mock_shutil: MagicMock, mock_tempfile: MagicMock,
                              mock_prepare: MagicMock) -> None:
    """Import new image."""
    mock_tempfile.mkdtemp.return_value = '/tmp/test-dir'
    module = _mock_module()
    client = MagicMock()
    client.get.side_effect = IncusNotFoundException('not found')
    client.post_file.return_value = {'type': 'async', 'metadata': {'id': 'op-123'}}
    client.wait.return_value = {'metadata': {'fingerprint': 'abc123'}}
    client.post.return_value = {'type': 'sync'}
    run_module_main(MODULE, module, client, main)
    module.exit_json.assert_called_once_with(changed=True)
    client.post_file.assert_called_once()
    client.post.assert_called_once()
    alias_data = client.post.call_args[0][1]
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
    client = MagicMock()
    client.get.side_effect = IncusNotFoundException('not found')
    client.post_file.return_value = {'type': 'async', 'metadata': {'id': 'op-123'}}
    client.wait.return_value = {'metadata': {'fingerprint': 'abc123'}}
    client.post.return_value = {'type': 'sync'}
    run_module_main(MODULE, module, client, main)
    module.exit_json.assert_called_once_with(changed=True)
    assert client.post.call_count == 2
    first_alias = client.post.call_args_list[0][0][1]
    second_alias = client.post.call_args_list[1][0][1]
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
    client = MagicMock()
    client.get.return_value = {'metadata': {'name': 'chr/7.22', 'target': 'abc123'}}
    client.delete.return_value = {'type': 'sync'}
    client.post_file.return_value = {'type': 'async', 'metadata': {'id': 'op-123'}}
    client.wait.return_value = {'metadata': {'fingerprint': 'def456'}}
    client.post.return_value = {'type': 'sync'}
    run_module_main(MODULE, module, client, main)
    module.exit_json.assert_called_once_with(changed=True)
    client.delete.assert_called_once()
    assert 'abc123' in client.delete.call_args[0][0]
    client.post_file.assert_called_once()
    alias_data = client.post.call_args[0][1]
    assert alias_data['name'] == 'chr/7.22'
    assert alias_data['target'] == 'def456'
    mock_shutil.rmtree.assert_called_once_with('/tmp/test-dir', ignore_errors=True)
    mock_prepare.assert_called_once()


def test_present_force_check_mode() -> None:
    """Skip force re-import in check mode."""
    module = _mock_module(force=True, check_mode=True)
    client = MagicMock()
    client.get.return_value = {'metadata': {'name': 'chr/7.22', 'target': 'abc123'}}
    run_module_main(MODULE, module, client, main)
    module.exit_json.assert_called_once_with(changed=True)
    client.delete.assert_not_called()
    client.post_file.assert_not_called()


def test_absent_delete_by_fingerprint() -> None:
    """Delete image by fingerprint."""
    module = _mock_module(state='absent')
    client = MagicMock()
    client.get.return_value = {'metadata': {'name': 'chr/7.22', 'target': 'abc123'}}
    client.delete.return_value = {'type': 'sync'}
    run_module_main(MODULE, module, client, main)
    module.exit_json.assert_called_once_with(changed=True)
    client.delete.assert_called_once()
    assert 'abc123' in client.delete.call_args[0][0]


def test_absent_alias_not_found() -> None:
    """Skip delete for missing alias."""
    assert_write_delete_missing(main, MODULE, _mock_module(state='absent'))


def test_absent_check_mode() -> None:
    """Skip delete in check mode."""
    module = _mock_module(state='absent', check_mode=True)
    client = MagicMock()
    client.get.return_value = {'metadata': {'name': 'chr/7.22', 'target': 'abc123'}}
    run_module_main(MODULE, module, client, main)
    module.exit_json.assert_called_once_with(changed=True)
    client.delete.assert_not_called()
