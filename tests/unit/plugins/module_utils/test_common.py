# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for common data conversion utilities."""

from __future__ import annotations

from ansible_collections.damex.incus.plugins.module_utils.common import (
    incus_common_flatten_to_config,
    incus_common_named_list_to_dict,
    incus_common_stringify_value,
)

__all__ = [
    'test_named_list_to_dict_basic',
    'test_named_list_to_dict_multiple',
    'test_named_list_to_dict_empty_list',
    'test_named_list_to_dict_none',
    'test_named_list_to_dict_skips_none_values',
    'test_named_list_to_dict_preserves_types',
    'test_flatten_to_config_required_fields',
    'test_flatten_to_config_optional_fields',
    'test_flatten_to_config_bool_values',
    'test_flatten_to_config_empty_dict',
    'test_stringify_value_bool_true',
    'test_stringify_value_bool_false',
    'test_stringify_value_string',
    'test_stringify_value_int',
]


def test_named_list_to_dict_basic() -> None:
    """Convert named list to dict keyed by name."""
    items = [{'name': 'router', 'address': '10.0.0.1', 'asn': 64601}]
    result = incus_common_named_list_to_dict(items)
    assert result == {'router': {'address': '10.0.0.1', 'asn': 64601}}


def test_named_list_to_dict_multiple() -> None:
    """Convert multiple named dicts."""
    items = [
        {'name': 'eth0', 'dhcp4': True},
        {'name': 'eth1', 'dhcp4': False, 'addresses': ['10.0.0.2/24']},
    ]
    result = incus_common_named_list_to_dict(items)
    assert result == {
        'eth0': {'dhcp4': True},
        'eth1': {'dhcp4': False, 'addresses': ['10.0.0.2/24']},
    }


def test_named_list_to_dict_empty_list() -> None:
    """Return empty dict for empty list."""
    assert not incus_common_named_list_to_dict([])


def test_named_list_to_dict_none() -> None:
    """Return empty dict for None."""
    assert not incus_common_named_list_to_dict(None)


def test_named_list_to_dict_skips_none_values() -> None:
    """Skip None values in items."""
    items = [{'name': 'router', 'address': '10.0.0.1', 'holdtime': None}]
    result = incus_common_named_list_to_dict(items)
    assert result == {'router': {'address': '10.0.0.1'}}


def test_named_list_to_dict_preserves_types() -> None:
    """Preserve non-string types in values."""
    items = [{'name': '/dev/vdb', 'table_type': 'gpt', 'layout': True}]
    result = incus_common_named_list_to_dict(items)
    assert result == {'/dev/vdb': {'table_type': 'gpt', 'layout': True}}


def test_flatten_to_config_required_fields() -> None:
    """Flatten nested dict to dotted config keys."""
    data = {'router': {'address': '10.0.0.1', 'asn': 64601}}
    result = incus_common_flatten_to_config('bgp.peers', data)
    assert result == {
        'bgp.peers.router.address': '10.0.0.1',
        'bgp.peers.router.asn': '64601',
    }


def test_flatten_to_config_optional_fields() -> None:
    """Flatten nested dict with optional fields."""
    data = {'router': {'address': '10.0.0.1', 'asn': 64601, 'holdtime': 300, 'password': 'secret'}}
    result = incus_common_flatten_to_config('bgp.peers', data)
    assert result == {
        'bgp.peers.router.address': '10.0.0.1',
        'bgp.peers.router.asn': '64601',
        'bgp.peers.router.holdtime': '300',
        'bgp.peers.router.password': 'secret',
    }


def test_flatten_to_config_bool_values() -> None:
    """Stringify bool values as lowercase."""
    data = {'test': {'enabled': True, 'disabled': False}}
    result = incus_common_flatten_to_config('prefix', data)
    assert result == {
        'prefix.test.enabled': 'true',
        'prefix.test.disabled': 'false',
    }


def test_flatten_to_config_empty_dict() -> None:
    """Return empty dict for empty input."""
    assert not incus_common_flatten_to_config('bgp.peers', {})


def test_stringify_value_bool_true() -> None:
    """Stringify True as lowercase."""
    assert incus_common_stringify_value(True) == 'true'


def test_stringify_value_bool_false() -> None:
    """Stringify False as lowercase."""
    assert incus_common_stringify_value(False) == 'false'


def test_stringify_value_string() -> None:
    """Preserve string values."""
    assert incus_common_stringify_value('hello') == 'hello'


def test_stringify_value_int() -> None:
    """Stringify int values."""
    assert incus_common_stringify_value(64601) == '64601'
