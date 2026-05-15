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
    'test_create_network_zone_with_config',
    'test_skip_matching_network_zone_with_config',
    'test_skip_matching_network_zone',
    'test_update_network_zone_description',
    'test_update_network_zone_config',
    'test_delete_existing_network_zone',
    'test_delete_nonexistent_network_zone',
    'test_network_zone_check_mode',
]

MODULE = 'ansible_collections.damex.incus.plugins.modules.incus_network_zone'


def _mock_module(state: str = 'present', check_mode: bool = False) -> MagicMock:
    """Build mock module."""
    module = MagicMock()
    module.params = CONNECTION_PARAMS.copy()
    module.params['name'] = 'example.com'
    module.params['state'] = state
    module.params['project'] = 'default'
    module.params['description'] = ''
    module.params['config'] = {}
    module.check_mode = check_mode
    return module


def test_create_network_zone() -> None:
    """Create missing network zone."""
    assert_write_create(main, MODULE, _mock_module())


def test_create_network_zone_with_config() -> None:
    """Create network zone with user config key-value pairs."""
    module = _mock_module()
    module.params['config'] = [
        {'name': 'dns.nameservers', 'value': 'ns1.example.com'},
    ]
    client = assert_write_create(main, MODULE, module)
    _post_path, post_data = client.post.call_args.args
    assert post_data['config']['user.dns.nameservers'] == 'ns1.example.com'


def test_skip_matching_network_zone_with_config() -> None:
    """Skip matching network zone with user config."""
    module = _mock_module()
    module.params['config'] = [
        {'name': 'contact', 'value': 'admin@example.com'},
    ]
    assert_write_skip(main, MODULE, module, {
        'description': '',
        'config': {'user.contact': 'admin@example.com'},
    })


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


def test_update_network_zone_config() -> None:
    """Update network zone user config."""
    module = _mock_module()
    module.params['config'] = [
        {'name': 'contact', 'value': 'new@example.com'},
    ]
    put_data = assert_write_update(main, MODULE, module, {
        'description': '',
        'config': {'user.contact': 'old@example.com'},
    })
    assert put_data['config']['user.contact'] == 'new@example.com'


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
