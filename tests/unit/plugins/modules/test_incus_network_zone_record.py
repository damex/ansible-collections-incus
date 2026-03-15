# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_network_zone_record module."""

from __future__ import annotations

from unittest.mock import MagicMock

from ansible_collections.damex.incus.plugins.modules.incus_network_zone_record import main
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
    'test_create_network_zone_record',
    'test_create_network_zone_record_with_entries',
    'test_create_includes_name',
    'test_skip_matching_network_zone_record',
    'test_skip_matching_network_zone_record_with_entries',
    'test_update_network_zone_record_entries',
    'test_delete_existing_network_zone_record',
    'test_delete_nonexistent_network_zone_record',
    'test_network_zone_record_check_mode',
    'test_entries_sorted_by_type_and_value',
    'test_entries_normalized_with_defaults',
]

MODULE = 'ansible_collections.damex.incus.plugins.modules.incus_network_zone_record'


def _mock_module(state: str = 'present', check_mode: bool = False) -> MagicMock:
    """Build mock module."""
    module = MagicMock()
    module.params = {
        **CONNECTION_PARAMS,
        'name': 'web',
        'zone': 'example.com',
        'state': state,
        'project': 'default',
        'description': '',
        'config': {},
        'entries': [],
    }
    module.check_mode = check_mode
    return module


def test_create_network_zone_record() -> None:
    """Create missing network zone record."""
    assert_write_create(main, MODULE, _mock_module())


def test_create_network_zone_record_with_entries() -> None:
    """Create network zone record with DNS entries."""
    module = _mock_module()
    module.params['entries'] = [
        {
            'type': 'A',
            'value': '10.0.0.5',
            'ttl': 0,
        },
    ]
    client = assert_write_create(main, MODULE, module)
    post_data = client.post.call_args[0][1]
    assert len(post_data['entries']) == 1
    assert post_data['entries'][0]['type'] == 'A'
    assert post_data['entries'][0]['value'] == '10.0.0.5'


def test_create_includes_name() -> None:
    """Verify name is included in create payload."""
    client = assert_write_create(main, MODULE, _mock_module())
    post_data = client.post.call_args[0][1]
    assert post_data['name'] == 'web'


def test_skip_matching_network_zone_record() -> None:
    """Skip matching network zone record."""
    assert_write_skip(main, MODULE, _mock_module(), {
        'description': '',
        'config': {},
        'entries': [],
    })


def test_skip_matching_network_zone_record_with_entries() -> None:
    """Skip matching network zone record with entries."""
    module = _mock_module()
    module.params['entries'] = [
        {
            'type': 'A',
            'value': '10.0.0.5',
            'ttl': 300,
        },
    ]
    current = {
        'description': '',
        'config': {},
        'entries': [
            {
                'type': 'A',
                'value': '10.0.0.5',
                'ttl': 300,
            },
        ],
    }
    assert_write_skip(main, MODULE, module, current)


def test_update_network_zone_record_entries() -> None:
    """Update network zone record when entries change."""
    module = _mock_module()
    module.params['entries'] = [
        {
            'type': 'A',
            'value': '10.0.0.10',
            'ttl': 0,
        },
    ]
    put_data = assert_write_update(main, MODULE, module, {
        'description': '',
        'config': {},
        'entries': [
            {
                'type': 'A',
                'value': '10.0.0.5',
                'ttl': 0,
            },
        ],
    })
    assert len(put_data['entries']) == 1
    assert put_data['entries'][0]['value'] == '10.0.0.10'


def test_delete_existing_network_zone_record() -> None:
    """Delete existing network zone record."""
    assert_write_delete(main, MODULE, _mock_module(state='absent'), {
        'description': '',
        'config': {},
        'entries': [],
    })


def test_delete_nonexistent_network_zone_record() -> None:
    """Skip delete for missing network zone record."""
    assert_write_delete_missing(main, MODULE, _mock_module(state='absent'))


def test_network_zone_record_check_mode() -> None:
    """Skip API calls in check mode."""
    assert_write_check_mode(main, MODULE, _mock_module(check_mode=True))


def test_entries_sorted_by_type_and_value() -> None:
    """Verify entries are sorted by type and value."""
    module = _mock_module()
    module.params['entries'] = [
        {
            'type': 'AAAA',
            'value': 'fd42::10',
            'ttl': 0,
        },
        {
            'type': 'A',
            'value': '10.0.0.5',
            'ttl': 0,
        },
    ]
    client = assert_write_create(main, MODULE, module)
    post_data = client.post.call_args[0][1]
    assert post_data['entries'][0]['type'] == 'A'
    assert post_data['entries'][1]['type'] == 'AAAA'


def test_entries_normalized_with_defaults() -> None:
    """Verify entries get default values for missing fields."""
    module = _mock_module()
    module.params['entries'] = [
        {
            'type': 'A',
            'value': '10.0.0.5',
            'ttl': None,
        },
    ]
    client = assert_write_create(main, MODULE, module)
    post_data = client.post.call_args[0][1]
    entry = post_data['entries'][0]
    assert not entry['ttl']
    assert entry['type'] == 'A'
    assert entry['value'] == '10.0.0.5'
