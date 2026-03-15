# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_network_zone module."""

from __future__ import annotations

from unittest.mock import MagicMock

from ansible_collections.damex.incus.plugins.modules.incus_network_zone import main
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
    'test_create_network_zone',
    'test_skip_matching_network_zone',
    'test_update_network_zone_description',
    'test_delete_existing_network_zone',
    'test_delete_nonexistent_network_zone',
    'test_network_zone_check_mode',
]

MODULE = 'ansible_collections.damex.incus.plugins.modules.incus_network_zone'


def _mock_module(state: str = 'present', check_mode: bool = False) -> MagicMock:
    """Build mock module."""
    module = MagicMock()
    module.params = {
        **CONNECTION_PARAMS,
        'name': 'example.com',
        'state': state,
        'project': 'default',
        'description': '',
        'config': {},
    }
    module.check_mode = check_mode
    return module


def test_create_network_zone() -> None:
    """Create missing network zone."""
    assert_write_create(main, MODULE, _mock_module())


def test_skip_matching_network_zone() -> None:
    """Skip matching network zone."""
    assert_write_skip(main, MODULE, _mock_module(), {
        'description': '',
        'config': {},
    })


def test_update_network_zone_description() -> None:
    """Update network zone with changed description."""
    module = _mock_module()
    module.params['description'] = 'Updated zone'
    assert_write_update(main, MODULE, module, {
        'description': 'Old zone',
        'config': {},
    })


def test_delete_existing_network_zone() -> None:
    """Delete existing network zone."""
    assert_write_delete(main, MODULE, _mock_module(state='absent'), {
        'description': '',
        'config': {},
    })


def test_delete_nonexistent_network_zone() -> None:
    """Skip delete for missing network zone."""
    assert_write_delete_missing(main, MODULE, _mock_module(state='absent'))


def test_network_zone_check_mode() -> None:
    """Skip API calls in check mode."""
    assert_write_check_mode(main, MODULE, _mock_module(check_mode=True))
