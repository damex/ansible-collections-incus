# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Devices documentation fragment for Incus modules."""

from __future__ import annotations

__all__ = ['ModuleDocFragment']


class ModuleDocFragment:  # pylint: disable=too-few-public-methods
    """Device options."""

    DOCUMENTATION = r"""
options:
  devices:
    description:
      - Devices as a list.
      - Each item must include a C(name) field used as the device key in the Incus API.
      - Boolean values are converted to lowercase strings.
    type: list
    elements: dict
    default: []
    suboptions:
      name:
        description: Device name used as the key in the Incus API.
        type: str
        required: true
      type:
        description: Device type.
        type: str
        choices: [disk, nic]
        required: true
      ceph.cluster_name:
        description: Ceph cluster name (disk only).
        type: str
      ceph.user_name:
        description: Ceph user name (disk only).
        type: str
      io.cache:
        description: Caching mode for the disk device (disk only).
        type: str
      limits.read:
        description: I/O limit in byte/s or IOPS for read operations (disk only).
        type: str
      limits.write:
        description: I/O limit in byte/s or IOPS for write operations (disk only).
        type: str
      path:
        description: Path inside the instance where the disk will be mounted (disk only).
        type: str
      pool:
        description: Incus storage pool backing the disk device (disk only).
        type: str
      propagation:
        description: Controls how a bind-mount is shared between instance and host (disk only).
        type: str
      raw.mount.options:
        description: File system specific mount options (disk only).
        type: str
      readonly:
        description: Whether to make the mount read-only (disk only).
        type: bool
      recursive:
        description: Whether to recursively mount the source path (disk only).
        type: bool
      required:
        description: Whether to fail if the source path does not exist (disk only).
        type: bool
      shift:
        description: Whether to set up a shifting overlay to translate the source UID/GID (disk, containers only).
        type: bool
      size:
        description: Disk size limit, e.g. C(20GiB) (disk only).
        type: str
      size.state:
        description: Size for the VM runtime state file system (disk, VMs only).
        type: str
      source:
        description: Source of a file system or block device (disk only).
        type: str
      wwn:
        description: Whether to set a World Wide Name for the disk (disk, VMs only).
        type: bool
      acceleration:
        description: Enable hardware offloading (none/sriov/vdpa) (nic, OVN only).
        type: str
      attached:
        description: Whether the device is attached or ejected (disk, nic).
        type: bool
      boot.priority:
        description: Boot priority for VMs (disk, nic).
        type: int
      connected:
        description: Whether the NIC is connected to the host network (nic only).
        type: bool
      gvrp:
        description: Register VLAN using GARP VLAN Registration Protocol (nic only).
        type: bool
      host_name:
        description: Name of the interface on the host (nic only).
        type: str
      hwaddr:
        description: MAC address of the new interface (nic only).
        type: str
      io.bus:
        description: Override bus for the device, e.g. C(virtio) or C(usb) (disk, nic, VMs only).
        type: str
      ipv4.address:
        description: IPv4 address to assign via DHCP or static allocation (nic only).
        type: str
      ipv4.address.external:
        description: Select specific external IPv4 address (nic, OVN only).
        type: str
      ipv4.gateway:
        description: Default IPv4 gateway, e.g. C(auto) or C(none) (nic, routed/ipvlan only).
        type: str
      ipv4.host_address:
        description: IPv4 address on the host-side veth interface (nic, routed only).
        type: str
      ipv4.host_table:
        description: Custom policy routing table ID for IPv4 (nic, deprecated in favor of C(ipv4.host_tables)).
        type: int
      ipv4.host_tables:
        description: Comma-separated routing table IDs for IPv4 routes (nic, routed only).
        type: str
      ipv4.neighbor_probe:
        description: Whether to probe the parent network for IP availability (nic, routed only).
        type: bool
      ipv4.routes:
        description: Comma-delimited IPv4 static routes to add on the host (nic only).
        type: str
      ipv4.routes.external:
        description: Comma-delimited IPv4 routes to publish via BGP (nic only).
        type: str
      ipv6.address:
        description: IPv6 address to assign via DHCP or static allocation (nic only).
        type: str
      ipv6.address.external:
        description: Select specific external IPv6 address (nic, OVN only).
        type: str
      ipv6.gateway:
        description: Default IPv6 gateway, e.g. C(auto) or C(none) (nic, routed/ipvlan only).
        type: str
      ipv6.host_address:
        description: IPv6 address on the host-side veth interface (nic, routed only).
        type: str
      ipv6.host_table:
        description: Custom policy routing table ID for IPv6 (nic, deprecated in favor of C(ipv6.host_tables)).
        type: int
      ipv6.host_tables:
        description: Comma-separated routing table IDs for IPv6 routes (nic, routed only).
        type: str
      ipv6.neighbor_probe:
        description: Whether to probe the parent network for IP availability (nic, routed only).
        type: bool
      ipv6.routes:
        description: Comma-delimited IPv6 static routes to add on the host (nic only).
        type: str
      ipv6.routes.external:
        description: Comma-delimited IPv6 routes to publish via BGP (nic only).
        type: str
      limits.egress:
        description: Outgoing traffic I/O limit in bit/s (nic only).
        type: str
      limits.ingress:
        description: Incoming traffic I/O limit in bit/s (nic only).
        type: str
      limits.max:
        description: I/O limit in byte/s or IOPS for both read and write (disk), or combined traffic limit in bit/s (nic).
        type: str
      limits.priority:
        description: Outgoing traffic priority for queuing (nic only).
        type: int
      mode:
        description: NIC mode, e.g. C(bridge) for macvlan or C(l3s) for ipvlan (nic only).
        type: str
      mtu:
        description: Maximum transmission unit of the new interface (nic only).
        type: str
      nested:
        description: Parent NIC name to nest this OVN NIC under (nic, OVN only).
        type: str
      network:
        description: Managed Incus network to attach the NIC to (nic only).
        type: str
      nictype:
        description: NIC type when not using a managed network, e.g. C(bridged) or C(macvlan) (nic only).
        type: str
      parent:
        description: Parent host device name (nic only).
        type: str
      pci:
        description: PCI address of the parent host device (nic, SR-IOV only).
        type: str
      productid:
        description: Product ID of the parent host device (nic, SR-IOV only).
        type: str
      queue.tx.length:
        description: Transmit queue length for the NIC (nic only).
        type: int
      security.acls:
        description: Comma-separated list of network ACLs to apply (nic only).
        type: str
      security.acls.default.egress.action:
        description: Default action for egress traffic not matching any ACL rule (nic only).
        type: str
      security.acls.default.egress.logged:
        description: Whether to log egress traffic not matching any ACL rule (nic only).
        type: bool
      security.acls.default.ingress.action:
        description: Default action for ingress traffic not matching any ACL rule (nic only).
        type: str
      security.acls.default.ingress.logged:
        description: Whether to log ingress traffic not matching any ACL rule (nic only).
        type: bool
      security.ipv4_filtering:
        description: Whether to prevent IPv4 address spoofing (nic, bridged only).
        type: bool
      security.ipv6_filtering:
        description: Whether to prevent IPv6 address spoofing (nic, bridged only).
        type: bool
      security.mac_filtering:
        description: Whether to prevent MAC address spoofing (nic only).
        type: bool
      security.port_isolation:
        description: Whether to prevent the NIC from communicating with other isolated NICs (nic, bridged only).
        type: bool
      security.promiscuous:
        description: Whether to send unknown traffic to this interface (nic, OVN only).
        type: bool
      security.trusted:
        description: Whether to allow the instance to configure the NIC in potentially unsafe ways (nic, SR-IOV only).
        type: bool
      vendorid:
        description: Vendor ID of the parent host device (nic, SR-IOV only).
        type: str
      vlan:
        description: VLAN ID to attach to (nic only).
        type: int
      vlan.tagged:
        description: Comma-separated VLAN IDs or ranges for tagged traffic (nic only).
        type: str
      vrf:
        description: VRF name on the host for the host-side interface and routes (nic, routed only).
        type: str
"""
