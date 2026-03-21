# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_network_zone_record_info module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    IncusClientException,
    IncusNotFoundException,
)
from ansible_collections.damex.incus.plugins.modules.incus_network_zone_record_info import main

__all__ = [
    'test_return_record_by_name',
    'test_return_empty_for_missing_record',
    'test_return_all_records',
    'test_fail_on_record_exception',
]

MODULE = 'ansible_collections.damex.incus.plugins.modules.incus_network_zone_record_info'
UTILS = 'ansible_collections.damex.incus.plugins.module_utils.incus'


def _mock_module(name: str | None = None) -> MagicMock:
    """Build mock info module."""
    module = MagicMock()
    module.params = {
        'zone': 'example.com',
        'name': name,
        'project': 'default',
    }
    return module


def _run_info(module: MagicMock, client: MagicMock) -> None:
    """Patch module creation and run main."""
    with patch(f'{MODULE}.incus_create_info_module', return_value=module), \
         patch(f'{UTILS}.incus_create_client', return_value=client):
        main()


def test_return_record_by_name() -> None:
    """Return record by name."""
    module = _mock_module(name='web')
    client = MagicMock()
    client.__enter__ = MagicMock(return_value=client)
    client.__exit__ = MagicMock(return_value=False)
    client.get.return_value = {
        'metadata': {'name': 'web', 'description': '', 'entries': []},
    }
    _run_info(module, client)
    result = module.exit_json.call_args[1]['network_zone_records']
    assert len(result) == 1
    assert result[0]['name'] == 'web'


def test_return_empty_for_missing_record() -> None:
    """Return empty list for missing record."""
    module = _mock_module(name='missing')
    client = MagicMock()
    client.__enter__ = MagicMock(return_value=client)
    client.__exit__ = MagicMock(return_value=False)
    client.get.side_effect = IncusNotFoundException('not found')
    _run_info(module, client)
    module.exit_json.assert_called_once_with(network_zone_records=[])


def test_return_all_records() -> None:
    """Return all records."""
    module = _mock_module()
    client = MagicMock()
    client.__enter__ = MagicMock(return_value=client)
    client.__exit__ = MagicMock(return_value=False)
    client.get.return_value = {
        'metadata': [
            {'name': 'web'},
            {'name': 'mail'},
        ],
    }
    _run_info(module, client)
    result = module.exit_json.call_args[1]['network_zone_records']
    assert len(result) == 2


def test_fail_on_record_exception() -> None:
    """Fail on client exception."""
    module = _mock_module()
    client = MagicMock()
    client.__enter__ = MagicMock(return_value=client)
    client.__exit__ = MagicMock(return_value=False)
    client.get.side_effect = IncusClientException('connection refused')
    _run_info(module, client)
    module.fail_json.assert_called_once_with(msg='connection refused')
