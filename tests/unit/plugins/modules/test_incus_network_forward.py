# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_network_forward module."""

from __future__ import annotations

from unittest.mock import MagicMock

from ansible_collections.damex.incus.plugins.modules.incus_network_forward import main
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
    'test_create_network_forward',
    'test_create_network_forward_with_ports',
    'test_create_includes_listen_address',
    'test_skip_matching_network_forward',
    'test_skip_matching_network_forward_with_ports',
    'test_update_network_forward_description',
    'test_update_network_forward_ports',
    'test_delete_existing_network_forward',
    'test_delete_nonexistent_network_forward',
    'test_network_forward_check_mode',
    'test_ports_normalized_with_defaults',
]

MODULE = 'ansible_collections.damex.incus.plugins.modules.incus_network_forward'


def _mock_module(state: str = 'present', check_mode: bool = False) -> MagicMock:
    """Build mock module."""
    module = MagicMock()
    module.params = {
        **CONNECTION_PARAMS,
        'name': '192.168.1.100',
        'network': 'incusbr0',
        'state': state,
        'project': 'default',
        'description': '',
        'config': {},
        'ports': [],
    }
    module.check_mode = check_mode
    return module


def test_create_network_forward() -> None:
    """Create missing network forward."""
    assert_write_create(main, MODULE, _mock_module())


def test_create_network_forward_with_ports() -> None:
    """Create network forward with port rules."""
    module = _mock_module()
    module.params['ports'] = [
        {
            'protocol': 'tcp',
            'listen_port': '80',
            'target_address': '10.0.0.5',
            'target_port': '',
            'description': 'HTTP',
            'snat': False,
        },
    ]
    client = assert_write_create(main, MODULE, module)
    post_data = client.post.call_args[0][1]
    assert len(post_data['ports']) == 1
    assert post_data['ports'][0]['protocol'] == 'tcp'
    assert post_data['ports'][0]['listen_port'] == '80'
    assert post_data['ports'][0]['target_address'] == '10.0.0.5'


def test_create_includes_listen_address() -> None:
    """Verify listen_address is included in create payload."""
    client = assert_write_create(main, MODULE, _mock_module())
    post_data = client.post.call_args[0][1]
    assert post_data['listen_address'] == '192.168.1.100'


def test_skip_matching_network_forward() -> None:
    """Skip matching network forward."""
    assert_write_skip(main, MODULE, _mock_module(), {
        'description': '',
        'config': {},
        'ports': [],
    })


def test_skip_matching_network_forward_with_ports() -> None:
    """Skip matching network forward with ports."""
    module = _mock_module()
    module.params['ports'] = [
        {
            'protocol': 'tcp',
            'listen_port': '443',
            'target_address': '10.0.0.5',
            'target_port': '8443',
            'description': '',
            'snat': False,
        },
    ]
    current = {
        'description': '',
        'config': {},
        'ports': [
            {
                'protocol': 'tcp',
                'listen_port': '443',
                'target_address': '10.0.0.5',
                'target_port': '8443',
                'description': '',
                'snat': False,
            },
        ],
    }
    assert_write_skip(main, MODULE, module, current)


def test_update_network_forward_description() -> None:
    """Update network forward with changed description."""
    module = _mock_module()
    module.params['description'] = 'Updated forward'
    assert_write_update(main, MODULE, module, {
        'description': 'Old forward',
        'config': {},
        'ports': [],
    })


def test_update_network_forward_ports() -> None:
    """Update network forward when ports change."""
    module = _mock_module()
    module.params['ports'] = [
        {
            'protocol': 'tcp',
            'listen_port': '80',
            'target_address': '10.0.0.5',
            'target_port': '',
            'description': '',
            'snat': False,
        },
    ]
    put_data = assert_write_update(main, MODULE, module, {
        'description': '',
        'config': {},
        'ports': [],
    })
    assert len(put_data['ports']) == 1
    assert put_data['ports'][0]['listen_port'] == '80'


def test_delete_existing_network_forward() -> None:
    """Delete existing network forward."""
    assert_write_delete(main, MODULE, _mock_module(state='absent'), {
        'description': '',
        'config': {},
        'ports': [],
    })


def test_delete_nonexistent_network_forward() -> None:
    """Skip delete for missing network forward."""
    assert_write_delete_missing(main, MODULE, _mock_module(state='absent'))


def test_network_forward_check_mode() -> None:
    """Skip API calls in check mode."""
    assert_write_check_mode(main, MODULE, _mock_module(check_mode=True))


def test_ports_normalized_with_defaults() -> None:
    """Verify ports get default values for missing fields."""
    module = _mock_module()
    module.params['ports'] = [
        {
            'protocol': 'udp',
            'listen_port': '53',
            'target_address': '10.0.0.10',
            'target_port': None,
            'description': None,
            'snat': None,
        },
    ]
    client = assert_write_create(main, MODULE, module)
    post_data = client.post.call_args[0][1]
    port = post_data['ports'][0]
    assert not port['target_port']
    assert not port['description']
    assert port['snat'] is False
