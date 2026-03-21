# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_ensure_resource."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    IncusNotFoundException,
    IncusResourceOptions,
    incus_ensure_resource,
)
from ansible_collections.damex.incus.tests.unit.conftest import (
    CONNECTION_PARAMS,
    mock_incus_client,
)

__all__ = [
    'test_ensure_resource_create',
    'test_ensure_resource_no_change',
    'test_ensure_resource_update',
    'test_ensure_resource_delete_exists',
    'test_ensure_resource_delete_not_exists',
    'test_ensure_resource_check_mode_create',
    'test_ensure_resource_check_mode_update',
    'test_ensure_resource_check_mode_delete',
    'test_ensure_resource_project_query',
    'test_ensure_resource_project_and_target',
    'test_ensure_resource_create_only_params',
    'test_ensure_resource_create_only_param_missing_fails',
    'test_ensure_resource_target_create',
    'test_ensure_resource_target_exists_created_skips',
    'test_ensure_resource_target_pending_updates',
    'test_ensure_resource_target_pending_posts',
    'test_ensure_resource_target_errored_fails_with_message',
    'test_ensure_resource_target_not_found_but_created_skips',
    'test_ensure_resource_pending_finalize',
    'test_ensure_resource_encodes_name',
    'test_ensure_resource_encodes_name_on_update',
    'test_ensure_resource_encodes_name_on_delete',
    'test_ensure_resource_update_extra_config_keys',
    'test_ensure_resource_update_extra_device_keys',
]


def _ensure_module(
    name: str = 'test', state: str = 'present',
    project: str | None = None, target: str | None = None,
    check_mode: bool = False,
) -> MagicMock:
    """Build mock module."""
    module = MagicMock()
    module.params = {
        **CONNECTION_PARAMS,
        'name': name,
        'state': state,
        'target': target,
    }
    if project:
        module.params['project'] = project
    module.check_mode = check_mode
    return module


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_ensure_resource_create(mock_create_client: MagicMock) -> None:
    """Create missing resource."""
    client = mock_incus_client()
    client.get.side_effect = IncusNotFoundException('not found')
    client.post.return_value = {'type': 'sync'}
    mock_create_client.return_value = client

    module = _ensure_module()
    desired = {'description': '', 'config': {}}
    result = incus_ensure_resource(module, 'projects', desired)

    assert result is True
    client.post.assert_called_once()


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_ensure_resource_no_change(mock_create_client: MagicMock) -> None:
    """Skip matching resource."""
    client = mock_incus_client()
    client.get.return_value = {'metadata': {'description': 'desc', 'config': {'k': 'v'}}}
    mock_create_client.return_value = client

    module = _ensure_module()
    desired = {'description': 'desc', 'config': {'k': 'v'}}
    result = incus_ensure_resource(module, 'projects', desired)

    assert result is False


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_ensure_resource_update(mock_create_client: MagicMock) -> None:
    """Update changed resource."""
    client = mock_incus_client()
    client.get.return_value = {'metadata': {'description': 'old', 'config': {}}}
    client.put.return_value = {'type': 'sync'}
    mock_create_client.return_value = client

    module = _ensure_module()
    desired = {'description': 'new', 'config': {}}
    result = incus_ensure_resource(module, 'projects', desired)

    assert result is True
    client.put.assert_called_once()


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_ensure_resource_delete_exists(mock_create_client: MagicMock) -> None:
    """Delete existing resource."""
    client = mock_incus_client()
    client.get.return_value = {'metadata': {'description': '', 'config': {}}}
    client.delete.return_value = {'type': 'sync'}
    mock_create_client.return_value = client

    module = _ensure_module(state='absent')
    result = incus_ensure_resource(module, 'projects', {'description': '', 'config': {}})

    assert result is True
    client.delete.assert_called_once()


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_ensure_resource_delete_not_exists(mock_create_client: MagicMock) -> None:
    """Skip deleting missing resource."""
    client = mock_incus_client()
    client.get.side_effect = IncusNotFoundException('not found')
    mock_create_client.return_value = client

    module = _ensure_module(state='absent')
    result = incus_ensure_resource(module, 'projects', {'description': '', 'config': {}})

    assert result is False


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_ensure_resource_check_mode_create(mock_create_client: MagicMock) -> None:
    """Skip create in check mode."""
    client = mock_incus_client()
    client.get.side_effect = IncusNotFoundException('not found')
    mock_create_client.return_value = client

    module = _ensure_module(check_mode=True)
    result = incus_ensure_resource(module, 'projects', {'description': '', 'config': {}})

    assert result is True
    client.post.assert_not_called()


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_ensure_resource_check_mode_update(mock_create_client: MagicMock) -> None:
    """Skip PUT in check mode."""
    client = mock_incus_client()
    client.get.return_value = {'metadata': {'description': 'old', 'config': {}}}
    mock_create_client.return_value = client

    module = _ensure_module(check_mode=True)
    desired = {'description': 'new', 'config': {}}
    result = incus_ensure_resource(module, 'projects', desired)

    assert result is True
    client.put.assert_not_called()


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_ensure_resource_check_mode_delete(mock_create_client: MagicMock) -> None:
    """Skip DELETE in check mode."""
    client = mock_incus_client()
    client.get.return_value = {'metadata': {'description': '', 'config': {}}}
    mock_create_client.return_value = client

    module = _ensure_module(state='absent', check_mode=True)
    result = incus_ensure_resource(module, 'projects', {'description': '', 'config': {}})

    assert result is True
    client.delete.assert_not_called()


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_ensure_resource_project_query(mock_create_client: MagicMock) -> None:
    """Add project query param."""
    client = mock_incus_client()
    client.get.side_effect = IncusNotFoundException('not found')
    client.post.return_value = {'type': 'sync'}
    mock_create_client.return_value = client

    module = _ensure_module(project='myproject')
    desired = {'description': '', 'config': {}}
    incus_ensure_resource(module, 'networks', desired)

    client.get.assert_called_with('/1.0/networks/test?project=myproject')
    client.post.assert_called_once()
    args = client.post.call_args
    assert '?project=myproject' in args[0][0]


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_ensure_resource_project_and_target(mock_create_client: MagicMock) -> None:
    """Combine project and target in queries."""
    client = mock_incus_client()
    client.get.side_effect = IncusNotFoundException('not found')
    client.post.return_value = {'type': 'sync'}
    mock_create_client.return_value = client

    module = _ensure_module(project='myproject')
    module.params['target'] = 'node1'
    module.params['driver'] = 'dir'
    desired = {'description': '', 'config': {}}
    incus_ensure_resource(
        module, 'storage-pools', desired,
        IncusResourceOptions(create_only_params=['driver']),
    )

    get_path = client.get.call_args_list[0][0][0]
    assert '?project=myproject&target=node1' in get_path
    global_get_path = client.get.call_args_list[1][0][0]
    assert '?project=myproject' in global_get_path
    assert 'target' not in global_get_path
    post_path = client.post.call_args[0][0]
    assert '?project=myproject&target=node1' in post_path


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_ensure_resource_create_only_params(mock_create_client: MagicMock) -> None:
    """Include create-only params."""
    client = mock_incus_client()
    client.get.side_effect = IncusNotFoundException('not found')
    client.post.return_value = {'type': 'sync'}
    mock_create_client.return_value = client

    module = _ensure_module()
    module.params['driver'] = 'zfs'
    desired = {'description': '', 'config': {}}
    incus_ensure_resource(
        module, 'storage-pools', desired,
        IncusResourceOptions(create_only_params=['driver']),
    )

    post_data = client.post.call_args[0][1]
    assert post_data['driver'] == 'zfs'


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_ensure_resource_create_only_param_missing_fails(mock_create_client: MagicMock) -> None:
    """Fail when required create-only param is missing."""
    client = mock_incus_client()
    client.get.side_effect = IncusNotFoundException('not found')
    mock_create_client.return_value = client

    module = _ensure_module()
    module.fail_json.side_effect = SystemExit(1)
    desired = {'description': '', 'config': {}}
    with pytest.raises(SystemExit):
        incus_ensure_resource(
            module, 'storage-pools', desired,
            IncusResourceOptions(create_only_params=['driver']),
        )
    module.fail_json.assert_called_once()
    assert 'driver' in module.fail_json.call_args[1]['msg']


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_ensure_resource_target_create(mock_create_client: MagicMock) -> None:
    """Include target in create query."""
    client = mock_incus_client()
    client.get.side_effect = IncusNotFoundException('not found')
    client.post.return_value = {'type': 'sync'}
    mock_create_client.return_value = client

    module = _ensure_module()
    module.params['target'] = 'node1'
    module.params['driver'] = 'dir'
    desired = {'description': '', 'config': {}}
    result = incus_ensure_resource(
        module, 'storage-pools', desired,
        IncusResourceOptions(create_only_params=['driver']),
    )

    assert result is True
    post_path = client.post.call_args[0][0]
    assert '?target=node1' in post_path


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_ensure_resource_target_exists_created_skips(mock_create_client: MagicMock) -> None:
    """Skip when target is set and resource exists with non-pending status."""
    client = mock_incus_client()
    client.get.return_value = {'metadata': {'description': 'old', 'config': {}, 'status': 'Created'}}
    mock_create_client.return_value = client

    module = _ensure_module()
    module.params['target'] = 'node1'
    desired = {'description': 'new', 'config': {}}
    result = incus_ensure_resource(module, 'storage-pools', desired)

    assert result is False
    client.put.assert_not_called()
    client.post.assert_not_called()


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_ensure_resource_target_pending_updates(mock_create_client: MagicMock) -> None:
    """POST when target is set and both targeted and global status are Pending."""
    client = mock_incus_client()
    client.get.side_effect = [
        {'metadata': {'description': '', 'config': {}, 'status': 'Pending'}},
        {'metadata': {'description': '', 'config': {}, 'status': 'Pending'}},
    ]
    client.post.return_value = {'type': 'sync'}
    mock_create_client.return_value = client

    module = _ensure_module()
    module.params['target'] = 'node1'
    module.params['driver'] = 'dir'
    desired = {'description': '', 'config': {}}
    result = incus_ensure_resource(
        module, 'storage-pools', desired,
        IncusResourceOptions(create_only_params=['driver']),
    )

    assert result is True
    client.post.assert_called_once()
    client.put.assert_not_called()


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_ensure_resource_target_pending_posts(mock_create_client: MagicMock) -> None:
    """POST per-member when resource does not exist at all."""
    client = mock_incus_client()
    client.get.side_effect = IncusNotFoundException('not found')
    client.post.return_value = {'type': 'sync'}
    mock_create_client.return_value = client

    module = _ensure_module()
    module.params['target'] = 'node2'
    module.params['driver'] = 'dir'
    desired = {'description': '', 'config': {}}
    result = incus_ensure_resource(
        module, 'storage-pools', desired,
        IncusResourceOptions(create_only_params=['driver']),
    )

    assert result is True
    client.post.assert_called_once()
    post_path = client.post.call_args[0][0]
    assert '?target=node2' in post_path


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_ensure_resource_target_errored_fails_with_message(mock_create_client: MagicMock) -> None:
    """Fail with message when target shows Pending but global is Errored."""
    client = mock_incus_client()
    client.get.side_effect = [
        {'metadata': {'config': {}, 'status': 'Pending'}},
        {'metadata': {'config': {}, 'status': 'Errored'}},
    ]
    mock_create_client.return_value = client

    module = _ensure_module()
    module.params['target'] = 'node1'
    desired = {'description': '', 'config': {}}
    incus_ensure_resource(module, 'networks', desired)

    module.fail_json.assert_called_once()
    assert 'errored state, delete it first' in module.fail_json.call_args[1]['msg']


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_ensure_resource_target_not_found_but_created_skips(mock_create_client: MagicMock) -> None:
    """Skip when target GET returns 404 but resource exists globally as Created."""
    client = mock_incus_client()
    client.get.side_effect = [
        IncusNotFoundException('not found'),
        {'metadata': {'status': 'Created', 'config': {}}},
    ]
    mock_create_client.return_value = client

    module = _ensure_module()
    module.params['target'] = 'node1'
    desired = {'description': '', 'config': {}}
    result = incus_ensure_resource(module, 'networks', desired)

    assert result is False
    client.post.assert_not_called()
    client.put.assert_not_called()


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_ensure_resource_pending_finalize(mock_create_client: MagicMock) -> None:
    """POST to finalize when resource is pending and no target."""
    client = mock_incus_client()
    client.get.return_value = {'metadata': {'description': '', 'config': {}, 'status': 'Pending'}}
    client.post.return_value = {'type': 'sync'}
    mock_create_client.return_value = client

    module = _ensure_module()
    module.params['driver'] = 'dir'
    desired = {'description': '', 'config': {}}
    result = incus_ensure_resource(
        module, 'storage-pools', desired,
        IncusResourceOptions(create_only_params=['driver']),
    )

    assert result is True
    client.post.assert_called_once()
    client.put.assert_not_called()


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_ensure_resource_encodes_name(mock_create_client: MagicMock) -> None:
    """Encode special characters in resource name on GET."""
    client = mock_incus_client()
    client.get.side_effect = IncusNotFoundException('not found')
    client.post.return_value = {'type': 'sync'}
    mock_create_client.return_value = client

    module = _ensure_module(name='my pool/test')
    desired = {'description': '', 'config': {}}
    incus_ensure_resource(module, 'storage-pools', desired)

    get_path = client.get.call_args[0][0]
    assert '/1.0/storage-pools/my%20pool%2Ftest' in get_path


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_ensure_resource_encodes_name_on_update(mock_create_client: MagicMock) -> None:
    """Encode special characters in resource name on PUT."""
    client = mock_incus_client()
    client.get.return_value = {'metadata': {'description': 'old', 'config': {}}}
    client.put.return_value = {'type': 'sync'}
    mock_create_client.return_value = client

    module = _ensure_module(name='net&work')
    desired = {'description': 'new', 'config': {}}
    incus_ensure_resource(module, 'networks', desired)

    put_path = client.put.call_args[0][0]
    assert '/1.0/networks/net%26work' in put_path


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_ensure_resource_encodes_name_on_delete(mock_create_client: MagicMock) -> None:
    """Encode special characters in resource name on DELETE."""
    client = mock_incus_client()
    client.get.return_value = {'metadata': {'description': '', 'config': {}}}
    client.delete.return_value = {'type': 'sync'}
    mock_create_client.return_value = client

    module = _ensure_module(name='pool #1', state='absent')
    desired = {'description': '', 'config': {}}
    incus_ensure_resource(module, 'storage-pools', desired)

    delete_path = client.delete.call_args[0][0]
    assert '/1.0/storage-pools/pool%20%231' in delete_path


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_ensure_resource_update_extra_config_keys(mock_create_client: MagicMock) -> None:
    """Update when current config has extra keys not in desired."""
    client = mock_incus_client()
    client.get.return_value = {
        'metadata': {
            'description': 'desc',
            'config': {'k': 'v', 'extra': 'val'},
        },
    }
    client.put.return_value = {'type': 'sync'}
    mock_create_client.return_value = client
    module = _ensure_module()
    desired = {'description': 'desc', 'config': {'k': 'v'}}
    result = incus_ensure_resource(module, 'projects', desired)
    assert result is True
    client.put.assert_called_once()


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_ensure_resource_update_extra_device_keys(mock_create_client: MagicMock) -> None:
    """Update when current has extra devices not in desired."""
    client = mock_incus_client()
    client.get.return_value = {
        'metadata': {
            'description': '',
            'config': {},
            'devices': {
                'eth0': {'type': 'nic', 'network': 'br0'},
                'extra': {'type': 'disk', 'path': '/mnt'},
            },
        },
    }
    client.put.return_value = {'type': 'sync'}
    mock_create_client.return_value = client
    module = _ensure_module()
    desired = {
        'description': '',
        'config': {},
        'devices': {'eth0': {'type': 'nic', 'network': 'br0'}},
    }
    result = incus_ensure_resource(module, 'profiles', desired)
    assert result is True
    client.put.assert_called_once()
