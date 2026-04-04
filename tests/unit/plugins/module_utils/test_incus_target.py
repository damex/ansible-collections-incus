# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for node-specific configuration keys."""

from __future__ import annotations

from ansible_collections.damex.incus.plugins.module_utils.incus_target import (
    incus_is_network_node_specific,
    incus_is_storage_node_specific,
)

__all__ = [
    'test_network_static_bgp_ipv4_nexthop',
    'test_network_static_bgp_ipv6_nexthop',
    'test_network_static_bridge_external_interfaces',
    'test_network_static_parent',
    'test_network_tunnel_local',
    'test_network_tunnel_interface',
    'test_network_tunnel_protocol_cluster_wide',
    'test_network_tunnel_remote_cluster_wide',
    'test_network_tunnel_group_cluster_wide',
    'test_network_tunnel_id_cluster_wide',
    'test_network_tunnel_port_cluster_wide',
    'test_network_tunnel_ttl_cluster_wide',
    'test_network_tunnel_name_only',
    'test_network_ipv4_address_cluster_wide',
    'test_network_ipv6_nat_cluster_wide',
    'test_network_dns_domain_cluster_wide',
    'test_network_bridge_mtu_cluster_wide',
    'test_storage_source',
    'test_storage_source_wipe',
    'test_storage_volatile_initial_source',
    'test_storage_zfs_pool_name',
    'test_storage_lvm_thinpool_name',
    'test_storage_lvm_vg_name',
    'test_storage_lvm_vg_force_reuse',
    'test_storage_size_zfs',
    'test_storage_size_dir',
    'test_storage_size_lvm',
    'test_storage_size_lvmcluster_cluster_wide',
    'test_storage_rsync_bwlimit_cluster_wide',
    'test_storage_rsync_compression_cluster_wide',
    'test_storage_zfs_clone_copy_cluster_wide',
    'test_storage_ceph_cluster_name_cluster_wide',
]


def test_network_static_bgp_ipv4_nexthop() -> None:
    """Verify bgp.ipv4.nexthop is node-specific."""
    assert incus_is_network_node_specific('bgp.ipv4.nexthop')


def test_network_static_bgp_ipv6_nexthop() -> None:
    """Verify bgp.ipv6.nexthop is node-specific."""
    assert incus_is_network_node_specific('bgp.ipv6.nexthop')


def test_network_static_bridge_external_interfaces() -> None:
    """Verify bridge.external_interfaces is node-specific."""
    assert incus_is_network_node_specific('bridge.external_interfaces')


def test_network_static_parent() -> None:
    """Verify parent is node-specific."""
    assert incus_is_network_node_specific('parent')


def test_network_tunnel_local() -> None:
    """Verify tunnel local is node-specific."""
    assert incus_is_network_node_specific('tunnel.site2.local')


def test_network_tunnel_interface() -> None:
    """Verify tunnel interface is node-specific."""
    assert incus_is_network_node_specific('tunnel.mysite.interface')


def test_network_tunnel_protocol_cluster_wide() -> None:
    """Verify tunnel protocol is cluster-wide."""
    assert not incus_is_network_node_specific('tunnel.site2.protocol')


def test_network_tunnel_remote_cluster_wide() -> None:
    """Verify tunnel remote is cluster-wide."""
    assert not incus_is_network_node_specific('tunnel.site2.remote')


def test_network_tunnel_group_cluster_wide() -> None:
    """Verify tunnel group is cluster-wide."""
    assert not incus_is_network_node_specific('tunnel.site2.group')


def test_network_tunnel_id_cluster_wide() -> None:
    """Verify tunnel id is cluster-wide."""
    assert not incus_is_network_node_specific('tunnel.site2.id')


def test_network_tunnel_port_cluster_wide() -> None:
    """Verify tunnel port is cluster-wide."""
    assert not incus_is_network_node_specific('tunnel.site2.port')


def test_network_tunnel_ttl_cluster_wide() -> None:
    """Verify tunnel ttl is cluster-wide."""
    assert not incus_is_network_node_specific('tunnel.site2.ttl')


def test_network_tunnel_name_only() -> None:
    """Verify bare tunnel name is not node-specific."""
    assert not incus_is_network_node_specific('tunnel.site2')


def test_network_ipv4_address_cluster_wide() -> None:
    """Verify ipv4.address is cluster-wide."""
    assert not incus_is_network_node_specific('ipv4.address')


def test_network_ipv6_nat_cluster_wide() -> None:
    """Verify ipv6.nat is cluster-wide."""
    assert not incus_is_network_node_specific('ipv6.nat')


def test_network_dns_domain_cluster_wide() -> None:
    """Verify dns.domain is cluster-wide."""
    assert not incus_is_network_node_specific('dns.domain')


def test_network_bridge_mtu_cluster_wide() -> None:
    """Verify bridge.mtu is cluster-wide."""
    assert not incus_is_network_node_specific('bridge.mtu')


def test_storage_source() -> None:
    """Verify source is node-specific."""
    assert incus_is_storage_node_specific(
        'source',
        'zfs',
    )


def test_storage_source_wipe() -> None:
    """Verify source.wipe is node-specific."""
    assert incus_is_storage_node_specific(
        'source.wipe',
        'zfs',
    )


def test_storage_volatile_initial_source() -> None:
    """Verify volatile.initial_source is node-specific."""
    assert incus_is_storage_node_specific(
        'volatile.initial_source',
        'dir',
    )


def test_storage_zfs_pool_name() -> None:
    """Verify zfs.pool_name is node-specific."""
    assert incus_is_storage_node_specific(
        'zfs.pool_name',
        'zfs',
    )


def test_storage_lvm_thinpool_name() -> None:
    """Verify lvm.thinpool_name is node-specific."""
    assert incus_is_storage_node_specific(
        'lvm.thinpool_name',
        'lvm',
    )


def test_storage_lvm_vg_name() -> None:
    """Verify lvm.vg_name is node-specific."""
    assert incus_is_storage_node_specific(
        'lvm.vg_name',
        'lvm',
    )


def test_storage_lvm_vg_force_reuse() -> None:
    """Verify lvm.vg.force_reuse is node-specific."""
    assert incus_is_storage_node_specific(
        'lvm.vg.force_reuse',
        'lvm',
    )


def test_storage_size_zfs() -> None:
    """Verify size is node-specific for zfs."""
    assert incus_is_storage_node_specific(
        'size',
        'zfs',
    )


def test_storage_size_dir() -> None:
    """Verify size is node-specific for dir."""
    assert incus_is_storage_node_specific(
        'size',
        'dir',
    )


def test_storage_size_lvm() -> None:
    """Verify size is node-specific for lvm."""
    assert incus_is_storage_node_specific(
        'size',
        'lvm',
    )


def test_storage_size_lvmcluster_cluster_wide() -> None:
    """Verify size is cluster-wide for lvmcluster."""
    assert not incus_is_storage_node_specific(
        'size',
        'lvmcluster',
    )


def test_storage_rsync_bwlimit_cluster_wide() -> None:
    """Verify rsync.bwlimit is cluster-wide."""
    assert not incus_is_storage_node_specific(
        'rsync.bwlimit',
        'dir',
    )


def test_storage_rsync_compression_cluster_wide() -> None:
    """Verify rsync.compression is cluster-wide."""
    assert not incus_is_storage_node_specific(
        'rsync.compression',
        'dir',
    )


def test_storage_zfs_clone_copy_cluster_wide() -> None:
    """Verify zfs.clone_copy is cluster-wide."""
    assert not incus_is_storage_node_specific(
        'zfs.clone_copy',
        'zfs',
    )


def test_storage_ceph_cluster_name_cluster_wide() -> None:
    """Verify ceph.cluster_name is cluster-wide."""
    assert not incus_is_storage_node_specific(
        'ceph.cluster_name',
        'ceph',
    )
