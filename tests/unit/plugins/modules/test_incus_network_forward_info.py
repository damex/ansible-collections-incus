# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_network_forward_info module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    IncusClientException,
    IncusNotFoundException,
)
from ansible_collections.damex.incus.plugins.modules.incus_network_forward_info import main
from ansible_collections.damex.incus.tests.unit.conftest import mock_incus_client

__all__ = [
    'test_return_forward_by_name',
    'test_return_empty_for_missing_forward',
    'test_return_all_forwards',
    'test_fail_on_forward_exception',
]

MODULE = 'ansible_collections.damex.incus.plugins.modules.incus_network_forward_info'
UTILS = 'ansible_collections.damex.incus.plugins.module_utils.incus'


def _mock_module(name: str | None = None) -> MagicMock:
    """Build mock info module."""
    module = MagicMock()
    module.params = {
        'network': 'incusbr0',
        'name': name,
        'project': 'default',
    }
    return module


def _run_info(module: MagicMock, client: MagicMock) -> None:
    """Patch module creation and run main."""
    with patch(f'{MODULE}.incus_create_info_module', return_value=module), \
         patch(f'{UTILS}.incus_create_client', return_value=client):
        main()


def test_return_forward_by_name() -> None:
    """Return forward by listen address."""
    module = _mock_module(name='192.168.1.100')
    client = mock_incus_client()
    client.get.return_value = {
        'metadata': {'listen_address': '192.168.1.100', 'description': ''},
    }
    _run_info(module, client)
    result = module.exit_json.call_args[1]['network_forwards']
    assert len(result) == 1
    assert result[0]['listen_address'] == '192.168.1.100'


def test_return_empty_for_missing_forward() -> None:
    """Return empty list for missing forward."""
    module = _mock_module(name='192.168.1.200')
    client = mock_incus_client()
    client.get.side_effect = IncusNotFoundException('not found')
    _run_info(module, client)
    module.exit_json.assert_called_once_with(network_forwards=[])


def test_return_all_forwards() -> None:
    """Return all forwards."""
    module = _mock_module()
    client = mock_incus_client()
    client.get.return_value = {
        'metadata': [
            {'listen_address': '192.168.1.100'},
            {'listen_address': '192.168.1.101'},
        ],
    }
    _run_info(module, client)
    result = module.exit_json.call_args[1]['network_forwards']
    assert len(result) == 2


def test_fail_on_forward_exception() -> None:
    """Fail on client exception."""
    module = _mock_module()
    client = mock_incus_client()
    client.get.side_effect = IncusClientException('connection refused')
    _run_info(module, client)
    module.fail_json.assert_called_once_with(msg='connection refused')
