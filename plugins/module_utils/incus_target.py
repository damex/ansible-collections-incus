# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Incus node-specific configuration keys.
"""

from __future__ import annotations

__all__ = [
    'incus_is_network_node_specific',
    'incus_is_storage_node_specific',
]

INCUS_NETWORK_NODE_SPECIFIC_KEYS = frozenset({
    'bgp.ipv4.nexthop',
    'bgp.ipv6.nexthop',
    'bridge.external_interfaces',
    'parent',
})

INCUS_NETWORK_NODE_SPECIFIC_LIST_KEYS = {
    'tunnel': frozenset({
        'interface',
        'local',
    }),
}

INCUS_STORAGE_NODE_SPECIFIC_KEYS = frozenset({
    'lvm.thinpool_name',
    'lvm.vg.force_reuse',
    'lvm.vg_name',
    'source',
    'source.wipe',
    'volatile.initial_source',
    'zfs.pool_name',
})


def incus_is_network_node_specific(config_key: str) -> bool:
    """
    Check node-specific network config key.

    >>> incus_is_network_node_specific('parent')
    True
    >>> incus_is_network_node_specific('tunnel.site2.local')
    True
    >>> incus_is_network_node_specific('ipv4.address')
    False
    """
    if config_key in INCUS_NETWORK_NODE_SPECIFIC_KEYS:
        return True
    for list_prefix, list_sub_keys in INCUS_NETWORK_NODE_SPECIFIC_LIST_KEYS.items():
        full_prefix = list_prefix + '.'
        if config_key.startswith(full_prefix):
            remainder = config_key[len(full_prefix):]
            dot_position = remainder.find('.')
            if dot_position > 0 and remainder[dot_position + 1:] in list_sub_keys:
                return True
    return False


def incus_is_storage_node_specific(
    config_key: str,
    driver_name: str,
) -> bool:
    """
    Check node-specific storage config key.

    >>> incus_is_storage_node_specific(
    ...     'source',
    ...     'zfs',
    ... )
    True
    >>> incus_is_storage_node_specific(
    ...     'size',
    ...     'lvmcluster',
    ... )
    False
    """
    if config_key in INCUS_STORAGE_NODE_SPECIFIC_KEYS:
        return True
    if config_key == 'size' and driver_name != 'lvmcluster':
        return True
    return False
