# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_profile module."""

from __future__ import annotations

from unittest.mock import MagicMock

from ansible_collections.damex.incus.plugins.modules.incus_profile import main
from ansible_collections.damex.incus.tests.unit.conftest import (
    CONNECTION_PARAMS,
    assert_write_create,
    assert_write_skip,
    assert_write_update,
    assert_write_delete,
    assert_write_delete_missing,
    assert_write_check_mode,
)

__all__ = [
    'test_create_profile',
    'test_skip_matching_profile',
    'test_update_profile_description',
    'test_update_profile_config',
    'test_update_profile_devices',
    'test_delete_existing_profile',
    'test_delete_nonexistent_profile',
    'test_profile_check_mode',
]

MODULE = 'ansible_collections.damex.incus.plugins.modules.incus_profile'


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


def test_create_profile() -> None:
    """Create missing profile."""
    assert_write_create(main, MODULE, _mock_module())


def test_skip_matching_profile() -> None:
    """Skip matching profile."""
    assert_write_skip(main, MODULE, _mock_module(), {
        'description': '', 'config': {}, 'devices': {},
    })


def test_update_profile_description() -> None:
    """Update profile with changed description."""
    module = _mock_module()
    module.params['description'] = 'new desc'
    assert_write_update(main, MODULE, module, {
        'description': 'old desc', 'config': {}, 'devices': {},
    })


def test_update_profile_config() -> None:
    """Update profile with changed config."""
    module = _mock_module()
    module.params['config'] = {'limits.cpu': '4'}
    assert_write_update(main, MODULE, module, {
        'description': '', 'config': {'limits.cpu': '2'}, 'devices': {},
    })


def test_update_profile_devices() -> None:
    """Update profile with changed devices."""
    module = _mock_module()
    module.params['devices'] = [{'name': 'root', 'type': 'disk', 'path': '/', 'pool': 'fast'}]
    assert_write_update(main, MODULE, module, {
        'description': '', 'config': {},
        'devices': {'root': {'type': 'disk', 'path': '/', 'pool': 'default'}},
    })


def test_delete_existing_profile() -> None:
    """Delete existing profile."""
    assert_write_delete(main, MODULE, _mock_module(state='absent'))


def test_delete_nonexistent_profile() -> None:
    """Skip delete for missing profile."""
    assert_write_delete_missing(main, MODULE, _mock_module(state='absent'))


def test_profile_check_mode() -> None:
    """Skip API calls in check mode."""
    assert_write_check_mode(main, MODULE, _mock_module(check_mode=True))
