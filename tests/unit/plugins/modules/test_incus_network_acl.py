# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_network_acl module."""

from __future__ import annotations

from unittest.mock import MagicMock

from ansible_collections.damex.incus.plugins.modules.incus_network_acl import main
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
    'test_create_network_acl',
    'test_create_network_acl_with_rules',
    'test_skip_matching_network_acl',
    'test_skip_matching_network_acl_with_rules',
    'test_update_network_acl_description',
    'test_update_network_acl_rules',
    'test_delete_existing_network_acl',
    'test_delete_nonexistent_network_acl',
    'test_network_acl_check_mode',
    'test_rules_sorted_by_action_priority',
    'test_rules_normalized_with_defaults',
]

MODULE = 'ansible_collections.damex.incus.plugins.modules.incus_network_acl'


def _mock_module(state: str = 'present', check_mode: bool = False) -> MagicMock:
    """Build mock module."""
    module = MagicMock()
    module.params = {
        **CONNECTION_PARAMS,
        'name': 'web',
        'state': state,
        'project': 'default',
        'description': '',
        'config': {},
        'ingress': [],
        'egress': [],
    }
    module.check_mode = check_mode
    return module


def test_create_network_acl() -> None:
    """Create missing network ACL."""
    assert_write_create(main, MODULE, _mock_module())


def test_create_network_acl_with_rules() -> None:
    """Create network ACL with ingress and egress rules."""
    module = _mock_module()
    module.params['ingress'] = [
        {
            'action': 'allow',
            'state': 'enabled',
            'description': 'Allow HTTP',
            'source': '@internal',
            'destination': '',
            'protocol': 'tcp',
            'source_port': '',
            'destination_port': '80',
            'icmp_type': '',
            'icmp_code': '',
        },
    ]
    module.params['egress'] = [
        {
            'action': 'allow',
            'state': 'enabled',
            'description': 'Allow DNS',
            'source': '',
            'destination': '8.8.8.8/32',
            'protocol': 'udp',
            'source_port': '',
            'destination_port': '53',
            'icmp_type': '',
            'icmp_code': '',
        },
    ]
    client = assert_write_create(main, MODULE, module)
    post_data = client.post.call_args[0][1]
    assert len(post_data['ingress']) == 1
    assert post_data['ingress'][0]['action'] == 'allow'
    assert post_data['ingress'][0]['protocol'] == 'tcp'
    assert post_data['ingress'][0]['destination_port'] == '80'
    assert len(post_data['egress']) == 1
    assert post_data['egress'][0]['destination'] == '8.8.8.8/32'


def test_skip_matching_network_acl() -> None:
    """Skip matching network ACL."""
    assert_write_skip(main, MODULE, _mock_module(), {
        'description': '',
        'config': {},
        'ingress': [],
        'egress': [],
    })


def test_skip_matching_network_acl_with_rules() -> None:
    """Skip matching network ACL with rules."""
    module = _mock_module()
    module.params['ingress'] = [
        {
            'action': 'drop',
            'state': 'enabled',
            'description': '',
            'source': '',
            'destination': '',
            'protocol': '',
            'source_port': '',
            'destination_port': '',
            'icmp_type': '',
            'icmp_code': '',
        },
    ]
    current = {
        'description': '',
        'config': {},
        'ingress': [
            {
                'action': 'drop',
                'state': 'enabled',
            },
        ],
        'egress': [],
    }
    assert_write_skip(main, MODULE, module, current)


def test_update_network_acl_description() -> None:
    """Update network ACL with changed description."""
    module = _mock_module()
    module.params['description'] = 'Updated ACL'
    assert_write_update(main, MODULE, module, {
        'description': 'Old ACL',
        'config': {},
        'ingress': [],
        'egress': [],
    })


def test_update_network_acl_rules() -> None:
    """Update network ACL when rules change."""
    module = _mock_module()
    module.params['ingress'] = [
        {
            'action': 'allow',
            'state': 'enabled',
            'description': '',
            'source': '@internal',
            'destination': '',
            'protocol': 'tcp',
            'source_port': '',
            'destination_port': '443',
            'icmp_type': '',
            'icmp_code': '',
        },
    ]
    put_data = assert_write_update(main, MODULE, module, {
        'description': '',
        'config': {},
        'ingress': [],
        'egress': [],
    })
    assert len(put_data['ingress']) == 1
    assert put_data['ingress'][0]['destination_port'] == '443'


def test_delete_existing_network_acl() -> None:
    """Delete existing network ACL."""
    assert_write_delete(main, MODULE, _mock_module(state='absent'), {
        'description': '',
        'config': {},
        'ingress': [],
        'egress': [],
    })


def test_delete_nonexistent_network_acl() -> None:
    """Skip delete for missing network ACL."""
    assert_write_delete_missing(main, MODULE, _mock_module(state='absent'))


def test_network_acl_check_mode() -> None:
    """Skip API calls in check mode."""
    assert_write_check_mode(main, MODULE, _mock_module(check_mode=True))


def test_rules_sorted_by_action_priority() -> None:
    """Verify rules are sorted by action priority."""
    module = _mock_module()
    module.params['ingress'] = [
        {
            'action': 'allow',
            'state': 'enabled',
            'description': 'Allow all',
            'source': '',
            'destination': '',
            'protocol': '',
            'source_port': '',
            'destination_port': '',
            'icmp_type': '',
            'icmp_code': '',
        },
        {
            'action': 'drop',
            'state': 'enabled',
            'description': 'Drop bad',
            'source': '10.0.0.0/8',
            'destination': '',
            'protocol': '',
            'source_port': '',
            'destination_port': '',
            'icmp_type': '',
            'icmp_code': '',
        },
    ]
    client = assert_write_create(main, MODULE, module)
    post_data = client.post.call_args[0][1]
    assert post_data['ingress'][0]['action'] == 'drop'
    assert post_data['ingress'][1]['action'] == 'allow'


def test_rules_normalized_with_defaults() -> None:
    """Verify rules get default values for missing fields."""
    module = _mock_module()
    module.params['egress'] = [
        {
            'action': 'reject',
            'state': None,
            'description': None,
            'source': None,
            'destination': None,
            'protocol': None,
            'source_port': None,
            'destination_port': None,
            'icmp_type': None,
            'icmp_code': None,
        },
    ]
    client = assert_write_create(main, MODULE, module)
    post_data = client.post.call_args[0][1]
    rule = post_data['egress'][0]
    assert rule['state'] == 'enabled'
    assert 'description' not in rule
    assert 'source' not in rule
    assert 'protocol' not in rule
