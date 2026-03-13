# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for cloud-init utilities."""

from __future__ import annotations

from ansible_collections.damex.incus.plugins.module_utils.cloud_init import (
    cloud_init_data_lists_to_dicts,
    cloud_init_interface_options,
    cloud_init_named_list_to_dict,
    cloud_init_named_list_to_scalar_dict,
)

__all__ = [
    'test_cloud_init_named_list_to_dict_single',
    'test_cloud_init_named_list_to_dict_multiple',
    'test_cloud_init_named_list_to_dict_empty',
    'test_cloud_init_named_list_to_scalar_dict_value',
    'test_cloud_init_named_list_to_scalar_dict_selection',
    'test_cloud_init_data_lists_to_dicts_disk_setup',
    'test_cloud_init_data_lists_to_dicts_sources',
    'test_cloud_init_data_lists_to_dicts_debconf',
    'test_cloud_init_data_lists_to_dicts_headers',
    'test_cloud_init_data_lists_to_dicts_passthrough',
    'test_cloud_init_data_lists_to_dicts_nested_recursion',
    'test_cloud_init_data_lists_to_dicts_multiple',
    'test_cloud_init_data_lists_to_dicts_ethernets',
    'test_cloud_init_data_lists_to_dicts_bonds',
    'test_cloud_init_data_lists_to_dicts_bridges',
    'test_cloud_init_data_lists_to_dicts_vlans',
    'test_cloud_init_data_lists_to_dicts_list_recursion',
    'test_cloud_init_interface_options_base_keys',
    'test_cloud_init_interface_options_extra_keys',
]


def test_cloud_init_named_list_to_dict_single() -> None:
    """Transform single named dict."""
    result = cloud_init_named_list_to_dict([
        {'name': '/dev/vdb', 'table_type': 'gpt', 'layout': True},
    ])
    assert result == {'/dev/vdb': {'table_type': 'gpt', 'layout': True}}


def test_cloud_init_named_list_to_dict_multiple() -> None:
    """Transform multiple named dicts."""
    result = cloud_init_named_list_to_dict([
        {'name': 'eth0', 'dhcp4': True},
        {'name': 'eth1', 'dhcp4': False, 'addresses': ['10.0.0.2/24']},
    ])
    assert result == {
        'eth0': {'dhcp4': True},
        'eth1': {'dhcp4': False, 'addresses': ['10.0.0.2/24']},
    }


def test_cloud_init_named_list_to_dict_empty() -> None:
    """Return empty dict for empty list."""
    assert not cloud_init_named_list_to_dict([])


def test_cloud_init_named_list_to_scalar_dict_value() -> None:
    """Transform name/value pair."""
    result = cloud_init_named_list_to_scalar_dict([
        {'name': 'Authorization', 'value': 'Bearer token123'},
    ])
    assert result == {'Authorization': 'Bearer token123'}


def test_cloud_init_named_list_to_scalar_dict_selection() -> None:
    """Transform name/selection pair."""
    result = cloud_init_named_list_to_scalar_dict([
        {'name': 'my_sel', 'selection': 'mysql mysql-server/root_password password s3cr3t'},
    ])
    assert result == {'my_sel': 'mysql mysql-server/root_password password s3cr3t'}


def test_cloud_init_data_lists_to_dicts_disk_setup() -> None:
    """Transform disk_setup named list."""
    data = {'disk_setup': [{'name': '/dev/vdb', 'table_type': 'gpt'}]}
    result = cloud_init_data_lists_to_dicts(data)
    assert result == {'disk_setup': {'/dev/vdb': {'table_type': 'gpt'}}}


def test_cloud_init_data_lists_to_dicts_sources() -> None:
    """Transform apt sources named list."""
    data = {
        'apt': {
            'sources': [
                {'name': 'my-repo', 'source': 'deb http://example.com stable main'},
            ],
        },
    }
    result = cloud_init_data_lists_to_dicts(data)
    assert result['apt']['sources'] == {
        'my-repo': {'source': 'deb http://example.com stable main'},
    }


def test_cloud_init_data_lists_to_dicts_debconf() -> None:
    """Transform debconf_selections to scalar dict."""
    data = {
        'apt': {
            'debconf_selections': [
                {'name': 'sel1', 'selection': 'pkg pkg/q string val'},
            ],
        },
    }
    result = cloud_init_data_lists_to_dicts(data)
    assert result['apt']['debconf_selections'] == {'sel1': 'pkg pkg/q string val'}


def test_cloud_init_data_lists_to_dicts_headers() -> None:
    """Transform headers to scalar dict."""
    data = {
        'write_files': [{
            'path': '/etc/f',
            'source': {
                'uri': 'https://example.com',
                'headers': [{'name': 'Auth', 'value': 'Bearer tok'}],
            },
        }],
    }
    result = cloud_init_data_lists_to_dicts(data)
    assert result['write_files'][0]['source']['headers'] == {'Auth': 'Bearer tok'}


def test_cloud_init_data_lists_to_dicts_passthrough() -> None:
    """Return non-collection values unchanged."""
    assert cloud_init_data_lists_to_dicts('hello') == 'hello'
    assert cloud_init_data_lists_to_dicts(42) == 42
    assert cloud_init_data_lists_to_dicts(True) is True


def test_cloud_init_data_lists_to_dicts_nested_recursion() -> None:
    """Recurse into nested dicts without transform keys."""
    data = {'ntp': {'enabled': True, 'servers': ['ntp.example.com']}}
    result = cloud_init_data_lists_to_dicts(data)
    assert result == data


def test_cloud_init_data_lists_to_dicts_multiple() -> None:
    """Transform multiple named lists in one pass."""
    data = {
        'disk_setup': [{'name': '/dev/vdb', 'table_type': 'gpt'}],
        'apt': {
            'sources': [{'name': 'repo', 'source': 'deb http://x main'}],
            'debconf_selections': [{'name': 's1', 'selection': 'val'}],
        },
    }
    result = cloud_init_data_lists_to_dicts(data)
    assert '/dev/vdb' in result['disk_setup']
    assert 'repo' in result['apt']['sources']
    assert 's1' in result['apt']['debconf_selections']


def test_cloud_init_data_lists_to_dicts_ethernets() -> None:
    """Transform ethernets named list to dict."""
    data = {
        'version': 2,
        'ethernets': [
            {'name': 'eth0', 'dhcp4': True, 'dhcp6': True},
            {'name': 'eth1', 'gateway4': '10.0.0.1', 'mtu': 9000},
        ],
    }
    result = cloud_init_data_lists_to_dicts(data)
    assert result['ethernets'] == {
        'eth0': {'dhcp4': True, 'dhcp6': True},
        'eth1': {'gateway4': '10.0.0.1', 'mtu': 9000},
    }
    assert result['version'] == 2


def test_cloud_init_data_lists_to_dicts_bonds() -> None:
    """Transform bonds named list to dict."""
    data = {'bonds': [{'name': 'bond0', 'interfaces': ['eth0', 'eth1']}]}
    result = cloud_init_data_lists_to_dicts(data)
    assert result == {'bonds': {'bond0': {'interfaces': ['eth0', 'eth1']}}}


def test_cloud_init_data_lists_to_dicts_bridges() -> None:
    """Transform bridges named list to dict."""
    data = {'bridges': [{'name': 'br0', 'interfaces': ['eth0'], 'dhcp4': True}]}
    result = cloud_init_data_lists_to_dicts(data)
    assert result == {'bridges': {'br0': {'interfaces': ['eth0'], 'dhcp4': True}}}


def test_cloud_init_data_lists_to_dicts_vlans() -> None:
    """Transform vlans named list to dict."""
    data = {'vlans': [{'name': 'vlan100', 'id': 100, 'link': 'eth0'}]}
    result = cloud_init_data_lists_to_dicts(data)
    assert result == {'vlans': {'vlan100': {'id': 100, 'link': 'eth0'}}}


def test_cloud_init_data_lists_to_dicts_list_recursion() -> None:
    """Recurse into list items."""
    result = cloud_init_data_lists_to_dicts([
        {'disk_setup': [{'name': '/dev/vdb'}]},
    ])
    assert result == [{'disk_setup': {'/dev/vdb': {}}}]


def test_cloud_init_interface_options_base_keys() -> None:
    """Return base interface option keys."""
    opts = cloud_init_interface_options()
    assert 'name' in opts
    assert 'dhcp4' in opts
    assert 'dhcp6' in opts
    assert 'routes' in opts
    assert 'nameservers' in opts
    assert 'mtu' in opts
    assert 'gateway4' in opts
    assert 'gateway6' in opts
    assert 'set-name' in opts
    assert 'accept-ra' in opts
    assert 'optional' in opts


def test_cloud_init_interface_options_extra_keys() -> None:
    """Merge extra keys into interface options."""
    opts = cloud_init_interface_options(
        interfaces={'type': 'list', 'elements': 'str'},
        parameters={'type': 'dict'},
    )
    assert 'interfaces' in opts
    assert 'parameters' in opts
    assert 'dhcp4' in opts
