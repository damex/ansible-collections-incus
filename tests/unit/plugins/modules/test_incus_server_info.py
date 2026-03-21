# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_server_info module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from ansible_collections.damex.incus.plugins.module_utils.incus_client import IncusClientException
from ansible_collections.damex.incus.plugins.modules.incus_server_info import main
from ansible_collections.damex.incus.tests.unit.conftest import (
    mock_incus_client,
    run_main,
)

__all__ = [
    'test_return_server_metadata',
    'test_return_empty_metadata',
    'test_fail_on_client_exception',
]


def _mock_info_module() -> MagicMock:
    """Build mock info module."""
    module = MagicMock()
    module.params = {}
    return module


@patch('ansible_collections.damex.incus.plugins.modules.incus_server_info.incus_create_client')
@patch('ansible_collections.damex.incus.plugins.modules.incus_server_info.incus_create_info_module')
def test_return_server_metadata(mock_create_module: MagicMock, mock_create_client: MagicMock) -> None:
    """Return server metadata."""
    module = _mock_info_module()
    client = mock_incus_client()
    client.get.return_value = {'metadata': {'api_version': '1.0', 'auth': 'trusted'}}
    run_main(mock_create_module, mock_create_client, module, client, main)
    server = module.exit_json.call_args[1]['server']
    assert server['api_version'] == '1.0'


@patch('ansible_collections.damex.incus.plugins.modules.incus_server_info.incus_create_client')
@patch('ansible_collections.damex.incus.plugins.modules.incus_server_info.incus_create_info_module')
def test_return_empty_metadata(mock_create_module: MagicMock, mock_create_client: MagicMock) -> None:
    """Return empty dict when no metadata."""
    module = _mock_info_module()
    client = mock_incus_client()
    client.get.return_value = {'metadata': None}
    run_main(mock_create_module, mock_create_client, module, client, main)
    module.exit_json.assert_called_once_with(server={})


@patch('ansible_collections.damex.incus.plugins.modules.incus_server_info.incus_create_client')
@patch('ansible_collections.damex.incus.plugins.modules.incus_server_info.incus_create_info_module')
def test_fail_on_client_exception(mock_create_module: MagicMock, mock_create_client: MagicMock) -> None:
    """Fail on client exception."""
    module = _mock_info_module()
    client = mock_incus_client()
    client.get.side_effect = IncusClientException('connection refused')
    run_main(mock_create_module, mock_create_client, module, client, main)
    module.fail_json.assert_called_once_with(msg='connection refused')
