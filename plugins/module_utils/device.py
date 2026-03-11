# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Incus device argument spec and helpers shared by profile and instance modules."""

from __future__ import annotations

from typing import Any

__all__ = [
    'INCUS_DEVICE_OPTIONS',
    'devices_to_api',
]

INCUS_DEVICE_OPTIONS: dict[str, dict[str, Any]] = {
    'name': {'type': 'str', 'required': True},
    'type': {'type': 'str', 'required': True, 'choices': ['disk', 'nic']},
    # disk
    'path': {'type': 'str'},
    'pool': {'type': 'str'},
    'source': {'type': 'str'},
    'size': {'type': 'str'},
    'readonly': {'type': 'bool'},
    # nic
    'acceleration': {'type': 'str'},
    'attached': {'type': 'bool'},
    'boot.priority': {'type': 'int'},
    'connected': {'type': 'bool'},
    'gvrp': {'type': 'bool'},
    'host_name': {'type': 'str'},
    'hwaddr': {'type': 'str'},
    'io.bus': {'type': 'str'},
    'ipv4.address': {'type': 'str'},
    'ipv4.address.external': {'type': 'str'},
    'ipv4.gateway': {'type': 'str'},
    'ipv4.host_address': {'type': 'str'},
    'ipv4.host_table': {'type': 'int'},
    'ipv4.host_tables': {'type': 'str'},
    'ipv4.neighbor_probe': {'type': 'bool'},
    'ipv4.routes': {'type': 'str'},
    'ipv4.routes.external': {'type': 'str'},
    'ipv6.address': {'type': 'str'},
    'ipv6.address.external': {'type': 'str'},
    'ipv6.gateway': {'type': 'str'},
    'ipv6.host_address': {'type': 'str'},
    'ipv6.host_table': {'type': 'int'},
    'ipv6.host_tables': {'type': 'str'},
    'ipv6.neighbor_probe': {'type': 'bool'},
    'ipv6.routes': {'type': 'str'},
    'ipv6.routes.external': {'type': 'str'},
    'limits.egress': {'type': 'str'},
    'limits.ingress': {'type': 'str'},
    'limits.max': {'type': 'str'},
    'limits.priority': {'type': 'int'},
    'mode': {'type': 'str'},
    'mtu': {'type': 'str'},
    'nested': {'type': 'str'},
    'network': {'type': 'str'},
    'nictype': {'type': 'str'},
    'parent': {'type': 'str'},
    'pci': {'type': 'str'},
    'productid': {'type': 'str'},
    'queue.tx.length': {'type': 'int'},
    'security.acls': {'type': 'str'},
    'security.acls.default.egress.action': {'type': 'str'},
    'security.acls.default.egress.logged': {'type': 'bool'},
    'security.acls.default.ingress.action': {'type': 'str'},
    'security.acls.default.ingress.logged': {'type': 'bool'},
    'security.ipv4_filtering': {'type': 'bool'},
    'security.ipv6_filtering': {'type': 'bool'},
    'security.mac_filtering': {'type': 'bool'},
    'security.port_isolation': {'type': 'bool'},
    'security.promiscuous': {'type': 'bool'},
    'security.trusted': {'type': 'bool'},
    'vendorid': {'type': 'str'},
    'vlan': {'type': 'int'},
    'vlan.tagged': {'type': 'str'},
    'vrf': {'type': 'str'},
}


def devices_to_api(devices: list[dict[str, Any]] | None) -> dict[str, dict[str, str]]:
    """Convert list of devices to Incus API dict format keyed by device name."""
    api_devices: dict[str, dict[str, str]] = {}
    for device in (devices or []):
        device_name: str = device['name']
        device_config: dict[str, str] = {}
        for k, v in device.items():
            if k == 'name' or v is None:
                continue
            if isinstance(v, bool):
                device_config[k] = str(v).lower()
            else:
                device_config[k] = str(v)
        api_devices[device_name] = device_config
    return api_devices
