# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for device module utilities."""

from __future__ import annotations

from ansible_collections.damex.incus.plugins.module_utils.device import devices_to_api

__all__ = [
    'test_devices_to_api_empty_list',
    'test_devices_to_api_none',
    'test_devices_to_api_disk_device',
    'test_devices_to_api_nic_device',
    'test_devices_to_api_none_values_skipped',
    'test_devices_to_api_bool_to_lowercase',
    'test_devices_to_api_bool_false_to_lowercase',
    'test_devices_to_api_multiple_devices',
    'test_devices_to_api_dot_notation_keys',
    'test_devices_to_api_int_value_stringified',
]


def test_devices_to_api_empty_list() -> None:
    """Return empty dict for empty list."""
    assert not devices_to_api([])


def test_devices_to_api_none() -> None:
    """Return empty dict for None."""
    assert not devices_to_api(None)


def test_devices_to_api_disk_device() -> None:
    """Convert disk device."""
    devices = [{'name': 'root', 'type': 'disk', 'path': '/', 'pool': 'default'}]
    assert devices_to_api(devices) == {
        'root': {'type': 'disk', 'path': '/', 'pool': 'default'},
    }


def test_devices_to_api_nic_device() -> None:
    """Convert nic device."""
    devices = [{'name': 'eth0', 'type': 'nic', 'network': 'incusbr0'}]
    assert devices_to_api(devices) == {
        'eth0': {'type': 'nic', 'network': 'incusbr0'},
    }


def test_devices_to_api_none_values_skipped() -> None:
    """Skip None values."""
    devices = [{'name': 'root', 'type': 'disk', 'path': '/', 'pool': None}]
    assert devices_to_api(devices) == {
        'root': {'type': 'disk', 'path': '/'},
    }


def test_devices_to_api_bool_to_lowercase() -> None:
    """Stringify True to 'true'."""
    devices = [{'name': 'root', 'type': 'disk', 'path': '/', 'readonly': True}]
    assert devices_to_api(devices)['root']['readonly'] == 'true'


def test_devices_to_api_bool_false_to_lowercase() -> None:
    """Stringify False to 'false'."""
    devices = [{'name': 'root', 'type': 'disk', 'path': '/', 'readonly': False}]
    assert devices_to_api(devices)['root']['readonly'] == 'false'


def test_devices_to_api_multiple_devices() -> None:
    """Convert multiple devices."""
    devices = [
        {'name': 'root', 'type': 'disk', 'path': '/', 'pool': 'default'},
        {'name': 'eth0', 'type': 'nic', 'network': 'incusbr0'},
    ]
    result = devices_to_api(devices)
    assert len(result) == 2
    assert 'root' in result
    assert 'eth0' in result


def test_devices_to_api_dot_notation_keys() -> None:
    """Preserve dot-notation keys."""
    devices = [{'name': 'eth0', 'type': 'nic', 'ipv4.address': '10.0.0.1'}]
    assert devices_to_api(devices) == {
        'eth0': {'type': 'nic', 'ipv4.address': '10.0.0.1'},
    }


def test_devices_to_api_int_value_stringified() -> None:
    """Stringify int values."""
    devices = [{'name': 'eth0', 'type': 'nic', 'mtu': 9000}]
    assert devices_to_api(devices)['eth0']['mtu'] == '9000'
