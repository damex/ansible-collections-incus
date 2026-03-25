# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_storage module."""

from __future__ import annotations

from unittest.mock import MagicMock

from ansible_collections.damex.incus.plugins.modules.incus_storage import main
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
    'test_create_storage_with_driver',
    'test_skip_matching_storage',
    'test_update_storage_config',
    'test_update_preserves_immutable_source',
    'test_update_preserves_immutable_zfs_pool_name',
    'test_update_drops_absent_immutable_key',
    'test_delete_existing_storage',
    'test_delete_existing_storage_per_target',
    'test_delete_nonexistent_storage',
    'test_storage_check_mode',
]

MODULE = 'ansible_collections.damex.incus.plugins.modules.incus_storage'


def _mock_module(state: str = 'present', check_mode: bool = False) -> MagicMock:
    """Build mock module."""
    module = MagicMock()
    module.params = CONNECTION_PARAMS.copy()
    module.params['name'] = 'tank'
    module.params['state'] = state
    module.params['description'] = ''
    module.params['config'] = {}
    module.params['driver'] = 'zfs'
    module.check_mode = check_mode
    return module


def test_create_storage_with_driver() -> None:
    """Create storage pool with driver."""
    result = assert_write_create(main, MODULE, _mock_module())
    assert result.post.call_args[0][1]['driver'] == 'zfs'


def test_skip_matching_storage() -> None:
    """Skip matching storage pool."""
    assert_write_skip(main, MODULE, _mock_module(), {'description': '', 'config': {}})


def test_update_storage_config() -> None:
    """Update storage pool with changed config."""
    module = _mock_module()
    module.params['config'] = {'size': '100GB'}
    assert_write_update(main, MODULE, module, {'description': '', 'config': {}})


def test_update_preserves_immutable_source() -> None:
    """Preserve immutable source from current when not in desired."""
    module = _mock_module()
    module.params['config'] = {'size': '200GB'}
    current = {
        'description': '',
        'config': {'source': '/dev/sda'},
    }
    put_data = assert_write_update(main, MODULE, module, current)
    assert put_data['config']['source'] == '/dev/sda'
    assert put_data['config']['size'] == '200GB'


def test_update_preserves_immutable_zfs_pool_name() -> None:
    """Preserve driver-specific immutable zfs.pool_name when not in desired."""
    module = _mock_module()
    module.params['config'] = {'size': '200GB'}
    current = {
        'description': '',
        'config': {'zfs.pool_name': 'tank'},
    }
    put_data = assert_write_update(main, MODULE, module, current)
    assert put_data['config']['zfs.pool_name'] == 'tank'
    assert put_data['config']['size'] == '200GB'


def test_update_drops_absent_immutable_key() -> None:
    """Drop immutable key from desired when absent from current."""
    module = _mock_module()
    module.params['config'] = {'size': '100GB', 'source': '/dev/sdb'}
    current = {
        'description': '',
        'config': {},
    }
    put_data = assert_write_update(main, MODULE, module, current)
    assert 'source' not in put_data['config']
    assert put_data['config']['size'] == '100GB'


def test_delete_existing_storage() -> None:
    """Delete existing storage pool."""
    assert_write_delete(main, MODULE, _mock_module(state='absent'))


def test_delete_existing_storage_per_target() -> None:
    """Delete storage pool member scoped to cluster target."""
    module = _mock_module(state='absent')
    module.params['target'] = 'biggie1.home'
    client = assert_write_delete(main, MODULE, module)
    client.delete.assert_called_once_with('/1.0/storage-pools/tank?target=biggie1.home')


def test_delete_nonexistent_storage() -> None:
    """Skip delete for missing storage pool."""
    assert_write_delete_missing(main, MODULE, _mock_module(state='absent'))


def test_storage_check_mode() -> None:
    """Skip API calls in check mode."""
    assert_write_check_mode(main, MODULE, _mock_module(check_mode=True))
