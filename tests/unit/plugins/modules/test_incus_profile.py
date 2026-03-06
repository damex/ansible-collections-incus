# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_profile module."""

from __future__ import annotations

from unittest.mock import MagicMock

from ansible_collections.damex.incus.plugins.modules.incus_profile import (
    _get_profile,
    _create_profile,
    _update_profile,
    _delete_profile,
    main,
)
from ansible_collections.damex.incus.tests.unit.conftest import (
    CONNECTION_PARAMS,
    assert_get_found,
    assert_get_not_found,
    assert_crud,
    assert_crud_skip,
    run_module_main,
    assert_module_create,
    assert_module_delete,
    assert_module_delete_missing,
    assert_module_check_mode_create,
)

__all__ = [
    'test_get_profile_found',
    'test_get_profile_not_found',
    'test_create_profile',
    'test_create_profile_check_mode',
    'test_update_profile',
    'test_update_profile_check_mode',
    'test_delete_profile',
    'test_delete_profile_check_mode',
    'test_main_create_missing',
    'test_main_skip_matching',
    'test_main_update_changed_description',
    'test_main_update_changed_config',
    'test_main_update_changed_devices',
    'test_main_delete_existing',
    'test_main_delete_nonexistent',
    'test_main_check_mode_create',
]

MODULE = 'ansible_collections.damex.incus.plugins.modules.incus_profile'


def test_get_profile_found() -> None:
    """Return metadata for existing profile."""
    meta = assert_get_found(_get_profile, {'name': 'base', 'description': 'Base'}, 'default', 'base')
    assert meta['name'] == 'base'


def test_get_profile_not_found() -> None:
    """Return empty dict for missing profile."""
    assert_get_not_found(_get_profile, 'default', 'base')


def test_create_profile() -> None:
    """Post profile creation request."""
    assert_crud(_create_profile, 'post', 'default', 'base', {'description': ''})


def test_create_profile_check_mode() -> None:
    """Skip post in check mode."""
    assert_crud_skip(_create_profile, 'post', 'default', 'base', {'description': ''})


def test_update_profile() -> None:
    """Put profile update request."""
    assert_crud(_update_profile, 'put', 'default', 'base', {'description': 'new'})


def test_update_profile_check_mode() -> None:
    """Skip put in check mode."""
    assert_crud_skip(_update_profile, 'put', 'default', 'base', {'description': 'new'})


def test_delete_profile() -> None:
    """Delete profile request."""
    assert_crud(_delete_profile, 'delete', 'default', 'base')


def test_delete_profile_check_mode() -> None:
    """Skip delete in check mode."""
    assert_crud_skip(_delete_profile, 'delete', 'default', 'base')


def _mock_module(state: str = 'present', check_mode: bool = False) -> MagicMock:
    """Build mock module."""
    module = MagicMock()
    module.params = {
        **CONNECTION_PARAMS,
        'name': 'base',
        'state': state,
        'project': 'default',
        'devices': [],
        'config': {},
        'description': '',
    }
    module.check_mode = check_mode
    return module


def test_main_create_missing() -> None:
    """Create missing profile."""
    assert_module_create(main, MODULE, _mock_module())


def test_main_skip_matching() -> None:
    """Skip matching profile."""
    module = _mock_module()
    client = MagicMock()
    client.get.return_value = {'metadata': {
        'description': '', 'config': {}, 'devices': {},
    }}
    run_module_main(MODULE, module, client, main)
    module.exit_json.assert_called_once_with(changed=False)


def test_main_update_changed_description() -> None:
    """Update profile with changed description."""
    module = _mock_module()
    module.params['description'] = 'new desc'
    client = MagicMock()
    client.get.return_value = {'metadata': {
        'description': 'old desc', 'config': {}, 'devices': {},
    }}
    client.put.return_value = {'type': 'sync'}
    run_module_main(MODULE, module, client, main)
    module.exit_json.assert_called_once_with(changed=True)
    client.put.assert_called_once()


def test_main_update_changed_config() -> None:
    """Update profile with changed config."""
    module = _mock_module()
    module.params['config'] = {'limits.cpu': '4'}
    client = MagicMock()
    client.get.return_value = {'metadata': {
        'description': '', 'config': {'limits.cpu': '2'}, 'devices': {},
    }}
    client.put.return_value = {'type': 'sync'}
    run_module_main(MODULE, module, client, main)
    module.exit_json.assert_called_once_with(changed=True)


def test_main_update_changed_devices() -> None:
    """Update profile with changed devices."""
    module = _mock_module()
    module.params['devices'] = [{'name': 'root', 'type': 'disk', 'path': '/', 'pool': 'fast'}]
    client = MagicMock()
    client.get.return_value = {'metadata': {
        'description': '', 'config': {},
        'devices': {'root': {'type': 'disk', 'path': '/', 'pool': 'default'}},
    }}
    client.put.return_value = {'type': 'sync'}
    run_module_main(MODULE, module, client, main)
    module.exit_json.assert_called_once_with(changed=True)


def test_main_delete_existing() -> None:
    """Delete existing profile."""
    assert_module_delete(main, MODULE, _mock_module(state='absent'), {'description': '', 'config': {}})


def test_main_delete_nonexistent() -> None:
    """Skip delete for missing profile."""
    assert_module_delete_missing(main, MODULE, _mock_module(state='absent'))


def test_main_check_mode_create() -> None:
    """Skip API calls in check mode."""
    assert_module_check_mode_create(main, MODULE, _mock_module(check_mode=True))
