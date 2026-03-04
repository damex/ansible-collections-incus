# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Incus device argument spec and helpers shared by profile and instance modules."""

from __future__ import annotations

__all__ = [
    'INCUS_DEVICE_OPTIONS',
    'devices_to_api',
]

INCUS_DEVICE_OPTIONS = {
    'name': {'type': 'str', 'required': True},
    'type': {'type': 'str', 'required': True, 'choices': ['disk', 'nic']},
    # disk
    'path': {'type': 'str'},
    'pool': {'type': 'str'},
    'source': {'type': 'str'},
    'size': {'type': 'str'},
    'readonly': {'type': 'bool'},
    # nic
    'network': {'type': 'str'},
    'nictype': {'type': 'str'},
    'parent': {'type': 'str'},
    'hwaddr': {'type': 'str'},
    'mtu': {'type': 'str'},
    'ipv4.address': {'type': 'str'},
    'ipv4.routes': {'type': 'str'},
    'ipv6.address': {'type': 'str'},
    'ipv6.routes': {'type': 'str'},
}


def devices_to_api(devices):
    """Convert list of devices to Incus API dict format keyed by device name."""
    api_devices = {}
    for device in (devices or []):
        device_name = device['name']
        device_config = {}
        for k, v in device.items():
            if k == 'name' or v is None:
                continue
            if isinstance(v, bool):
                device_config[k] = str(v).lower()
            else:
                device_config[k] = str(v)
        api_devices[device_name] = device_config
    return api_devices
