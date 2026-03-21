# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_image module."""

from __future__ import annotations

from unittest.mock import MagicMock

from ansible_collections.damex.incus.plugins.module_utils.incus import IncusNotFoundException
from ansible_collections.damex.incus.plugins.modules.incus_image import main
from ansible_collections.damex.incus.tests.unit.conftest import (
    CONNECTION_PARAMS,
    assert_write_check_mode,
    assert_write_delete_missing,
    mock_incus_client,
    assert_write_fail_create,
    assert_write_update,
    run_module_main,
)

__all__ = [
    'test_present_alias_exists_no_change',
    'test_present_alias_exists_update_auto_update',
    'test_present_alias_exists_update_public',
    'test_present_alias_exists_update_check_mode',
    'test_present_copy_image',
    'test_present_copy_aliases',
    'test_present_missing_source',
    'test_present_check_mode',
    'test_absent_delete_by_fingerprint',
    'test_absent_alias_not_found',
    'test_absent_check_mode',
]

MODULE = 'ansible_collections.damex.incus.plugins.modules.incus_image'


def _mock_module(state: str = 'present', check_mode: bool = False,
                 source: str | None = 'images:debian/13') -> MagicMock:
    """Build mock module."""
    module = MagicMock()
    module.params = {
        **CONNECTION_PARAMS,
        'alias': 'debian/13',
        'state': state,
        'project': 'default',
        'type': 'container',
        'source': source,
        'source_protocol': 'simplestreams',
        'source_server': None,
        'copy_aliases': False,
        'auto_update': False,
        'public': False,
    }
    module.check_mode = check_mode
    return module


def test_present_alias_exists_no_change() -> None:
    """Skip existing image with matching settings."""
    module = _mock_module()
    client = mock_incus_client()
    client.get.side_effect = [
        {'metadata': {'name': 'debian/13', 'target': 'abc123'}},
        {'metadata': {'auto_update': False, 'public': False, 'properties': {}, 'expires_at': ''}},
    ]
    run_module_main(MODULE, module, client, main)
    module.exit_json.assert_called_once_with(changed=False)
    client.post.assert_not_called()
    client.put.assert_not_called()


def test_present_alias_exists_update_auto_update() -> None:
    """Update auto_update on existing image."""
    module = _mock_module()
    module.params['auto_update'] = True
    image_metadata = {
        'auto_update': False, 'public': False,
        'properties': {'os': 'debian'}, 'expires_at': '2030-01-01T00:00:00Z',
    }
    put_data = assert_write_update(main, MODULE, module, [
        {'metadata': {'name': 'debian/13', 'target': 'abc123'}},
        {'metadata': image_metadata},
    ])
    assert put_data['auto_update'] is True
    assert put_data['public'] is False
    assert put_data['properties'] == {'os': 'debian'}
    assert put_data['expires_at'] == '2030-01-01T00:00:00Z'


def test_present_alias_exists_update_public() -> None:
    """Update public on existing image."""
    module = _mock_module()
    module.params['public'] = True
    put_data = assert_write_update(main, MODULE, module, [
        {'metadata': {'name': 'debian/13', 'target': 'abc123'}},
        {'metadata': {'auto_update': False, 'public': False, 'properties': {}, 'expires_at': ''}},
    ])
    assert put_data['public'] is True
    assert not put_data['expires_at']


def test_present_alias_exists_update_check_mode() -> None:
    """Skip PUT in check mode when update needed."""
    module = _mock_module(check_mode=True)
    module.params['auto_update'] = True
    client = mock_incus_client()
    client.get.side_effect = [
        {'metadata': {'name': 'debian/13', 'target': 'abc123'}},
        {'metadata': {'auto_update': False, 'public': False, 'properties': {}, 'expires_at': ''}},
    ]
    run_module_main(MODULE, module, client, main)
    module.exit_json.assert_called_once_with(changed=True)
    client.put.assert_not_called()


def test_present_copy_image() -> None:
    """Copy new image."""
    module = _mock_module()
    client = mock_incus_client()
    client.get.side_effect = IncusNotFoundException('not found')
    client.post.return_value = {'type': 'sync'}
    run_module_main(MODULE, module, client, main)
    module.exit_json.assert_called_once_with(changed=True)
    client.post.assert_called_once()
    post_data = client.post.call_args[0][1]
    assert post_data['aliases'] == [{'name': 'debian/13'}]
    assert post_data['source']['image_type'] == 'container'


def test_present_copy_aliases() -> None:
    """Include copy_aliases in source."""
    module = _mock_module()
    module.params['copy_aliases'] = True
    client = mock_incus_client()
    client.get.side_effect = IncusNotFoundException('not found')
    client.post.return_value = {'type': 'sync'}
    run_module_main(MODULE, module, client, main)
    post_data = client.post.call_args[0][1]
    assert post_data['source']['copy_aliases'] is True


def test_present_missing_source() -> None:
    """Fail when source missing on create."""
    assert_write_fail_create(main, MODULE, _mock_module(source=None))


def test_present_check_mode() -> None:
    """Skip post in check mode."""
    assert_write_check_mode(main, MODULE, _mock_module(check_mode=True))


def test_absent_delete_by_fingerprint() -> None:
    """Delete image by fingerprint."""
    module = _mock_module(state='absent')
    client = mock_incus_client()
    client.get.return_value = {'metadata': {'name': 'debian/13', 'target': 'abc123'}}
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
    client = mock_incus_client()
    client.get.return_value = {'metadata': {'name': 'debian/13', 'target': 'abc123'}}
    run_module_main(MODULE, module, client, main)
    module.exit_json.assert_called_once_with(changed=True)
    client.delete.assert_not_called()
