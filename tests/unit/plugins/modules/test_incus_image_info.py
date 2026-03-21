# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_image_info module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from ansible_collections.damex.incus.plugins.module_utils.incus_client import (
    IncusClientException,
    IncusNotFoundException,
)
from ansible_collections.damex.incus.plugins.modules.incus_image_info import main
from ansible_collections.damex.incus.tests.unit.conftest import (
    mock_incus_client,
    run_main,
)

__all__ = [
    'test_return_image_by_alias',
    'test_return_empty_for_missing_alias',
    'test_return_all_images',
    'test_return_empty_for_no_fingerprint',
    'test_fail_on_client_exception',
]


def _mock_info_module(name: str | None = 'debian/13') -> MagicMock:
    """Build mock info module."""
    module = MagicMock()
    module.params = {'name': name, 'project': 'default'}
    return module


@patch('ansible_collections.damex.incus.plugins.modules.incus_image_info.incus_create_client')
@patch('ansible_collections.damex.incus.plugins.modules.incus_image_info.incus_create_info_module')
def test_return_image_by_alias(mock_create_module: MagicMock, mock_create_client: MagicMock) -> None:
    """Return image by alias."""
    module = _mock_info_module()
    client = mock_incus_client()
    client.get.side_effect = [
        {'metadata': {'name': 'debian/13', 'target': 'abc123'}},
        {'metadata': {'fingerprint': 'abc123', 'type': 'container'}},
    ]
    run_main(mock_create_module, mock_create_client, module, client, main)
    module.exit_json.assert_called_once()
    images = module.exit_json.call_args[1]['images']
    assert len(images) == 1
    assert images[0]['fingerprint'] == 'abc123'


@patch('ansible_collections.damex.incus.plugins.modules.incus_image_info.incus_create_client')
@patch('ansible_collections.damex.incus.plugins.modules.incus_image_info.incus_create_info_module')
def test_return_empty_for_missing_alias(mock_create_module: MagicMock, mock_create_client: MagicMock) -> None:
    """Return empty list for missing alias."""
    module = _mock_info_module('missing')
    client = mock_incus_client()
    client.get.side_effect = IncusNotFoundException('not found')
    run_main(mock_create_module, mock_create_client, module, client, main)
    module.exit_json.assert_called_once_with(images=[])


@patch('ansible_collections.damex.incus.plugins.modules.incus_image_info.incus_create_client')
@patch('ansible_collections.damex.incus.plugins.modules.incus_image_info.incus_create_info_module')
def test_return_all_images(mock_create_module: MagicMock, mock_create_client: MagicMock) -> None:
    """Return all images."""
    module = _mock_info_module(name=None)
    client = mock_incus_client()
    client.get.return_value = {'metadata': [{'fingerprint': 'a'}, {'fingerprint': 'b'}]}
    run_main(mock_create_module, mock_create_client, module, client, main)
    images = module.exit_json.call_args[1]['images']
    assert len(images) == 2


@patch('ansible_collections.damex.incus.plugins.modules.incus_image_info.incus_create_client')
@patch('ansible_collections.damex.incus.plugins.modules.incus_image_info.incus_create_info_module')
def test_return_empty_for_no_fingerprint(mock_create_module: MagicMock, mock_create_client: MagicMock) -> None:
    """Return empty list when alias has no fingerprint."""
    module = _mock_info_module('broken')
    client = mock_incus_client()
    client.get.return_value = {'metadata': {'name': 'broken', 'target': None}}
    run_main(mock_create_module, mock_create_client, module, client, main)
    module.exit_json.assert_called_once_with(images=[])


@patch('ansible_collections.damex.incus.plugins.modules.incus_image_info.incus_create_client')
@patch('ansible_collections.damex.incus.plugins.modules.incus_image_info.incus_create_info_module')
def test_fail_on_client_exception(mock_create_module: MagicMock, mock_create_client: MagicMock) -> None:
    """Fail on client exception."""
    module = _mock_info_module(name=None)
    client = mock_incus_client()
    client.get.side_effect = IncusClientException('connection refused')
    run_main(mock_create_module, mock_create_client, module, client, main)
    module.fail_json.assert_called_once_with(msg='connection refused')
