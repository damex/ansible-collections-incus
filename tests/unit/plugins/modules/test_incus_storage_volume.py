# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_storage_volume module."""

from __future__ import annotations

from unittest.mock import MagicMock

from ansible_collections.damex.incus.plugins.modules.incus_storage_volume import main
from ansible_collections.damex.incus.tests.unit.conftest import (
    CONNECTION_PARAMS,
    assert_write_create,
    assert_write_skip,
    assert_write_update,
    assert_write_delete,
    assert_write_delete_missing,
    assert_write_check_mode,
)

__all__ = [
    'test_create_volume_with_content_type',
    'test_skip_matching_volume',
    'test_update_volume_config',
    'test_delete_existing_volume',
    'test_delete_nonexistent_volume',
    'test_volume_check_mode',
    'test_create_volume_block_type',
    'test_create_volume_with_target',
    'test_skip_update_with_target',
]

MODULE = 'ansible_collections.damex.incus.plugins.modules.incus_storage_volume'


def _mock_module(state: str = 'present', check_mode: bool = False) -> MagicMock:
    """Build mock module."""
    module = MagicMock()
    module.params = {
        **CONNECTION_PARAMS,
        'name': 'data',
        'pool': 'default',
        'state': state,
        'project': 'default',
        'target': None,
        'content_type': 'filesystem',
        'description': '',
        'config': {},
    }
    module.check_mode = check_mode
    return module


def test_create_volume_with_content_type() -> None:
    """Create volume with content_type in payload."""
    client = assert_write_create(main, MODULE, _mock_module())
    post_data = client.post.call_args[0][1]
    assert post_data['content_type'] == 'filesystem'
    assert post_data['name'] == 'data'


def test_skip_matching_volume() -> None:
    """Skip matching volume."""
    assert_write_skip(main, MODULE, _mock_module(), {'description': '', 'config': {}})


def test_update_volume_config() -> None:
    """Update volume with changed config."""
    module = _mock_module()
    module.params['config'] = {'size': '50GiB'}
    assert_write_update(main, MODULE, module, {'description': '', 'config': {}})


def test_delete_existing_volume() -> None:
    """Delete existing volume."""
    assert_write_delete(main, MODULE, _mock_module(state='absent'))


def test_delete_nonexistent_volume() -> None:
    """Skip delete for missing volume."""
    assert_write_delete_missing(main, MODULE, _mock_module(state='absent'))


def test_volume_check_mode() -> None:
    """Skip API calls in check mode."""
    assert_write_check_mode(main, MODULE, _mock_module(check_mode=True))


def test_create_volume_block_type() -> None:
    """Create block volume with correct content_type."""
    module = _mock_module()
    module.params['content_type'] = 'block'
    client = assert_write_create(main, MODULE, module)
    post_data = client.post.call_args[0][1]
    assert post_data['content_type'] == 'block'


def test_create_volume_with_target() -> None:
    """Create volume with target in API path."""
    module = _mock_module()
    module.params['target'] = 'node1'
    client = assert_write_create(main, MODULE, module)
    post_url = client.post.call_args[0][0]
    assert 'target=node1' in post_url


def test_skip_update_with_target() -> None:
    """Skip update when target is set on existing volume."""
    module = _mock_module()
    module.params['target'] = 'node1'
    assert_write_skip(main, MODULE, module, {'description': '', 'config': {}})
