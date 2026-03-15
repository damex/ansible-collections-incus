#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Ensure Incus network."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_network
short_description: Ensure Incus network
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Create, update, and delete Incus networks via the Incus REST API.
  - Networks are project-scoped resources.
  - The network type is set on creation and cannot be changed afterwards.
extends_documentation_fragment: [damex.incus.common, damex.incus.common.project, damex.incus.common.write]
options:
  name:
    description:
      - Name of the network.
    type: str
    required: true
  state:
    description:
      - Desired state of the network.
    type: str
    choices: [present, absent]
    default: present
  target:
    description:
      - Cluster member to target for pending network creation.
    type: str
  type:
    description:
      - Network type.
      - Required when creating a new network.
      - Ignored on update — type cannot be changed after creation.
    type: str
    choices:
      - bridge
      - macvlan
      - ovn
      - physical
      - sriov
  description:
    description:
      - Network description.
    type: str
    default: ''
  config:
    description:
      - Network configuration key-value pairs.
      - Boolean values are converted to lowercase strings.
    type: dict
    default: {}
    suboptions:
      bridge.driver:
        description:
          - Bridge driver to use.
        type: str
        choices: [native, openvswitch]
      bridge.external_interfaces:
        description:
          - Comma-separated list of unconfigured NICs to bridge.
        type: str
      bridge.hwaddr:
        description:
          - MAC address for the bridge.
        type: str
      bridge.mtu:
        description:
          - Bridge MTU.
        type: str
      dns.domain:
        description:
          - Domain to advertise to DHCP clients and use for DNS resolution.
        type: str
      dns.mode:
        description:
          - DNS registration mode.
        type: str
        choices: [managed, dynamic, none]
      dns.nameservers:
        description:
          - Comma-separated list of DNS nameservers.
        type: str
      dns.search:
        description:
          - Comma-separated list of DNS search domains.
        type: str
      dns.zone.forward:
        description:
          - Comma-separated list of DNS zone names for forward DNS records.
        type: str
      dns.zone.reverse.ipv4:
        description:
          - DNS zone name for IPv4 reverse DNS records.
        type: str
      dns.zone.reverse.ipv6:
        description:
          - DNS zone name for IPv6 reverse DNS records.
        type: str
      ipv4.address:
        description:
          - IPv4 address for the bridge (use none or auto).
        type: str
      ipv4.dhcp:
        description:
          - Whether to allocate addresses via DHCP.
        type: bool
      ipv4.dhcp.expiry:
        description:
          - DHCP lease expiry time.
        type: str
      ipv4.dhcp.gateway:
        description:
          - Address of the gateway for the subnet.
        type: str
      ipv4.dhcp.ranges:
        description:
          - Comma-separated list of IPv4 DHCP ranges.
        type: str
      ipv4.dhcp.routes:
        description:
          - Additional IPv4 routes to advertise via DHCP.
        type: str
      ipv4.firewall:
        description:
          - Whether to generate filtering firewall rules.
        type: bool
      ipv4.gateway:
        description:
          - Override gateway for the subnet.
        type: str
      ipv4.gateway.hwaddr:
        description:
          - MAC address of the gateway.
        type: str
      ipv4.nat:
        description:
          - Whether to NAT IPv4 traffic.
        type: bool
      ipv4.nat.address:
        description:
          - Source address for outbound IPv4 NAT.
        type: str
      ipv4.nat.order:
        description:
          - Whether to add NAT rules before or after pre-existing rules.
        type: str
        choices: [before, after]
      ipv4.routes:
        description:
          - Comma-separated list of additional IPv4 CIDR subnets to route to the bridge.
        type: str
      ipv4.routes.anycast:
        description:
          - Whether to allow overlapping routes on multiple networks.
        type: bool
      ipv4.routing:
        description:
          - Whether to route IPv4 traffic in and out of the bridge.
        type: bool
      ipv6.address:
        description:
          - IPv6 address for the bridge (use none or auto).
        type: str
      ipv6.dhcp:
        description:
          - Whether to provide additional network configuration via DHCPv6.
        type: bool
      ipv6.dhcp.expiry:
        description:
          - DHCPv6 lease expiry time.
        type: str
      ipv6.dhcp.ranges:
        description:
          - Comma-separated list of IPv6 DHCP ranges.
        type: str
      ipv6.dhcp.stateful:
        description:
          - Whether to enable stateful DHCPv6 address allocation.
        type: bool
      ipv6.firewall:
        description:
          - Whether to generate filtering firewall rules.
        type: bool
      ipv6.gateway:
        description:
          - Override gateway for the subnet.
        type: str
      ipv6.gateway.hwaddr:
        description:
          - MAC address of the gateway.
        type: str
      ipv6.nat:
        description:
          - Whether to NAT IPv6 traffic.
        type: bool
      ipv6.nat.address:
        description:
          - Source address for outbound IPv6 NAT.
        type: str
      ipv6.nat.order:
        description:
          - Whether to add NAT rules before or after pre-existing rules.
        type: str
        choices: [before, after]
      ipv6.routes:
        description:
          - Comma-separated list of additional IPv6 CIDR subnets to route to the bridge.
        type: str
      ipv6.routes.anycast:
        description:
          - Whether to allow overlapping routes on multiple networks.
        type: bool
      ipv6.routing:
        description:
          - Whether to route IPv6 traffic in and out of the bridge.
        type: bool
      raw.dnsmasq:
        description:
          - Additional dnsmasq configuration to append.
        type: str
      security.acls:
        description:
          - Comma-separated list of network ACLs to apply.
        type: str
      security.acls.default.egress.action:
        description:
          - Default action for egress traffic not matching any ACL rule.
        type: str
        choices: [allow, reject, drop]
      security.acls.default.egress.logged:
        description:
          - Whether to log default egress actions.
        type: bool
      security.acls.default.ingress.action:
        description:
          - Default action for ingress traffic not matching any ACL rule.
        type: str
        choices: [allow, reject, drop]
      security.acls.default.ingress.logged:
        description:
          - Whether to log default ingress actions.
        type: bool
      bgp.ipv4.nexthop:
        description:
          - Override the next-hop for advertised IPv4 prefixes.
        type: str
      bgp.ipv6.nexthop:
        description:
          - Override the next-hop for advertised IPv6 prefixes.
        type: str
      gvrp:
        description:
          - Whether to register VLAN via GARP VLAN Registration Protocol.
        type: bool
      mtu:
        description:
          - MTU of the network interface.
        type: str
      parent:
        description:
          - Parent interface to use for the network.
        type: str
      vlan:
        description:
          - VLAN ID to attach to.
        type: int
      vlan.tagged:
        description:
          - Comma-separated list of VLAN IDs to join for tagged traffic.
        type: str
      bgp_peers:
        description:
          - List of BGP peers for OVN downstream networks.
          - Each peer is converted to C(bgp.peers.<name>.<key>) config keys internally.
          - Supported on bridge and physical network types used as OVN uplinks.
        type: list
        elements: dict
        suboptions:
          name:
            description:
              - Name identifier for the BGP peer.
            type: str
            required: true
          address:
            description:
              - Peer address (IPv4 or IPv6).
            type: str
            required: true
          asn:
            description:
              - Peer AS number.
            type: int
            required: true
          holdtime:
            description:
              - Hold time in seconds for the BGP session.
            type: int
          password:
            description:
              - Password for the BGP session.
            type: str
      tunnels:
        description:
          - List of tunnels for bridge networks.
          - Each tunnel is converted to C(tunnel.<name>.<key>) config keys internally.
        type: list
        elements: dict
        suboptions:
          name:
            description:
              - Name identifier for the tunnel.
            type: str
            required: true
          protocol:
            description:
              - Tunneling protocol.
            type: str
            required: true
            choices: [vxlan, gre]
          local:
            description:
              - Local address for the tunnel.
            type: str
          remote:
            description:
              - Remote address for the tunnel.
            type: str
          group:
            description:
              - Multicast address for VXLAN tunnels.
            type: str
          id:
            description:
              - Tunnel ID for VXLAN tunnels.
            type: int
          port:
            description:
              - Destination UDP port for VXLAN tunnels.
            type: int
          interface:
            description:
              - Host interface to use for the tunnel.
            type: str
          ttl:
            description:
              - TTL for multicast routing topologies.
            type: int
"""

EXAMPLES = r"""
- name: Ensure bridge network
  damex.incus.incus_network:
    name: incusbr0
    type: bridge
    config:
      ipv4.address: 10.0.0.1/24
      ipv4.nat: true

- name: Ensure network on cluster member
  damex.incus.incus_network:
    name: incusbr0
    type: bridge
    target: node1

- name: Ensure network is finalized
  damex.incus.incus_network:
    name: incusbr0
    type: bridge
    config:
      ipv4.address: 10.0.0.1/24
      ipv4.nat: true

- name: Ensure bridge network with BGP peers
  damex.incus.incus_network:
    name: bgpbr0
    type: bridge
    config:
      ipv4.address: 10.12.102.1/24
      ipv4.nat: false
      bgp_peers:
        - name: router
          address: 10.12.101.1
          asn: 64601
        - name: backup
          address: 10.12.101.2
          asn: 64602
          holdtime: 300

- name: Ensure bridge network with VXLAN tunnel
  damex.incus.incus_network:
    name: multibr0
    type: bridge
    config:
      ipv4.address: 10.0.0.1/24
      tunnels:
        - name: site2
          protocol: vxlan
          local: 192.168.1.1
          remote: 192.168.1.2
          id: 100

- name: Ensure network is absent
  damex.incus.incus_network:
    name: incusbr0
    state: absent
"""

RETURN = r"""
"""

from typing import Any

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    INCUS_COMMON_ARGUMENT_SPEC,
    incus_create_write_module,
    incus_ensure_resource,
    incus_common_flatten_to_config,
    incus_common_named_list_to_dict,
    incus_common_stringify_dict,
    incus_run_write_module,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']

INCUS_NETWORK_CONFIG_OPTIONS = {
    'bridge.driver': {
        'type': 'str',
        'choices': [
            'native',
            'openvswitch',
        ],
    },
    'bridge.external_interfaces': {'type': 'str'},
    'bridge.hwaddr': {'type': 'str'},
    'bridge.mtu': {'type': 'str'},
    'dns.domain': {'type': 'str'},
    'dns.mode': {
        'type': 'str',
        'choices': [
            'managed',
            'dynamic',
            'none',
        ],
    },
    'dns.nameservers': {'type': 'str'},
    'dns.search': {'type': 'str'},
    'dns.zone.forward': {'type': 'str'},
    'dns.zone.reverse.ipv4': {'type': 'str'},
    'dns.zone.reverse.ipv6': {'type': 'str'},
    'ipv4.address': {'type': 'str'},
    'ipv4.dhcp': {'type': 'bool'},
    'ipv4.dhcp.expiry': {'type': 'str'},
    'ipv4.dhcp.gateway': {'type': 'str'},
    'ipv4.dhcp.ranges': {'type': 'str'},
    'ipv4.dhcp.routes': {'type': 'str'},
    'ipv4.firewall': {'type': 'bool'},
    'ipv4.gateway': {'type': 'str'},
    'ipv4.gateway.hwaddr': {'type': 'str'},
    'ipv4.nat': {'type': 'bool'},
    'ipv4.nat.address': {'type': 'str'},
    'ipv4.nat.order': {
        'type': 'str',
        'choices': [
            'before',
            'after',
        ],
    },
    'ipv4.routes': {'type': 'str'},
    'ipv4.routes.anycast': {'type': 'bool'},
    'ipv4.routing': {'type': 'bool'},
    'ipv6.address': {'type': 'str'},
    'ipv6.dhcp': {'type': 'bool'},
    'ipv6.dhcp.expiry': {'type': 'str'},
    'ipv6.dhcp.ranges': {'type': 'str'},
    'ipv6.dhcp.stateful': {'type': 'bool'},
    'ipv6.firewall': {'type': 'bool'},
    'ipv6.gateway': {'type': 'str'},
    'ipv6.gateway.hwaddr': {'type': 'str'},
    'ipv6.nat': {'type': 'bool'},
    'ipv6.nat.address': {'type': 'str'},
    'ipv6.nat.order': {
        'type': 'str',
        'choices': [
            'before',
            'after',
        ],
    },
    'ipv6.routes': {'type': 'str'},
    'ipv6.routes.anycast': {'type': 'bool'},
    'ipv6.routing': {'type': 'bool'},
    'raw.dnsmasq': {'type': 'str'},
    'security.acls': {'type': 'str'},
    'security.acls.default.egress.action': {
        'type': 'str',
        'choices': [
            'allow',
            'reject',
            'drop',
        ],
    },
    'security.acls.default.egress.logged': {'type': 'bool'},
    'security.acls.default.ingress.action': {
        'type': 'str',
        'choices': [
            'allow',
            'reject',
            'drop',
        ],
    },
    'security.acls.default.ingress.logged': {'type': 'bool'},
    'bgp.ipv4.nexthop': {'type': 'str'},
    'bgp.ipv6.nexthop': {'type': 'str'},
    'gvrp': {'type': 'bool'},
    'mtu': {'type': 'str'},
    'parent': {'type': 'str'},
    'vlan': {'type': 'int'},
    'vlan.tagged': {'type': 'str'},
    'bgp_peers': {
        'type': 'list',
        'elements': 'dict',
        'options': {
            'name': {
                'type': 'str',
                'required': True,
            },
            'address': {
                'type': 'str',
                'required': True,
            },
            'asn': {
                'type': 'int',
                'required': True,
            },
            'holdtime': {'type': 'int'},
            'password': {
                'type': 'str',
                'no_log': True,
            },
        },
    },
    'tunnels': {
        'type': 'list',
        'elements': 'dict',
        'options': {
            'name': {
                'type': 'str',
                'required': True,
            },
            'protocol': {
                'type': 'str',
                'required': True,
                'choices': [
                    'vxlan',
                    'gre',
                ],
            },
            'local': {'type': 'str'},
            'remote': {'type': 'str'},
            'group': {'type': 'str'},
            'id': {'type': 'int'},
            'port': {'type': 'int'},
            'interface': {'type': 'str'},
            'ttl': {'type': 'int'},
        },
    },
}


def main() -> None:
    """Run module."""
    module = incus_create_write_module({
        **INCUS_COMMON_ARGUMENT_SPEC,
        'project': {'type': 'str', 'default': 'default'},
        'target': {'type': 'str'},
        'type': {
            'type': 'str',
            'choices': [
                'bridge',
                'macvlan',
                'ovn',
                'physical',
                'sriov',
            ],
        },
        'config': {
            'type': 'dict',
            'default': {},
            'options': INCUS_NETWORK_CONFIG_OPTIONS,
        },
        'description': {'type': 'str', 'default': ''},
    })
    config = module.params['config'] or {}
    bgp_peers = config.get('bgp_peers')
    tunnels = config.get('tunnels')
    plain_config = {key: value for key, value in config.items() if key not in ('bgp_peers', 'tunnels')}
    desired: dict[str, Any] = {
        'description': module.params['description'],
        'config': incus_common_stringify_dict(plain_config),
    }
    if bgp_peers:
        desired['config'].update(
            incus_common_flatten_to_config('bgp.peers', incus_common_named_list_to_dict(bgp_peers)),
        )
    if tunnels:
        desired['config'].update(
            incus_common_flatten_to_config('tunnel', incus_common_named_list_to_dict(tunnels)),
        )
    incus_run_write_module(module, lambda: incus_ensure_resource(module, 'networks', desired, ['type']))


if __name__ == '__main__':
    main()
