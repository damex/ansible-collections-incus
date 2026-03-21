# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_storage_volume_info module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from ansible_collections.damex.incus.plugins.module_utils.incus_client import (
    IncusClientException,
    IncusNotFoundException,
)
from ansible_collections.damex.incus.plugins.modules.incus_storage_volume_info import main
from ansible_collections.damex.incus.tests.unit.conftest import mock_incus_client

__all__ = [
    'test_return_volume_by_name',
    'test_return_empty_for_missing_volume',
    'test_return_all_volumes',
    'test_fail_on_volume_exception',
]

MODULE = 'ansible_collections.damex.incus.plugins.modules.incus_storage_volume_info'


def _mock_module(name: str | None = None) -> MagicMock:
    """Build mock info module."""
    module = MagicMock()
    module.params = {
        'pool': 'default',
        'name': name,
        'project': 'default',
        'socket_path': '/var/lib/incus/unix.socket',
        'url': None,
        'client_cert': None,
        'client_key': None,
        'server_cert': None,
        'client_cert_path': None,
        'client_key_path': None,
        'server_cert_path': None,
        'token': None,
        'validate_certs': True,
    }
    return module


def _run_info(module: MagicMock, client: MagicMock) -> None:
    """Patch module creation and run main."""
    with patch(f'{MODULE}.AnsibleModule', return_value=module), \
         patch(f'{MODULE}.incus_create_client', return_value=client):
        main()


def test_return_volume_by_name() -> None:
    """Return volume by name."""
    module = _mock_module(name='data')
    client = mock_incus_client()
    client.get.return_value = {'metadata': {'name': 'data', 'content_type': 'filesystem'}}
    _run_info(module, client)
    result = module.exit_json.call_args[1]['storage_volumes']
    assert len(result) == 1
    assert result[0]['name'] == 'data'


def test_return_empty_for_missing_volume() -> None:
    """Return empty list for missing volume."""
    module = _mock_module(name='missing')
    client = mock_incus_client()
    client.get.side_effect = IncusNotFoundException('not found')
    _run_info(module, client)
    module.exit_json.assert_called_once_with(storage_volumes=[])


def test_return_all_volumes() -> None:
    """Return all volumes."""
    module = _mock_module()
    client = mock_incus_client()
    client.get.return_value = {'metadata': [{'name': 'a'}, {'name': 'b'}]}
    _run_info(module, client)
    result = module.exit_json.call_args[1]['storage_volumes']
    assert len(result) == 2


def test_fail_on_volume_exception() -> None:
    """Fail on client exception."""
    module = _mock_module()
    client = mock_incus_client()
    client.get.side_effect = IncusClientException('connection refused')
    _run_info(module, client)
    module.fail_json.assert_called_once_with(msg='connection refused')
