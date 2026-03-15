# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_network_address_set module."""

from __future__ import annotations

from unittest.mock import MagicMock

from ansible_collections.damex.incus.plugins.modules.incus_network_address_set import main
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
    'test_create_network_address_set',
    'test_create_network_address_set_with_addresses',
    'test_skip_matching_network_address_set',
    'test_skip_matching_network_address_set_with_addresses',
    'test_update_network_address_set_description',
    'test_update_network_address_set_addresses',
    'test_delete_existing_network_address_set',
    'test_delete_nonexistent_network_address_set',
    'test_network_address_set_check_mode',
    'test_addresses_sorted',
]

MODULE = 'ansible_collections.damex.incus.plugins.modules.incus_network_address_set'


def _mock_module(state: str = 'present', check_mode: bool = False) -> MagicMock:
    """Build mock module."""
    module = MagicMock()
    module.params = {
        **CONNECTION_PARAMS,
        'name': 'web_servers',
        'state': state,
        'project': 'default',
        'description': '',
        'config': {},
        'addresses': [],
    }
    module.check_mode = check_mode
    return module


def test_create_network_address_set() -> None:
    """Create missing network address set."""
    assert_write_create(main, MODULE, _mock_module())


def test_create_network_address_set_with_addresses() -> None:
    """Create network address set with addresses."""
    module = _mock_module()
    module.params['addresses'] = ['10.0.0.5', '10.0.0.6']
    client = assert_write_create(main, MODULE, module)
    post_data = client.post.call_args[0][1]
    assert len(post_data['addresses']) == 2
    assert '10.0.0.5' in post_data['addresses']
    assert '10.0.0.6' in post_data['addresses']


def test_skip_matching_network_address_set() -> None:
    """Skip matching network address set."""
    assert_write_skip(main, MODULE, _mock_module(), {
        'description': '',
        'config': {},
        'addresses': [],
    })


def test_skip_matching_network_address_set_with_addresses() -> None:
    """Skip matching network address set with addresses."""
    module = _mock_module()
    module.params['addresses'] = ['10.0.0.5', '2001:db8::1']
    current = {
        'description': '',
        'config': {},
        'addresses': ['10.0.0.5', '2001:db8::1'],
    }
    assert_write_skip(main, MODULE, module, current)


def test_update_network_address_set_description() -> None:
    """Update network address set with changed description."""
    module = _mock_module()
    module.params['description'] = 'Updated set'
    assert_write_update(main, MODULE, module, {
        'description': 'Old set',
        'config': {},
        'addresses': [],
    })


def test_update_network_address_set_addresses() -> None:
    """Update network address set when addresses change."""
    module = _mock_module()
    module.params['addresses'] = ['10.0.0.5', '10.0.0.6']
    put_data = assert_write_update(main, MODULE, module, {
        'description': '',
        'config': {},
        'addresses': ['10.0.0.5'],
    })
    assert len(put_data['addresses']) == 2


def test_delete_existing_network_address_set() -> None:
    """Delete existing network address set."""
    assert_write_delete(main, MODULE, _mock_module(state='absent'), {
        'description': '',
        'config': {},
        'addresses': [],
    })


def test_delete_nonexistent_network_address_set() -> None:
    """Skip delete for missing network address set."""
    assert_write_delete_missing(main, MODULE, _mock_module(state='absent'))


def test_network_address_set_check_mode() -> None:
    """Skip API calls in check mode."""
    assert_write_check_mode(main, MODULE, _mock_module(check_mode=True))


def test_addresses_sorted() -> None:
    """Verify addresses are sorted for stable comparison."""
    module = _mock_module()
    module.params['addresses'] = ['10.0.0.6', '10.0.0.5', '2001:db8::1']
    client = assert_write_create(main, MODULE, module)
    post_data = client.post.call_args[0][1]
    assert post_data['addresses'] == ['10.0.0.5', '10.0.0.6', '2001:db8::1']
