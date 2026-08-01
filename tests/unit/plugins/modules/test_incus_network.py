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
    'test_create_network_with_bgp_peers',
    'test_create_network_with_unnumbered_bgp_peer',
    'test_update_network_with_bgp_peers',
    'test_skip_matching_network_with_bgp_peers',
    'test_create_network_with_tunnels',
    'test_update_network_with_tunnels',
    'test_skip_matching_network_with_tunnels',
    'test_create_network_with_target_filters_config',
    'test_update_network_with_target',
    'test_skip_matching_network_with_target',
    'test_create_network_with_target_filters_tunnel_keys',
]

MODULE = 'ansible_collections.damex.incus.plugins.modules.incus_network'


def _mock_module(state: str = 'present', check_mode: bool = False) -> MagicMock:
    """Build mock module."""
    module = MagicMock()
    module.params = CONNECTION_PARAMS.copy()
    module.params['name'] = 'incusbr0'
    module.params['state'] = state
    module.params['project'] = 'default'
    module.params['description'] = ''
    module.params['config'] = {}
    module.params['type'] = 'bridge'
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
    _post_path, post_data = result.post.call_args.args
    assert post_data['type'] == 'bridge'


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


def test_create_network_with_bgp_peers() -> None:
    """Create network with BGP peers merged into config."""
    module = _mock_module()
    module.params['config'] = {
        'bgp_peers': [
            {'name': 'router', 'address': '10.0.0.1', 'asn': 64601, 'holdtime': None, 'password': None},
        ],
    }
    client = assert_write_create(main, MODULE, module)
    _post_path, post_data = client.post.call_args.args
    assert post_data['config']['bgp.peers.router.address'] == '10.0.0.1'
    assert post_data['config']['bgp.peers.router.asn'] == '64601'


def test_create_network_with_unnumbered_bgp_peer() -> None:
    """Create network with interface-based BGP peer merged into config."""
    module = _mock_module()
    module.params['config'] = {
        'bgp_peers': [
            {
                'name': 'router',
                'address': None,
                'interface': 'uplink0',
                'asn': 64601,
                'holdtime': None,
                'password': None,
            },
        ],
    }
    client = assert_write_create(main, MODULE, module)
    _post_path, post_data = client.post.call_args.args
    assert post_data['config']['bgp.peers.router.interface'] == 'uplink0'
    assert post_data['config']['bgp.peers.router.asn'] == '64601'
    assert 'bgp.peers.router.address' not in post_data['config']


def test_update_network_with_bgp_peers() -> None:
    """Update network when BGP peers change."""
    module = _mock_module()
    module.params['config'] = {
        'bgp_peers': [
            {'name': 'router', 'address': '10.0.0.1', 'asn': 64601, 'holdtime': None, 'password': None},
        ],
    }
    assert_write_update(main, MODULE, module, {'description': '', 'config': {}})


def test_skip_matching_network_with_bgp_peers() -> None:
    """Skip update when BGP peers match current state."""
    module = _mock_module()
    module.params['config'] = {
        'bgp_peers': [
            {'name': 'router', 'address': '10.0.0.1', 'asn': 64601, 'holdtime': None, 'password': None},
        ],
    }
    current = {
        'description': '',
        'config': {
            'bgp.peers.router.address': '10.0.0.1',
            'bgp.peers.router.asn': '64601',
        },
    }
    assert_write_skip(main, MODULE, module, current)


def test_create_network_with_tunnels() -> None:
    """Create network with tunnels merged into config."""
    module = _mock_module()
    module.params['config'] = {
        'tunnels': [
            {'name': 'site2', 'protocol': 'vxlan', 'local': '192.168.1.1', 'remote': '192.168.1.2',
             'id': 100, 'group': None, 'port': None, 'interface': None, 'ttl': None},
        ],
    }
    client = assert_write_create(main, MODULE, module)
    _post_path, post_data = client.post.call_args.args
    assert post_data['config']['tunnel.site2.protocol'] == 'vxlan'
    assert post_data['config']['tunnel.site2.local'] == '192.168.1.1'
    assert post_data['config']['tunnel.site2.remote'] == '192.168.1.2'
    assert post_data['config']['tunnel.site2.id'] == '100'


def test_update_network_with_tunnels() -> None:
    """Update network when tunnels change."""
    module = _mock_module()
    module.params['config'] = {
        'tunnels': [
            {'name': 'site2', 'protocol': 'vxlan', 'local': '192.168.1.1', 'remote': '192.168.1.2',
             'id': None, 'group': None, 'port': None, 'interface': None, 'ttl': None},
        ],
    }
    assert_write_update(main, MODULE, module, {'description': '', 'config': {}})


def test_skip_matching_network_with_tunnels() -> None:
    """Skip update when tunnels match current state."""
    module = _mock_module()
    module.params['config'] = {
        'tunnels': [
            {'name': 'site2', 'protocol': 'vxlan', 'local': '192.168.1.1', 'remote': '192.168.1.2',
             'id': None, 'group': None, 'port': None, 'interface': None, 'ttl': None},
        ],
    }
    current = {
        'description': '',
        'config': {
            'tunnel.site2.protocol': 'vxlan',
            'tunnel.site2.local': '192.168.1.1',
            'tunnel.site2.remote': '192.168.1.2',
        },
    }
    assert_write_skip(main, MODULE, module, current)


def test_create_network_with_target_filters_config() -> None:
    """Create network with target keeps only node-specific config."""
    module = _mock_module()
    module.params['target'] = 'node1'
    module.params['config'] = {
        'parent': 'eth0',
        'ipv4.address': '10.0.0.1/24',
    }
    client = assert_write_create(main, MODULE, module)
    post_url, post_data = client.post.call_args.args
    assert post_data['config']['parent'] == 'eth0'
    assert 'ipv4.address' not in post_data['config']
    assert not post_data['description']
    assert 'target=node1' in post_url


def test_update_network_with_target() -> None:
    """Update node-specific network config with target."""
    module = _mock_module()
    module.params['target'] = 'node1'
    module.params['config'] = {
        'parent': 'eth1',
        'ipv4.address': '10.0.0.1/24',
    }
    current = {
        'description': '',
        'config': {'parent': 'eth0'},
    }
    put_data = assert_write_update(main, MODULE, module, current)
    assert put_data['config']['parent'] == 'eth1'
    assert 'ipv4.address' not in put_data['config']


def test_skip_matching_network_with_target() -> None:
    """Skip update when node-specific config matches with target."""
    module = _mock_module()
    module.params['target'] = 'node1'
    module.params['config'] = {'parent': 'eth0'}
    current = {
        'description': '',
        'config': {'parent': 'eth0'},
    }
    assert_write_skip(main, MODULE, module, current)


def test_create_network_with_target_filters_tunnel_keys() -> None:
    """Create network with target keeps only node-specific tunnel keys."""
    module = _mock_module()
    module.params['target'] = 'node1'
    module.params['config'] = {
        'tunnels': [
            {
                'name': 'site2',
                'protocol': 'vxlan',
                'local': '192.168.1.1',
                'remote': '192.168.1.2',
                'id': None,
                'group': None,
                'port': None,
                'interface': 'tun0',
                'ttl': None,
            },
        ],
    }
    client = assert_write_create(main, MODULE, module)
    post_url, post_data = client.post.call_args.args
    assert 'target=node1' in post_url
    assert post_data['config']['tunnel.site2.local'] == '192.168.1.1'
    assert post_data['config']['tunnel.site2.interface'] == 'tun0'
    assert 'tunnel.site2.protocol' not in post_data['config']
    assert 'tunnel.site2.remote' not in post_data['config']
