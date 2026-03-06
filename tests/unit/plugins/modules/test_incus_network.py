# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_network module."""

from __future__ import annotations

from unittest.mock import MagicMock

from ansible_collections.damex.incus.plugins.modules.incus_network import main
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
    'test_create_network_with_type',
    'test_skip_matching_network',
    'test_update_network_config',
    'test_delete_existing_network',
    'test_delete_nonexistent_network',
    'test_network_check_mode',
]

MODULE = 'ansible_collections.damex.incus.plugins.modules.incus_network'


def _mock_module(state: str = 'present', check_mode: bool = False) -> MagicMock:
    """Build mock module."""
    module = MagicMock()
    module.params = {
        **CONNECTION_PARAMS,
        'name': 'incusbr0',
        'state': state,
        'project': 'default',
        'description': '',
        'config': {},
        'type': 'bridge',
    }
    module.check_mode = check_mode
    return module


def test_update_network_config() -> None:
    """Update network with changed config."""
    module = _mock_module()
    module.params['config'] = {'ipv4.address': '10.0.0.1/24'}
    assert_write_update(main, MODULE, module, {'description': '', 'config': {}})


def test_create_network_with_type() -> None:
    """Create network with type."""
    result = assert_write_create(main, MODULE, _mock_module())
    assert result.post.call_args[0][1]['type'] == 'bridge'


def test_skip_matching_network() -> None:
    """Skip matching network."""
    assert_write_skip(main, MODULE, _mock_module(), {'description': '', 'config': {}})


def test_delete_existing_network() -> None:
    """Delete existing network."""
    assert_write_delete(main, MODULE, _mock_module(state='absent'))


def test_delete_nonexistent_network() -> None:
    """Skip delete for missing network."""
    assert_write_delete_missing(main, MODULE, _mock_module(state='absent'))


def test_network_check_mode() -> None:
    """Skip API calls in check mode."""
    assert_write_check_mode(main, MODULE, _mock_module(check_mode=True))
