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
        choices: [disk, gpu, infiniband, nic, none, pci, proxy, tpm, unix-block, unix-char, unix-hotplug, usb]
        required: true
      # shared
      attached:
        description: Whether the device is attached or ejected (disk, nic).
        type: bool
      boot.priority:
        description: Boot priority for VMs (disk, nic).
        type: int
      gid:
        description: GID of the device owner in the instance (unix-char, unix-block, unix-hotplug).
        type: int
      io.bus:
        description: Override bus for the device, e.g. C(virtio) or C(usb) (disk, nic, VMs only).
        type: str
      limits.max:
        description: I/O limit in byte/s or IOPS for both read and write (disk), or combined traffic limit in bit/s (nic).
        type: str
      mode:
        description: NIC mode, e.g. C(bridge) for macvlan (nic), or device permission mode, e.g. C(0660) (unix-char, unix-block, unix-hotplug).
        type: str
      path:
        description: Path inside the instance (disk, tpm, unix-char, unix-block).
        type: str
      pci:
        description: PCI address of the parent host device (nic SR-IOV, unix-hotplug).
        type: str
      productid:
        description: Product ID of the parent host device (nic SR-IOV, unix-hotplug).
        type: str
      required:
        description: Whether to fail if the source does not exist (disk, unix-char, unix-block, unix-hotplug).
        type: bool
      source:
        description: Source of a file system, block device, or host device path (disk, unix-char, unix-block).
        type: str
      uid:
        description: UID of the device owner in the instance (unix-char, unix-block, unix-hotplug).
        type: int
      hwaddr:
        description: MAC address of the new interface (nic, infiniband).
        type: str
      mtu:
        description: Maximum transmission unit of the new interface (nic, infiniband).
        type: str
      nictype:
        description: NIC type when not using a managed network (nic, infiniband).
        type: str
      parent:
        description: Parent host device name (nic, infiniband).
        type: str
      vendorid:
        description: Vendor ID of the parent host device (nic SR-IOV, unix-hotplug).
        type: str
      # disk
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
      shift:
        description: Whether to set up a shifting overlay to translate the source UID/GID (disk, containers only).
        type: bool
      size:
        description: Disk size limit, e.g. C(20GiB) (disk only).
        type: str
      size.state:
        description: Size for the VM runtime state file system (disk, VMs only).
        type: str
      wwn:
        description: Whether to set a World Wide Name for the disk (disk, VMs only).
        type: bool
      # nic
      acceleration:
        description: Enable hardware offloading (none/sriov/vdpa) (nic, OVN only).
        type: str
      connected:
        description: Whether the NIC is connected to the host network (nic only).
        type: bool
      gvrp:
        description: Register VLAN using GARP VLAN Registration Protocol (nic only).
        type: bool
      host_name:
        description: Name of the interface on the host (nic only).
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
      limits.priority:
        description: Outgoing traffic priority for queuing (nic only).
        type: int
      nested:
        description: Parent NIC name to nest this OVN NIC under (nic, OVN only).
        type: str
      network:
        description: Managed Incus network to attach the NIC to (nic only).
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
      vlan:
        description: VLAN ID to attach to (nic only).
        type: int
      vlan.tagged:
        description: Comma-separated VLAN IDs or ranges for tagged traffic (nic only).
        type: str
      vrf:
        description: VRF name on the host for the host-side interface and routes (nic, routed only).
        type: str
      # proxy
      bind:
        description: Which side to bind on, C(host) or C(instance) (proxy only).
        type: str
      connect:
        description: Address and port to connect to (proxy only).
        type: str
      listen:
        description: Address and port to bind and listen on (proxy only).
        type: str
      nat:
        description: Whether to use NAT-based proxying (proxy only).
        type: bool
      proxy_protocol:
        description: Whether to use the HAProxy PROXY protocol to transmit sender information (proxy only).
        type: bool
      security.gid:
        description: GID to drop privilege to (proxy only).
        type: int
      security.uid:
        description: UID to drop privilege to (proxy only).
        type: int
      # tpm
      pathrm:
        description: Resource manager path inside the instance, e.g. C(/dev/tpmrm0) (tpm, containers only).
        type: str
      # unix-char, unix-block
      major:
        description: Device major number (unix-char, unix-block).
        type: int
      minor:
        description: Device minor number (unix-char, unix-block).
        type: int
      # gpu
      id:
        description: DRM card ID of the GPU device (gpu only).
        type: str
      mdev:
        description: Mediated device profile to use (gpu mdev only, VMs only).
        type: str
      mig.ci:
        description: Existing MIG compute instance ID (gpu mig only, containers only).
        type: int
      mig.gi:
        description: Existing MIG GPU instance ID (gpu mig only, containers only).
        type: int
      mig.uuid:
        description: Existing MIG device UUID (gpu mig only, containers only).
        type: str
      # pci
      address:
        description: PCI address of the device (pci only, VMs only).
        type: str
      firmware:
        description: Whether to expose the device's option ROM to the VM (pci only).
        type: bool
      # usb
      busnum:
        description: Bus number the USB device is connected to (usb only).
        type: int
      devnum:
        description: Device number of the USB device (usb only).
        type: int
      serial:
        description: Serial number of the USB device (usb only).
        type: str
"""
