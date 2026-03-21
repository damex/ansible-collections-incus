# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_certificate_info module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from ansible_collections.damex.incus.plugins.module_utils.incus import IncusClientException
from ansible_collections.damex.incus.plugins.modules.incus_certificate_info import main
from ansible_collections.damex.incus.tests.unit.conftest import (
    mock_incus_client,
    run_main,
)

__all__ = [
    'test_return_certificate_by_name',
    'test_return_empty_for_missing_certificate',
    'test_return_all_certificates',
    'test_fail_on_certificate_exception',
]

CERTS = [
    {'fingerprint': 'abc123', 'name': 'ansible', 'type': 'client', 'restricted': False},
    {'fingerprint': 'def456', 'name': 'ci', 'type': 'client', 'restricted': True},
]


@patch('ansible_collections.damex.incus.plugins.modules.incus_certificate_info.incus_create_client')
@patch('ansible_collections.damex.incus.plugins.modules.incus_certificate_info.incus_create_info_module')
def test_return_certificate_by_name(mock_create_module: MagicMock, mock_create_client: MagicMock) -> None:
    """Return certificate by name."""
    module = MagicMock()
    module.params = {'name': 'ansible'}
    client = mock_incus_client()
    client.get.return_value = {'metadata': CERTS}
    run_main(mock_create_module, mock_create_client, module, client, main)
    certs = module.exit_json.call_args[1]['certificates']
    assert len(certs) == 1
    assert certs[0]['fingerprint'] == 'abc123'


@patch('ansible_collections.damex.incus.plugins.modules.incus_certificate_info.incus_create_client')
@patch('ansible_collections.damex.incus.plugins.modules.incus_certificate_info.incus_create_info_module')
def test_return_empty_for_missing_certificate(mock_create_module: MagicMock, mock_create_client: MagicMock) -> None:
    """Return empty list for missing certificate."""
    module = MagicMock()
    module.params = {'name': 'missing'}
    client = mock_incus_client()
    client.get.return_value = {'metadata': CERTS}
    run_main(mock_create_module, mock_create_client, module, client, main)
    module.exit_json.assert_called_once_with(certificates=[])


@patch('ansible_collections.damex.incus.plugins.modules.incus_certificate_info.incus_create_client')
@patch('ansible_collections.damex.incus.plugins.modules.incus_certificate_info.incus_create_info_module')
def test_return_all_certificates(mock_create_module: MagicMock, mock_create_client: MagicMock) -> None:
    """Return all certificates."""
    module = MagicMock()
    module.params = {'name': None}
    client = mock_incus_client()
    client.get.return_value = {'metadata': CERTS}
    run_main(mock_create_module, mock_create_client, module, client, main)
    certs = module.exit_json.call_args[1]['certificates']
    assert len(certs) == 2


@patch('ansible_collections.damex.incus.plugins.modules.incus_certificate_info.incus_create_client')
@patch('ansible_collections.damex.incus.plugins.modules.incus_certificate_info.incus_create_info_module')
def test_fail_on_certificate_exception(mock_create_module: MagicMock, mock_create_client: MagicMock) -> None:
    """Fail on client exception."""
    module = MagicMock()
    module.params = {'name': None}
    client = mock_incus_client()
    client.get.side_effect = IncusClientException('connection refused')
    run_main(mock_create_module, mock_create_client, module, client, main)
    module.fail_json.assert_called_once_with(msg='connection refused')
