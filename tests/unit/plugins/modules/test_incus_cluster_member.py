# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_cluster_member module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    IncusClientException,
    IncusNotFoundException,
)
from ansible_collections.damex.incus.plugins.modules.incus_cluster_member import main
from ansible_collections.damex.incus.tests.unit.conftest import (
    CONNECTION_PARAMS,
)

__all__ = [
    'test_create_generates_join_token',
    'test_create_check_mode',
    'test_skip_matching_member',
    'test_update_member_description',
    'test_update_member_config',
    'test_update_member_roles',
    'test_delete_existing_member',
    'test_delete_nonexistent_member',
    'test_fail_on_exception',
]

MODULE = 'ansible_collections.damex.incus.plugins.modules.incus_cluster_member'
UTILS = 'ansible_collections.damex.incus.plugins.module_utils.incus'


def _mock_module(state: str = 'present', check_mode: bool = False) -> MagicMock:
    """Build mock module."""
    module = MagicMock()
    module.params = {
        **CONNECTION_PARAMS,
        'name': 'node2',
        'state': state,
        'description': '',
        'config': {},
        'roles': None,
        'groups': None,
        'failure_domain': None,
        'target': None,
    }
    module.check_mode = check_mode
    return module


def _run_main(module: MagicMock, client: MagicMock) -> None:
    """Patch module creation and client, then run main."""
    with patch(f'{MODULE}.incus_create_write_module', return_value=module), \
         patch(f'{UTILS}.incus_create_client', return_value=client), \
         patch(f'{MODULE}.incus_create_client', return_value=client, create=True):
        main()


def test_create_generates_join_token() -> None:
    """Generate join token when member does not exist."""
    module = _mock_module()
    client = MagicMock()
    client.get.side_effect = IncusNotFoundException('not found')
    client.post.return_value = {'type': 'async', 'metadata': {'id': 'op1'}}
    client.wait.return_value = {
        'metadata': {
            'secret': 'test-join-token',
            'fingerprint': 'abc123',
            'addresses': ['10.0.0.1:8443'],
        },
    }
    _run_main(module, client)
    call_kwargs = module.exit_json.call_args[1]
    assert call_kwargs['changed'] is True
    assert call_kwargs['join_token'] == 'test-join-token'
    assert call_kwargs['join_fingerprint'] == 'abc123'
    assert call_kwargs['join_addresses'] == ['10.0.0.1:8443']
    client.post.assert_called_once()
    post_data = client.post.call_args[0][1]
    assert post_data['server_name'] == 'node2'


def test_create_check_mode() -> None:
    """Skip API calls in check mode for new member."""
    module = _mock_module(check_mode=True)
    client = MagicMock()
    client.get.side_effect = IncusNotFoundException('not found')
    _run_main(module, client)
    module.exit_json.assert_called_once_with(changed=True)
    client.post.assert_not_called()


MULTI_NODE = {'metadata': ['/1.0/cluster/members/node1', '/1.0/cluster/members/node2']}
MEMBER_DEFAULT = {
    'description': '',
    'config': {},
    'roles': [],
    'groups': [],
    'failure_domain': '',
}


def test_skip_matching_member() -> None:
    """Skip update when member already matches."""
    module = _mock_module()
    client = MagicMock()
    client.get.side_effect = [
        {'metadata': MEMBER_DEFAULT},
        MULTI_NODE,
    ]
    _run_main(module, client)
    module.exit_json.assert_called_once_with(changed=False)
    client.put.assert_not_called()


def test_update_member_description() -> None:
    """Update member description."""
    module = _mock_module()
    module.params['description'] = 'Primary node'
    client = MagicMock()
    client.get.side_effect = [
        {'metadata': MEMBER_DEFAULT},
        MULTI_NODE,
    ]
    client.put.return_value = {'type': 'sync'}
    _run_main(module, client)
    module.exit_json.assert_called_once_with(changed=True)
    client.put.assert_called_once()
    put_data = client.put.call_args[0][1]
    assert put_data['description'] == 'Primary node'


def test_update_member_config() -> None:
    """Update member config."""
    module = _mock_module()
    module.params['config'] = {'scheduler.instance': 'manual'}
    client = MagicMock()
    client.get.side_effect = [
        {'metadata': {**MEMBER_DEFAULT, 'config': {'scheduler.instance': 'all'}}},
        MULTI_NODE,
    ]
    client.put.return_value = {'type': 'sync'}
    _run_main(module, client)
    module.exit_json.assert_called_once_with(changed=True)
    put_data = client.put.call_args[0][1]
    assert put_data['config']['scheduler.instance'] == 'manual'


def test_update_member_roles() -> None:
    """Update member roles."""
    module = _mock_module()
    module.params['roles'] = ['event-hub']
    client = MagicMock()
    client.get.side_effect = [
        {'metadata': {**MEMBER_DEFAULT, 'roles': ['database']}},
        MULTI_NODE,
    ]
    client.put.return_value = {'type': 'sync'}
    _run_main(module, client)
    module.exit_json.assert_called_once_with(changed=True)
    put_data = client.put.call_args[0][1]
    assert 'database' in put_data['roles']
    assert 'event-hub' in put_data['roles']


def test_delete_existing_member() -> None:
    """Delete existing cluster member."""
    module = _mock_module(state='absent')
    client = MagicMock()
    client.get.return_value = {
        'metadata': {'description': '', 'config': {}},
    }
    client.delete.return_value = {'type': 'sync'}
    _run_main(module, client)
    module.exit_json.assert_called_once_with(changed=True)
    client.delete.assert_called_once()


def test_delete_nonexistent_member() -> None:
    """Skip delete for missing cluster member."""
    module = _mock_module(state='absent')
    client = MagicMock()
    client.get.side_effect = IncusNotFoundException('not found')
    _run_main(module, client)
    module.exit_json.assert_called_once_with(changed=False)


def test_fail_on_exception() -> None:
    """Fail on client exception."""
    module = _mock_module()
    client = MagicMock()
    client.get.side_effect = IncusClientException('connection refused')
    _run_main(module, client)
    module.fail_json.assert_called_once_with(msg='connection refused')
