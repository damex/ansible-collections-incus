# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_cluster_info module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from ansible_collections.damex.incus.plugins.module_utils.incus_client import IncusClientException
from ansible_collections.damex.incus.plugins.modules.incus_cluster_info import main
from ansible_collections.damex.incus.tests.unit.conftest import (
    mock_incus_client,
    run_main,
)

__all__ = [
    'test_return_cluster_metadata',
    'test_return_empty_cluster',
    'test_fail_on_cluster_exception',
]


def _mock_info_module() -> MagicMock:
    """Build mock info module."""
    module = MagicMock()
    module.params = {}
    return module


@patch('ansible_collections.damex.incus.plugins.modules.incus_cluster_info.incus_create_client')
@patch('ansible_collections.damex.incus.plugins.modules.incus_cluster_info.incus_create_info_module')
def test_return_cluster_metadata(mock_create_module: MagicMock, mock_create_client: MagicMock) -> None:
    """Return cluster metadata."""
    module = _mock_info_module()
    client = mock_incus_client()
    client.get.return_value = {
        'metadata': {'enabled': True, 'server_name': 'node1'},
    }
    run_main(mock_create_module, mock_create_client, module, client, main)
    cluster = module.exit_json.call_args[1]['cluster']
    assert cluster['enabled'] is True
    assert cluster['server_name'] == 'node1'


@patch('ansible_collections.damex.incus.plugins.modules.incus_cluster_info.incus_create_client')
@patch('ansible_collections.damex.incus.plugins.modules.incus_cluster_info.incus_create_info_module')
def test_return_empty_cluster(mock_create_module: MagicMock, mock_create_client: MagicMock) -> None:
    """Return empty dict when no metadata."""
    module = _mock_info_module()
    client = mock_incus_client()
    client.get.return_value = {'metadata': None}
    run_main(mock_create_module, mock_create_client, module, client, main)
    module.exit_json.assert_called_once_with(cluster={})


@patch('ansible_collections.damex.incus.plugins.modules.incus_cluster_info.incus_create_client')
@patch('ansible_collections.damex.incus.plugins.modules.incus_cluster_info.incus_create_info_module')
def test_fail_on_cluster_exception(mock_create_module: MagicMock, mock_create_client: MagicMock) -> None:
    """Fail on client exception."""
    module = _mock_info_module()
    client = mock_incus_client()
    client.get.side_effect = IncusClientException('connection refused')
    run_main(mock_create_module, mock_create_client, module, client, main)
    module.fail_json.assert_called_once_with(msg='connection refused')
