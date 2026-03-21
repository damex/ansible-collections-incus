# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_cluster_group module."""

from __future__ import annotations

from unittest.mock import MagicMock

from ansible_collections.damex.incus.plugins.modules.incus_cluster_group import main
from ansible_collections.damex.incus.tests.unit.conftest import (
    CONNECTION_PARAMS,
    assert_write_create,
    assert_write_check_mode,
    assert_write_delete,
    assert_write_delete_missing,
    assert_write_skip,
    assert_write_update,
    run_module_main,
)

__all__ = [
    'test_create_cluster_group',
    'test_create_cluster_group_with_members',
    'test_skip_matching_cluster_group',
    'test_skip_matching_cluster_group_with_members',
    'test_update_cluster_group_description',
    'test_update_cluster_group_members',
    'test_delete_existing_cluster_group',
    'test_delete_cluster_group_with_members',
    'test_delete_nonexistent_cluster_group',
    'test_cluster_group_check_mode',
    'test_members_sorted',
]

MODULE = 'ansible_collections.damex.incus.plugins.modules.incus_cluster_group'


def _mock_module(state: str = 'present', check_mode: bool = False) -> MagicMock:
    """Build mock module."""
    module = MagicMock()
    module.params = {
        **CONNECTION_PARAMS,
        'name': 'dpu',
        'state': state,
        'description': '',
        'members': [],
    }
    module.check_mode = check_mode
    return module


def test_create_cluster_group() -> None:
    """Create missing cluster group."""
    assert_write_create(main, MODULE, _mock_module())


def test_create_cluster_group_with_members() -> None:
    """Create cluster group with members."""
    module = _mock_module()
    module.params['members'] = ['arm64-node1', 'arm64-node2']
    client = assert_write_create(main, MODULE, module)
    _post_path, post_data = client.post.call_args.args
    assert 'arm64-node1' in post_data['members']
    assert 'arm64-node2' in post_data['members']


def test_skip_matching_cluster_group() -> None:
    """Skip matching cluster group."""
    assert_write_skip(main, MODULE, _mock_module(), {
        'description': '',
        'members': [],
    })


def test_skip_matching_cluster_group_with_members() -> None:
    """Skip matching cluster group with members."""
    module = _mock_module()
    module.params['members'] = ['arm64-node1', 'arm64-node2']
    assert_write_skip(main, MODULE, module, {
        'description': '',
        'members': ['arm64-node1', 'arm64-node2'],
    })


def test_update_cluster_group_description() -> None:
    """Update cluster group with changed description."""
    module = _mock_module()
    module.params['description'] = 'ARM64 DPU nodes'
    assert_write_update(main, MODULE, module, {
        'description': '',
        'members': [],
    })


def test_update_cluster_group_members() -> None:
    """Update cluster group when members change."""
    module = _mock_module()
    module.params['members'] = ['arm64-node1', 'arm64-node2']
    put_data = assert_write_update(main, MODULE, module, {
        'description': '',
        'members': ['arm64-node1'],
    })
    assert len(put_data['members']) == 2


def test_delete_existing_cluster_group() -> None:
    """Delete existing cluster group."""
    assert_write_delete(main, MODULE, _mock_module(state='absent'), {
        'description': '',
        'members': [],
    })


def test_delete_cluster_group_with_members() -> None:
    """Clear members then delete non-empty cluster group."""
    client = MagicMock()
    client.get.return_value = {'metadata': {'description': '', 'members': ['test-node']}}
    client.put.return_value = {'type': 'sync'}
    client.delete.return_value = {'type': 'sync'}
    run_module_main(MODULE, _mock_module(state='absent'), client, main)
    client.put.assert_called_once()
    _put_path, put_data = client.put.call_args.args
    assert put_data['members'] == []
    client.delete.assert_called_once()


def test_delete_nonexistent_cluster_group() -> None:
    """Skip delete for missing cluster group."""
    assert_write_delete_missing(main, MODULE, _mock_module(state='absent'))


def test_cluster_group_check_mode() -> None:
    """Skip API calls in check mode."""
    assert_write_check_mode(main, MODULE, _mock_module(check_mode=True))


def test_members_sorted() -> None:
    """Verify members are sorted for stable comparison."""
    module = _mock_module()
    module.params['members'] = ['z-node', 'a-node', 'm-node']
    client = assert_write_create(main, MODULE, module)
    _post_path, post_data = client.post.call_args.args
    assert post_data['members'] == ['a-node', 'm-node', 'z-node']
